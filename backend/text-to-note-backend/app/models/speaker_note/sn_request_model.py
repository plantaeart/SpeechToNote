from pydantic import BaseModel
from typing import Any, List

class SNRequest(BaseModel):
    """Standardized request model for SpeechToNote API"""
    data: List[Any]
    
    class Config:
        # Allow arbitrary types for the data field
        arbitrary_types_allowed = True
        
        # Example schema for documentation
        schema_extra = {
            "example": {
                "data": [
                    {"title": "Meeting Notes", "content": "Important discussion points..."},
                    {"title": "Action Items", "content": "Follow up tasks..."}
                ]
            }
        }
