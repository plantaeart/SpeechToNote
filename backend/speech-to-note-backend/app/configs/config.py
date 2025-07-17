import os
from .local import LocalConfig
from .docker import DockerConfig
from .kubernetes import KubernetesConfig
from .base import BaseConfig

def get_config():
    """Factory function to return the appropriate configuration"""
    current_env = os.getenv("CURRENT_ENV", "local").lower()
    
    config_map = {
        "local": LocalConfig,
        "docker": DockerConfig,
        "kubernetes": KubernetesConfig
    }
    
    config_class = config_map.get(current_env, LocalConfig)
    return config_class()

# Global config instance
config: BaseConfig = get_config()
