from .base import BaseConfig


class KubernetesConfig(BaseConfig):
    """Configuration for the backend running in the local kind cluster.

    MongoDB is reached through the in-cluster Service created by
    ``manifests/mongo-service.yaml``.
    """

    ENVIRONMENT: str = "kubernetes"
    MONGO_URI: str = "mongodb://mongo:27017"
    DATABASE_NAME: str = "speechtonote"
    DEBUG: bool = False
