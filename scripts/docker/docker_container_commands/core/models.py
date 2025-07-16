from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class ContainerInfo(BaseModel):
    """Container information model"""
    id: str = Field(..., description="Container ID")
    name: str = Field(..., description="Container name")
    image: str = Field(..., description="Image used by container")
    status: str = Field(..., description="Container status")
    ports: Optional[str] = Field(None, description="Port mappings")
    
    @property
    def is_running(self) -> bool:
        """Check if container is running"""
        return 'Up' in self.status
    
    @property
    def is_stopped(self) -> bool:
        """Check if container is stopped"""
        return 'Exited' in self.status or 'Created' in self.status
    
    @property
    def short_id(self) -> str:
        """Get short container ID"""
        return self.id[:12]
    
    @property
    def status_icon(self) -> str:
        """Get status icon"""
        if self.is_running:
            return "🟢"
        elif self.is_stopped:
            return "🔴"
        else:
            return "⚪"

class ContainerRegistry:
    """Registry for managing container operations"""
    
    def __init__(self):
        self.supported_operations = {
            "start": "Start stopped containers",
            "stop": "Stop running containers", 
            "restart": "Restart containers",
            "delete": "Delete containers",
            "logs": "View container logs"
        }
    
    def get_operation_description(self, operation: str) -> str:
        """Get description for an operation"""
        return self.supported_operations.get(operation, "Unknown operation")
    
    def list_operations(self) -> List[str]:
        """Get list of supported operations"""
        return list(self.supported_operations.keys())

# Global registry instance
container_registry = ContainerRegistry()
