from datetime import datetime
from typing import Dict, Any

class SpeakerCommandMigrations:
    """Handle speaker command schema migrations"""
    
    @staticmethod
    def get_current_schema_version() -> str:
        """Return current schema version"""
        return "1.0.1"  # Updated to include HTML tags and vocal command list
    
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
    def migrate_to_v1_0_1(collection, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate document to version 1.0.1 - Add HTML tags and convert command_vocal to list"""
        update_fields = {}
        
        # Convert command_vocal from string to list if it's still a string
        if "command_vocal" in doc and isinstance(doc["command_vocal"], str):
            update_fields["command_vocal"] = [doc["command_vocal"]]
        elif "command_vocal" not in doc:
            # If missing, set empty list (will be validated by API)
            update_fields["command_vocal"] = []
        
        # Add HTML tag fields if missing - initialize as empty strings
        if "html_tag_start" not in doc:
            update_fields["html_tag_start"] = ""
        
        if "html_tag_end" not in doc:
            update_fields["html_tag_end"] = ""
        
        # Update schema version
        update_fields["schema_version"] = "1.0.1"
        update_fields["updated_at"] = datetime.now()
        
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
                update_fields = {}
                
                # Apply migrations step by step
                if doc_version < "1.0.0":
                    v1_0_0_fields = SpeakerCommandMigrations.migrate_to_v1_0_0(collection, doc)
                    update_fields.update(v1_0_0_fields)
                    # Update doc with v1.0.0 fields for next migration
                    doc.update(v1_0_0_fields)
                
                if doc_version < "1.0.1":
                    v1_0_1_fields = SpeakerCommandMigrations.migrate_to_v1_0_1(collection, doc)
                    update_fields.update(v1_0_1_fields)
                
                if update_fields:
                    collection.update_one(
                        {"_id": doc["_id"]},
                        {"$set": update_fields}
                    )
                    updated_count += 1
                    print(f"Migrated document {doc.get('command_name', 'unknown')} to {current_version}")
            
            if updated_count > 0:
                print(f"Successfully migrated {updated_count} speaker commands to version {current_version}")
            else:
                print(f"All speaker commands are already at version {current_version}")
                
        except Exception as e:
            print(f"Speaker command migration error: {e}")
            raise