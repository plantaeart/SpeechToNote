from .base import BaseConfig

class ExampleConfig(BaseConfig):
    """Example environment configuration"""
    MONGO_URI: str = "your-mongo-uri"
    DATABASE_NAME: str = "your-database-name"
    ENVIRONMENT: str = "your-environment"
    DEBUG: bool = False
