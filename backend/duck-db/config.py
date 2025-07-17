import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB Docker container settings
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'speechtonote_local')
    
    # DuckDB settings
    DUCKDB_PATH = os.getenv('DUCKDB_PATH', ':memory:')  # Use :memory: for in-memory DB
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Default connection settings for MongoDB Docker
DEFAULT_CONFIG = {
    'mongo_uri': Config.MONGO_URI,
    'db_name': Config.MONGO_DB_NAME
}

COLLECTIONS = {
    "SPEAKER_NOTES": "SPEAKER_NOTES",
    "COMMANDS": "COMMANDS",
}
