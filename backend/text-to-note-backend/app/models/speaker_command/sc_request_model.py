from pydantic import BaseModel
from typing import List
from .speaker_command_model import SpeakerCommandCreate, SpeakerCommandUpdate

class SCCreateRequest(BaseModel):
    """Request model for creating speaker commands"""
    data: List[SpeakerCommandCreate]
    
    class Config:
        # Example schema for documentation
        schema_extra = {
            "example": {
                "data": [
                    {"command_name": "save_note", "command_vocal": "sauvegarder la note", "command_description": "Sauvegarde la note en cours"},
                    {"command_name": "export_pdf", "command_vocal": "exporter en PDF"}
                ]
            }
        }

class SCUpdateRequest(BaseModel):
    """Request model for updating speaker commands"""
    data: List[SpeakerCommandUpdate]
    
    class Config:
        # Example schema for documentation
        schema_extra = {
            "example": {
                "data": [
                    {"id_command": 1, "command_name": "updated_save"},
                    {"id_command": 2, "command_description": "Updated description only"}
                ]
            }
        }

class SCDeleteByIdsRequest(BaseModel):
    """Request model for deleting speaker commands by IDs"""
    ids_command: List[int]
    
    class Config:
        # Example schema for documentation
        schema_extra = {
            "example": {
                "ids_command": [1, 2, 3, 4]
            }
        }
# Keep the original for backward compatibility if needed
SCRequest = SCCreateRequest
