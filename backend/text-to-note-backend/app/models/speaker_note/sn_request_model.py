from pydantic import BaseModel
from typing import List
from .speaker_note_model import SpeakerNote, SpeakerNoteUpdate

class SNRequest(BaseModel):
    """Standardized request model for SpeechToNote API"""
    data: List[SpeakerNote | SpeakerNoteUpdate]
    
    class Config:
        # Example schema for documentation
        schema_extra = {
            "example": {
                "data": [
                    {"title": "Meeting Notes", "content": "Important discussion points...", "commands": ["save"]},
                    {"title": "Action Items", "content": "Follow up tasks...", "commands": ["export"]}
                ]
            }
        }
