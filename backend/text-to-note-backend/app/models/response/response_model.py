from pydantic import BaseModel
from typing import Any, Optional

class SNResponse(BaseModel):
    """Standardized response model for Speaker Command API"""
    data: Any = None
    status_code: int
    message: str
    
    class Config:
        # Allow arbitrary types for the data field
        arbitrary_types_allowed = True
        
    @classmethod
    def success(cls, data: Any = None, message: str = "Success", status_code: int = 200):
        """Create a successful response"""
        return cls(data=data, status_code=status_code, message=message)
    
    @classmethod
    def error(cls, message: str, status_code: int = 400, data: Any = None):
        """Create an error response"""
        return cls(data=data, status_code=status_code, message=message)
