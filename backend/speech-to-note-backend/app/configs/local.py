from .base import BaseConfig


class LocalConfig(BaseConfig):
    """Configuration for running FastAPI directly on your machine."""

    ENVIRONMENT: str = "local"
    MONGO_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "speechtonote"
    DEBUG: bool = True
