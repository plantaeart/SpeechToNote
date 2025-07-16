from typing import Dict, List
from pydantic import BaseModel, Field

class ServiceConfig(BaseModel):
    """Service configuration model"""
    name: str = Field(..., description="Human-readable service name")
    image_name: str = Field(..., description="Docker image name")
    dockerfile_path: str = Field(..., description="Path to Dockerfile relative to project root")
    context_path: str = Field(..., description="Build context path relative to project root")
    default_port: int = Field(..., description="Default host port")
    container_port: int = Field(..., description="Container internal port")
    build_args: Dict[str, str] = Field(default_factory=dict, description="Docker build arguments")

    def get_full_image_name(self, tag: str) -> str:
        """Get full image name with tag"""
        return f"{self.image_name}:{tag}"

    def get_default_container_name(self, tag: str) -> str:
        """Get default container name"""
        return f"{self.image_name}-{tag}"

class ServicesRegistry:
    """Registry for managing service configurations"""
    
    def __init__(self):
        self._services = {
            "backend": ServiceConfig(
                name="FastAPI Backend",
                image_name="speechtonote-backend",
                dockerfile_path="backend\\speech-to-note-backend\\Dockerfile",
                context_path="backend\\speech-to-note-backend",
                default_port=8000,
                container_port=8000,
                build_args={}
            ),
            "frontend": ServiceConfig(
                name="Vue.js Frontend",
                image_name="speechtonote-frontend",
                dockerfile_path="frontend\\Dockerfile",
                context_path="frontend",
                default_port=3000,
                container_port=80,
                build_args={"VITE_CONFIG_ENV_FRONT": "local_docker"}
            )
        }
    
    def get(self, service_name: str) -> ServiceConfig:
        """Get service configuration by name"""
        if service_name not in self._services:
            raise ValueError(f"Unknown service: {service_name}")
        return self._services[service_name]
    
    def exists(self, service_name: str) -> bool:
        """Check if service exists"""
        return service_name in self._services
    
    def list_services(self) -> List[str]:
        """Get list of available service names"""
        return list(self._services.keys())
    
    def items(self):
        """Iterate over service items"""
        return self._services.items()

# Global registry instance
services_registry = ServicesRegistry()
