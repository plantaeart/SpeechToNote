from pydantic_settings import BaseSettings
from typing import Optional

class BaseConfig(BaseSettings):
    """Base configuration class"""
    MONGO_URI: str
    DATABASE_NAME: str
    ENVIRONMENT: str
    COLLECTIONS: list[str] = ["SPEAKER_NOTES", "COMMANDS"]
    CURRENT_APPLICATION_VERSION: str = "2.1.0"
    CURRENT_SC_SCHEMA_VERSION: str = "1.0.1"
    CURRENT_SN_SCHEMA_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
