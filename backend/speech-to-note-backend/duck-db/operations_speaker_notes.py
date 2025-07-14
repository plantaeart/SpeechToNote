from connection import DuckDBMongoDB
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime, timedelta
import logging
from config import Config, COLLECTIONS
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseSpeakerNotesOperations:
    def __init__(self, connection: DuckDBMongoDB):
        self.connection = connection

    # Method to search speaker notes using DuckDB's text search capabilities
    # It allows searching by content or title, with a limit on the number of results
    def search_speaker_notes(self, search_term: str, collection: str = COLLECTIONS["SPEAKER_NOTES"], limit: int = 50) -> List[Dict]:
        """Search speaker_notes using DuckDB's text search capabilities"""
        try:
            self.connection.sync_mongo_to_duckdb(collection)
            check_query = f"SELECT COUNT(*) as count FROM {collection}"
            count_result = self.connection.query_duckdb(check_query)
            if not count_result or count_result[0]['count'] == 0:
                logger.info(f"No data found in {collection}")
                return []

            escaped_term = search_term.replace("'", "''")
            query = f"""
            SELECT id_note, title, content, commands, schema_version, created_at, updated_at
            FROM {collection}
            WHERE (content IS NOT NULL AND LOWER(content) LIKE LOWER('%{escaped_term}%'))
            OR (title IS NOT NULL AND LOWER(title) LIKE LOWER('%{escaped_term}%'))
            ORDER BY created_at DESC
            LIMIT {limit}
            """
            results = self.connection.query_duckdb(query)
            # Convert commands from JSON string to list if needed
            for note in results:
                if isinstance(note.get("commands"), str):
                    try:
                        import json
                        note["commands"] = json.loads(note["commands"])
                    except Exception:
                        note["commands"] = []
                # Convert created_at/updated_at to datetime if string
                for dt_field in ("created_at", "updated_at"):
                    if note.get(dt_field) and isinstance(note[dt_field], str):
                        try:
                            note[dt_field] = datetime.fromisoformat(note[dt_field])
                        except Exception:
                            pass
            return results
        except Exception as e:
            logger.error(f"Search failed for term '{search_term}': {e}")
            return []

    # Get speaker notes by date range using DuckDB
    # If no dates are provided, it returns all notes ordered by creation date
    def get_speaker_notes_by_date_range(self, start_date: Optional[str] = None, end_date: Optional[str] = None, collection: str = COLLECTIONS["SPEAKER_NOTES"]) -> List[Dict]:
        """Get speaker_notes within a date range using DuckDB. If no dates, return all notes."""
        try:
            self.connection.sync_mongo_to_duckdb(collection)
            check_query = f"SELECT COUNT(*) as count FROM {collection}"
            count_result = self.connection.query_duckdb(check_query)
            if not count_result or count_result[0]['count'] == 0:
                logger.info(f"No data found in {collection}")
                return []

            if start_date and end_date:
                query = f"""
                SELECT id_note, title, content, commands, schema_version, created_at, updated_at
                FROM {collection}
                WHERE created_at IS NOT NULL 
                AND created_at BETWEEN '{start_date}' AND '{end_date}'
                ORDER BY created_at DESC
                """
            else:
                query = f"""
                SELECT id_note, title, content, commands, schema_version, created_at, updated_at
                FROM {collection}
                ORDER BY created_at DESC
                """

            results = self.connection.query_duckdb(query)
            for note in results:
                if isinstance(note.get("commands"), str):
                    try:
                        import json
                        note["commands"] = json.loads(note["commands"])
                    except Exception:
                        note["commands"] = []
                for dt_field in ("created_at", "updated_at"):
                    if note.get(dt_field) and isinstance(note[dt_field], str):
                        try:
                            note[dt_field] = datetime.fromisoformat(note[dt_field])
                        except Exception:
                            pass
            return results
        except Exception as e:
            logger.error(f"Date range query failed: {e}")
            return []

    # Get comprehensive analytics on speaker_notes using DuckDB aggregation
    # It provides total count, notes by date, average content length, and most active hours
    def get_speaker_notes_analytics(self, collection: str = COLLECTIONS["SPEAKER_NOTES"], days: int = 30) -> Dict[str, Any]:
        """Get comprehensive analytics on speaker_notes using DuckDB aggregation"""
        try:
            self.connection.sync_mongo_to_duckdb(collection)
            analytics = {}
            check_query = f"SELECT COUNT(*) as count FROM {collection}"
            count_result = self.connection.query_duckdb(check_query)
            if not count_result or count_result[0]['count'] == 0:
                logger.info(f"No data found in {collection}")
                return {
                    'total_speaker_notes': 0,
                    'speaker_notes_by_date': [],
                    'avg_content_length': 0,
                    'most_active_hours': []
                }
            analytics['total_speaker_notes'] = count_result[0]['count']
            try:
                result = self.connection.query_duckdb(f"""
                    SELECT DATE(created_at) as date, COUNT(*) as count 
                    FROM {collection} 
                    WHERE created_at IS NOT NULL 
                    AND created_at >= CURRENT_DATE - INTERVAL '{days}' DAY
                    GROUP BY DATE(created_at) 
                    ORDER BY date DESC
                """)
                analytics['speaker_notes_by_date'] = result
            except Exception as e:
                logger.warning(f"Date analysis failed: {e}")
                analytics['speaker_notes_by_date'] = []
            try:
                result = self.connection.query_duckdb(f"""
                    SELECT AVG(LENGTH(content)) as avg_length 
                    FROM {collection}
                    WHERE content IS NOT NULL AND content != ''
                """)
                analytics['avg_content_length'] = result[0]['avg_length'] if result and result[0]['avg_length'] else 0
            except Exception as e:
                logger.warning(f"Content length analysis failed: {e}")
                analytics['avg_content_length'] = 0
            try:
                result = self.connection.query_duckdb(f"""
                    SELECT EXTRACT('hour' FROM created_at) as hour, COUNT(*) as count
                    FROM {collection}
                    WHERE created_at IS NOT NULL
                    GROUP BY EXTRACT('hour' FROM created_at)
                    ORDER BY count DESC
                    LIMIT 5
                """)
                analytics['most_active_hours'] = result
            except Exception as e:
                logger.warning(f"Active hours analysis failed: {e}")
                analytics['most_active_hours'] = []
            return analytics
        except Exception as e:
            logger.error(f"Analytics query failed: {e}")
            return {}

    # Get most recent speaker notes
    # It retrieves the latest notes ordered by creation date, with a limit on the number of
    def get_recent_speaker_notes(self, limit: int = 10, collection: str = COLLECTIONS["SPEAKER_NOTES"]) -> List[Dict]:
        """Get most recent speaker_notes"""
        try:
            self.connection.sync_mongo_to_duckdb(collection)
            check_query = f"SELECT COUNT(*) as count FROM {collection}"
            count_result = self.connection.query_duckdb(check_query)
            if not count_result or count_result[0]['count'] == 0:
                logger.info(f"No data found in {collection}")
                return []
            query = f"""
            SELECT id_note, title, content, commands, schema_version, created_at, updated_at
            FROM {collection}
            WHERE created_at IS NOT NULL
            ORDER BY created_at DESC
            LIMIT {limit}
            """
            results = self.connection.query_duckdb(query)
            for note in results:
                if isinstance(note.get("commands"), str):
                    try:
                        import json
                        note["commands"] = json.loads(note["commands"])
                    except Exception:
                        note["commands"] = []
                for dt_field in ("created_at", "updated_at"):
                    if note.get(dt_field) and isinstance(note[dt_field], str):
                        try:
                            note[dt_field] = datetime.fromisoformat(note[dt_field])
                        except Exception:
                            pass
            return results
        except Exception as e:
            logger.error(f"Recent speaker_notes query failed: {e}")
            return []

    # Export collection to pandas DataFrame for analysis
    # It retrieves all notes and converts them to a DataFrame, handling commands and date fields
    def export_to_dataframe(self, collection: str = COLLECTIONS["SPEAKER_NOTES"]) -> Optional[pd.DataFrame]:
        """Export collection to pandas DataFrame for analysis"""
        try:
            if self.connection.duck_conn is None:
                raise Exception("DuckDB connection not established. Call connect() first.")
            self.connection.sync_mongo_to_duckdb(collection)
            check_query = f"SELECT COUNT(*) as count FROM {collection}"
            count_result = self.connection.query_duckdb(check_query)
            if not count_result or count_result[0]['count'] == 0:
                logger.info(f"No data found in {collection}")
                return pd.DataFrame()
            df = self.connection.duck_conn.execute(
                f"SELECT id_note, title, content, commands, schema_version, created_at, updated_at FROM {collection}"
            ).df()
            # Convert commands from JSON string to list if needed
            if "commands" in df.columns:
                import json
                df["commands"] = df["commands"].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
            # Convert created_at/updated_at to datetime if string
            for dt_field in ("created_at", "updated_at"):
                if dt_field in df.columns:
                    df[dt_field] = pd.to_datetime(df[dt_field], errors="coerce")
            return df
        except Exception as e:
            logger.error(f"DataFrame export failed: {e}")
            return None

    # Get word frequency analysis from note contents
    # It retrieves the most common words in the notes, excluding short words and empty strings
    def get_word_frequency(self, collection: str = COLLECTIONS["SPEAKER_NOTES"], top_n: int = 20) -> List[Dict]:
        """Get word frequency analysis from note contents"""
        try:
            self.connection.sync_mongo_to_duckdb(collection)
            check_query = f"SELECT COUNT(*) as count FROM {collection} WHERE content IS NOT NULL AND content != ''"
            count_result = self.connection.query_duckdb(check_query)
            if not count_result or count_result[0]['count'] == 0:
                logger.info(f"No content data found in {collection}")
                return []
            query = f"""
            WITH words AS (
                SELECT UNNEST(string_split_regex(LOWER(content), '[^a-zA-Z]+')) as word
                FROM {collection}
                WHERE content IS NOT NULL AND content != ''
            )
            SELECT word, COUNT(*) as frequency
            FROM words
            WHERE LENGTH(word) > 2 AND word != ''
            GROUP BY word
            ORDER BY frequency DESC
            LIMIT {top_n}
            """
            return self.connection.query_duckdb(query)
        except Exception as e:
            logger.error(f"Word frequency analysis failed: {e}")
            return []
