from .base import BaseConfig


class DockerConfig(BaseConfig):
    """Configuration for the backend running inside a container.

    Under Docker Compose the database is reached by its service name; see
    infra/docker-compose.yml.
    """

    ENVIRONMENT: str = "docker"
    MONGO_URI: str = "mongodb://mongo:27017"
    DATABASE_NAME: str = "speechtonote"
    DEBUG: bool = False