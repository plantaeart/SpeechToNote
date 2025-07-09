from contextlib import asynccontextmanager
from fastapi import FastAPI
from pymongo import MongoClient
from datetime import datetime, timezone
import sys

# Import configuration first and display it prominently
print("\n" + "="*60, flush=True)
print("[STARTUP] 🚀 SpeechToNote API Initialization", flush=True)
print("="*60, flush=True)

# Import smart configuration
from .config import MONGO_URI, DATABASE_NAME, COLLECTIONS
from .migrations.speaker_note_migrations import SpeakerNoteMigrations
from .migrations.speaker_command_migrations import SpeakerCommandMigrations

print(f"[STARTUP] 📊 MongoDB URI: {MONGO_URI}", flush=True)
print(f"[STARTUP] 📊 Database: {DATABASE_NAME}", flush=True)
print(f"[STARTUP] 📊 Collections: {COLLECTIONS}", flush=True)
print("="*60 + "\n", flush=True)

# Global variables to store db connection
mongodb_client = None
database = None
collections = {}

@asynccontextmanager
async def app_lifespan(app):
    global mongodb_client, database, collections
    try:
        print("[STARTUP] 🔗 Connecting to MongoDB...", flush=True)
        mongodb_client = MongoClient(MONGO_URI)
        
        # Test the connection
        print("[STARTUP] 🧪 Testing MongoDB connection...", flush=True)
        mongodb_client.admin.command('ping')
        print("[STARTUP] ✅ MongoDB connection successful", flush=True)
        
        # Check if database exists, if not it will be created when we access it
        database = mongodb_client[DATABASE_NAME]
        
        # Check if collections exist, create them if they don't
        existing_collections = database.list_collection_names()
        for collection_name in COLLECTIONS:
            if collection_name not in existing_collections:
                database.create_collection(collection_name)
                print(f"Created collection: {collection_name}")
            else:
                print(f"Collection {collection_name} already exists")
            
            collections[collection_name] = database[collection_name]
        
        print(f"[STARTUP] 🗄️ Connected to database: {DATABASE_NAME}", flush=True)
        
        # Run migrations for speaker notes
        if "SPEAKER_NOTES" in collections:
            print("[STARTUP] 🔄 Running speaker notes migrations...", flush=True)
            SpeakerNoteMigrations.run_migrations(collections["SPEAKER_NOTES"])

        # Run migrations for commands
        if "COMMANDS" in collections:
            print("[STARTUP] 🔄 Running commands migrations...", flush=True)
            SpeakerCommandMigrations.run_migrations(collections["COMMANDS"])

        print("[STARTUP] ✅ All systems ready!", flush=True)

    except Exception as e:
        print(f"[STARTUP] ❌ MongoDB connection failed: {e}", flush=True)
        raise
    
    yield
    
    try:
        if mongodb_client:
            mongodb_client.close()
            print("[SHUTDOWN] 🔌 MongoDB connection closed", flush=True)
    except Exception as e:
        print(f"[SHUTDOWN] ⚠️ Error closing MongoDB connection: {e}", flush=True)

# Initialize FastAPI with lifespan
app = FastAPI(lifespan=app_lifespan)

# Function to get database connection
def get_database():
    return database

def get_collection(collection_name: str = "SPEAKER_NOTES"):
    return collections.get(collection_name)

def get_all_collections():
    return collections

# Register routes after defining helper functions
from .routes.speaker_note_route import router_speaker_note 
from .routes.speaker_command_route import router_speaker_command
app.include_router(router_speaker_note)
app.include_router(router_speaker_command)

__all__ = ["app", "get_database", "get_collection", "get_all_collections"]