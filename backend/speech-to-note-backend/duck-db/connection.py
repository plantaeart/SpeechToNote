import duckdb
import pymongo
from typing import Optional, Dict, Any, List
import json
import logging
from config import Config

logger = logging.getLogger(__name__)

class DuckDBMongoDB:
    def __init__(self, mongo_uri: str = Config.MONGO_URI, db_name: str = Config.MONGO_DB_NAME):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.mongo_client = None
        self.mongo_db = None
        self.duck_conn = None
        
    def connect(self):
        """Establish connections to both MongoDB Docker container and DuckDB"""
        try:
            # Connect to MongoDB Docker container
            self.mongo_client = pymongo.MongoClient(
                self.mongo_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            # Test connection
            self.mongo_client.admin.command('ping')
            self.mongo_db = self.mongo_client[self.db_name]
            
            # Create DuckDB connection (in-memory for fast analytics)
            self.duck_conn = duckdb.connect(':memory:')
            
            logger.info("Successfully connected to MongoDB Docker and DuckDB")
            return self
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            raise
    
    def sync_mongo_to_duckdb(self, collection_name: str, table_name: Optional[str] = None):
        """Sync MongoDB collection to DuckDB table for analytics"""
        if not table_name:
            table_name = collection_name
            
        try:
            if self.mongo_db is None:
                raise Exception("MongoDB connection not established. Call connect() first.")
            if self.duck_conn is None:
                raise Exception("DuckDB connection not established. Call connect() first.")

            print(f"🔄 Syncing MongoDB collection '{collection_name}' to DuckDB table '{table_name}'...")
            collection = self.mongo_db[collection_name]
            documents = list(collection.find())
            
            if documents:
                import pandas as pd
                processed_docs = []
                for doc in documents:
                    if '_id' in doc:
                        doc['_id'] = str(doc['_id'])
                    for key, value in doc.items():
                        if isinstance(value, (dict, list)):
                            doc[key] = json.dumps(value)
                        elif value is None:
                            doc[key] = ""
                    processed_docs.append(doc)
                df = pd.DataFrame(processed_docs)
                # Register the DataFrame as a DuckDB view, then create the table from it
                self.duck_conn.execute(f"DROP TABLE IF EXISTS {table_name}")
                self.duck_conn.register('tmp_mongo_df', df)
                self.duck_conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM tmp_mongo_df")
                self.duck_conn.unregister('tmp_mongo_df')
                logger.info(f"Synced {len(processed_docs)} documents from {collection_name} to DuckDB")
            else:
                self.duck_conn.execute(f"DROP TABLE IF EXISTS {table_name}")
                self.duck_conn.execute(f"CREATE TABLE {table_name} (placeholder VARCHAR)")
                logger.info(f"Created empty table {table_name} - no documents found in {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to sync {collection_name}: {e}")
            raise

    def query_duckdb(self, query: str) -> List[Dict]:
        """Execute query on DuckDB and return results"""
        try:
            if self.duck_conn is None:
                raise Exception("DuckDB connection not established. Call connect() first.")
            
            cursor = self.duck_conn.execute(query)
            result = cursor.fetchall()
            
            if result and len(result) > 0:
                # Get column names from cursor description
                description = cursor.description
                if description is not None:
                    columns = [desc[0] for desc in description]
                    return [dict(zip(columns, row)) for row in result]
            return []
        except Exception as e:
            logger.error(f"DuckDB query failed: {e}")
            raise

    def get_mongo_collection(self, collection_name: str):
        """Get MongoDB collection reference"""
        if self.mongo_db is None:
            raise Exception("MongoDB connection not established. Call connect() first.")
        return self.mongo_db[collection_name]
    
    def close(self):
        """Close all connections"""
        if self.mongo_client:
            self.mongo_client.close()
        if self.duck_conn:
            self.duck_conn.close()
        logger.info("Closed all database connections")
