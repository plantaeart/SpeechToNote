from fastapi import APIRouter, HTTPException
from bson import ObjectId
from typing import Optional
from ..models.sn_response_model import SNResponse

"""

http://127.0.0.1:8000/docs pour le Swagger

"""

router_speaker_note = APIRouter(prefix="/speaker_notes", tags=["speaker_notes"])

# Create a speaker_note
@router_speaker_note.post("/", response_model=SNResponse)
async def create_speaker_note(speaker_note: dict):
    """Create a new speaker note."""
    from app import get_collection
    collection = get_collection("SPEAKER_NOTES")
    
    if not speaker_note.get("title") or not speaker_note.get("content"):
        return SNResponse.error("Title and content are required", 400)
    
    try:
        if collection is not None:
            result = collection.insert_one(speaker_note)
            speaker_note["_id"] = str(result.inserted_id)
            return SNResponse.success(speaker_note, "Speaker note created successfully", 201)
        return SNResponse.error("No collection found", 500)
    except Exception as e:
        return SNResponse.error(f"Failed to create speaker note: {str(e)}", 500)

# Get all speaker notes or basic info
@router_speaker_note.get("/", response_model=SNResponse)
async def get_speaker_notes():
    """Get all speaker notes."""
    from app import get_collection
    
    collection = get_collection("SPEAKER_NOTES")
    if collection is not None:
        try:
            # Get all speaker notes and convert ObjectId to string
            speaker_notes = list(collection.find({}))
            for note in speaker_notes:
                note["_id"] = str(note["_id"])
            
            return SNResponse.success(speaker_notes, "Speaker notes retrieved successfully")
        except Exception as e:
            return SNResponse.error(f"Failed to retrieve speaker notes: {str(e)}", 500)
    return SNResponse.error("No collection found", 500)