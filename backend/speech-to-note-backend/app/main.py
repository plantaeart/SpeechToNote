from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import uvicorn

from .routes.speaker_note_route import router_speaker_note 
from .routes.speaker_command_route import router_speaker_command
from .configs.config import config
from .migrations.speaker_note_migrations import SpeakerNoteMigrations
from .migrations.speaker_command_migrations import SpeakerCommandMigrations
from .config_cors import CORS_CONFIG

# Display configuration before starting
print("\n" + "🚀 " + "="*50, flush=True)
print("  SpeechToNote FastAPI Server Starting...", flush=True)
print("="*54, flush=True)

print("\n" + "="*60, flush=True)
print("[STARTUP] 🚀 SpeechToNote API Initialization", flush=True)
print("="*60, flush=True)

print(f"[STARTUP] 📦 Environment: {config.ENVIRONMENT}", flush=True)
print(f"[STARTUP] 📊 MongoDB URI: {config.MONGO_URI}", flush=True)
print(f"[STARTUP] 📊 Database: {config.DATABASE_NAME}", flush=True)
print(f"[STARTUP] 📊 Collections: {config.COLLECTIONS}", flush=True)
print("="*60 + "\n", flush=True)

mongodb_client = None
database = None
collections = {}

@asynccontextmanager
async def app_lifespan(app):
    global mongodb_client, database, collections
    try:
        print("[STARTUP] 🔗 Connecting to MongoDB...", flush=True)
        mongodb_client = MongoClient(config.MONGO_URI)
        print("[STARTUP] 🧪 Testing MongoDB connection...", flush=True)
        mongodb_client.admin.command('ping')
        print("[STARTUP] ✅ MongoDB connection successful", flush=True)
        database = mongodb_client[config.DATABASE_NAME]
        existing_collections = database.list_collection_names()
        for collection_name in config.COLLECTIONS:
            if collection_name not in existing_collections:
                database.create_collection(collection_name)
                print(f"Created collection: {collection_name}")
            else:
                print(f"Collection {collection_name} already exists")
            collections[collection_name] = database[collection_name]
        print(f"[STARTUP] 🗄️ Connected to database: {config.DATABASE_NAME}", flush=True)
        if "SPEAKER_NOTES" in collections:
            print("[STARTUP] 🔄 Running speaker notes migrations...", flush=True)
            SpeakerNoteMigrations.run_migrations(collections["SPEAKER_NOTES"])
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

app = FastAPI(
    title="SpeechToNote API",
    description="API for managing speaker notes and commands",
    version=config.CURRENT_APPLICATION_VERSION,
    lifespan=app_lifespan
)

app.add_middleware(
    CORSMiddleware,
    **CORS_CONFIG
)

print(f"[CORS] Allowed origins: {CORS_CONFIG['allow_origins']}")

def get_database():
    return database

def get_collection(collection_name: str = "SPEAKER_NOTES"):
    return collections.get(collection_name)

def get_all_collections():
    return collections

app.include_router(router_speaker_note)
app.include_router(router_speaker_command)

__all__ = ["app", "get_database", "get_collection", "get_all_collections"]

if __name__ == "__main__":
    print("\n[MAIN] 🌐 Starting uvicorn server...", flush=True)
    print("[MAIN] 📍 URL: http://127.0.0.1:8000", flush=True)
    print("[MAIN] 📖 Docs: http://127.0.0.1:8000/docs", flush=True)
    print("="*54 + "\n", flush=True)
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
