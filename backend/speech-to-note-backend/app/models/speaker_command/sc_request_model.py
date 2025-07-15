from pydantic import BaseModel
from typing import List
from .speaker_command_model import SpeakerCommandCreate, SpeakerCommandUpdate

class SCCreateRequest(BaseModel):
    """Request model for creating speaker commands"""
    data: List[SpeakerCommandCreate]
    
    class Config:
        # Example schema for documentation
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "command_name": "titre",
                        "command_vocal": ["titre", "titres"],
                        "command_description": "Formate le texte comme un titre principal",
                        "html_tag_start": "<h1>",
                        "html_tag_end": "</h1>"
                    },
                    {
                        "command_name": "sous_titre",
                        "command_vocal": ["sous-titre", "sous titre", "sous titres"],
                        "command_description": "Formate le texte comme un sous-titre",
                        "html_tag_start": "<h2>",
                        "html_tag_end": "</h2>"
                    },
                    {
                        "command_name": "saut_ligne",
                        "command_vocal": ["saut de ligne", "nouvelle ligne"],
                        "command_description": "Insère un saut de ligne",
                        "html_tag_start": "<br>",
                        "html_tag_end": ""
                    }
                ]
            }
        }

class SCUpdateRequest(BaseModel):
    """Request model for updating speaker commands"""
    data: List[SpeakerCommandUpdate]
    
    class Config:
        # Example schema for documentation
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "id_command": 1,
                        "command_name": "titre_principal",
                        "command_vocal": ["titre", "titres", "titre principal"],
                        "html_tag_start": "<h1 class='main-title'>",
                        "html_tag_end": "</h1>"
                    },
                    {
                        "id_command": 2,
                        "command_description": "Description mise à jour seulement"
                    }
                ]
            }
        }

class SCDeleteByIdsRequest(BaseModel):
    """Request model for deleting speaker commands by IDs"""
    ids_command: List[int]
    
    class Config:
        # Example schema for documentation
        json_schema_extra = {
            "example": {
                "ids_command": [1, 2, 3, 4]
            }
        }
# Keep the original for backward compatibility if needed
SCRequest = SCCreateRequest
