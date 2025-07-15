from pydantic import BaseModel
from typing import List
from .speaker_note_model import SpeakerNoteCreate, SpeakerNoteUpdate

class SNCreateRequest(BaseModel):
    """Request model for creating speaker notes"""
    data: List[SpeakerNoteCreate]
    
    class Config:
        # Example schema for documentation
        json_schema_extra = {
            "example": {
                "data": [
                    {"title": "Meeting Notes", "content": "Important discussion points...", "commands": ["save"]},
                    {"title": "Action Items", "content": "Follow up tasks...", "commands": ["export"]}
                ]
            }
        }

class SNUpdateRequest(BaseModel):
    """Request model for updating speaker notes"""
    data: List[SpeakerNoteUpdate]
    
    class Config:
        # Example schema for documentation
        json_schema_extra = {
            "example": {
                "data": [
                    {"id_note": 1, "title": "Updated Meeting Notes"},
                    {"id_note": 2, "content": "Updated content only"}
                ]
            }
        }

class SNDeleteByIdsRequest(BaseModel):
    """Request model for deleting speaker notes by IDs"""
    ids_note: List[int]
    
    class Config:
        # Example schema for documentation
        json_schema_extra = {
            "example": {
                "ids_note": [1, 2, 3, 4]
            }
        }

# Keep the original for backward compatibility if needed
SNRequest = SNCreateRequest
