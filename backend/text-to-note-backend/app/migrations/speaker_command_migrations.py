from datetime import datetime
from typing import Dict, Any

class SpeakerCommandMigrations:
    """Handle speaker command schema migrations"""
    
    @staticmethod
    def get_current_schema_version() -> str:
        """Return current schema version"""
        return "1.0.0"  # Update this when you change the model
    
    @staticmethod
    def migrate_to_v1_0_0(collection, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate document to version 1.0.0"""
        update_fields = {}
        
        # Add missing fields
        if "command_description" not in doc:
            update_fields["command_description"] = None
        
        if "created_at" not in doc:
            update_fields["created_at"] = datetime.now()
        
        if "updated_at" not in doc:
            update_fields["updated_at"] = datetime.now()
        
        # Add schema version
        update_fields["schema_version"] = "1.0.0"
        
        return update_fields
    
    @staticmethod
    def run_migrations(collection):
        """Run all necessary migrations"""
        try:
            current_version = SpeakerCommandMigrations.get_current_schema_version()
            
            # Find documents that need migration
            documents_to_migrate = list(collection.find({
                "$or": [
                    {"schema_version": {"$exists": False}},
                    {"schema_version": {"$ne": current_version}}
                ]
            }))
            
            updated_count = 0
            
            for doc in documents_to_migrate:
                doc_version = doc.get("schema_version", "0.0.0")
                
                # Apply migrations based on current version
                if doc_version != current_version:
                    update_fields = SpeakerCommandMigrations.migrate_to_v1_0_0(collection, doc)
                    
                    if update_fields:
                        collection.update_one(
                            {"_id": doc["_id"]},
                            {"$set": update_fields}
                        )
                        updated_count += 1
            
            if updated_count > 0:
                print(f"Successfully migrated {updated_count} speaker commands to version {current_version}")
            else:
                print(f"All speaker commands are already at version {current_version}")
                
        except Exception as e:
            print(f"Speaker command migration error: {e}")
            raise
