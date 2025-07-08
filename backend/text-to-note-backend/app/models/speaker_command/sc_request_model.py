from pydantic import BaseModel
from typing import List
from .speaker_command_model import SpeakerCommand, SpeakerCommandUpdate

class SCRequest(BaseModel):
    """Standardized request model for Speaker Command API"""
    data: List[SpeakerCommand | SpeakerCommandUpdate]
    
    class Config:
        # Example schema for documentation
        schema_extra = {
            "example": {
                "data": [
                    {"command_name": "save_note", "command_vocal": "sauvegarder la note", "command_description": "Sauvegarde la note en cours"},
                    {"command_name": "export_pdf", "command_vocal": "exporter en PDF", "command_description": "Exporte la note au format PDF"}
                ]
            }
        }
