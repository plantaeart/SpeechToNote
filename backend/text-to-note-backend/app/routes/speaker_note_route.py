from fastapi import APIRouter, HTTPException
from bson import ObjectId
from typing import Optional
from datetime import datetime, timezone
from ..models.speaker_note.sn_response_model import SNResponse
from ..models.speaker_note.sn_request_model import SNRequest
from ..models.speaker_note.speaker_note_model import SpeakerNote

"""

http://127.0.0.1:8000/docs pour le Swagger

"""

router_speaker_note = APIRouter(prefix="/speaker_notes", tags=["speaker_notes"])

# Create a speaker_note
@router_speaker_note.post("/", response_model=SNResponse)
async def create_speaker_note(request: SNRequest):
    """Create a new speaker note."""
    from app import get_collection
    collection = get_collection("SPEAKER_NOTES")
    
    # Validate that we have data to process
    if not request.data:
        return SNResponse.error("Data array is required", 400)
    
    try:
        if collection is not None:
            created_notes = []
            
            # Get the highest id_note to continue the sequence
            last_note = collection.find_one({}, sort=[("id_note", -1)])
            next_id = (last_note["id_note"] + 1) if last_note and "id_note" in last_note else 1
            
            for speaker_note in request.data:
                if not speaker_note.get("title") or not speaker_note.get("content"):
                    return SNResponse.error("Title and content are required for all speaker notes", 400)
                
                # Add auto-incremented id_note and timestamps
                current_time = datetime.now(timezone.utc)
                speaker_note["id_note"] = next_id
                speaker_note["schema_version"] = "1.1.0"
                speaker_note["created_at"] = current_time
                speaker_note["updated_at"] = current_time
                
                # Set default commands if not provided
                if "commands" not in speaker_note:
                    speaker_note["commands"] = []
                
                next_id += 1
                
                result = collection.insert_one(speaker_note)
                speaker_note["_id"] = str(result.inserted_id)
                created_notes.append(speaker_note)
            
            return SNResponse.success(created_notes, "Speaker notes created successfully", 201)
        return SNResponse.error("No collection found", 500)
    except Exception as e:
        return SNResponse.error(f"Failed to create speaker notes: {str(e)}", 500)

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

# Update speaker notes
@router_speaker_note.put("/", response_model=SNResponse)
async def update_speaker_notes(request: SNRequest):
    """Update multiple speaker notes."""
    from app import get_collection
    collection = get_collection("SPEAKER_NOTES")
    
    if not request.data:
        return SNResponse.error("Data array is required", 400)
    
    try:
        if collection is not None:
            updated_notes = []
            for speaker_note in request.data:
                if not speaker_note.get("id_note"):
                    return SNResponse.error("id_note is required for all speaker notes to update", 400)
                
                id_note = speaker_note.get("id_note")
                
                # Remove id_note from the update data to avoid overwriting it
                update_data = {k: v for k, v in speaker_note.items() if k != "id_note"}
                update_data["updated_at"] = datetime.now(timezone.utc)
                
                result = collection.update_one(
                    {"id_note": id_note},
                    {"$set": update_data}
                )
                
                if result.matched_count == 0:
                    return SNResponse.error(f"Speaker note with id_note {id_note} not found", 404)
                
                # Get the updated document
                updated_doc = collection.find_one({"id_note": id_note})
                if updated_doc:
                    updated_doc["_id"] = str(updated_doc["_id"])
                    updated_notes.append(updated_doc)
            
            return SNResponse.success(updated_notes, "Speaker notes updated successfully")
        return SNResponse.error("No collection found", 500)
    except Exception as e:
        return SNResponse.error(f"Failed to update speaker notes: {str(e)}", 500)

# Delete a specific speaker note
@router_speaker_note.delete("/{id_note}", response_model=SNResponse)
async def delete_speaker_note(id_note: int):
    """Delete a specific speaker note by ID."""
    from app import get_collection
    collection = get_collection("SPEAKER_NOTES")
    
    try:
        if collection is not None:
            result = collection.delete_one({"id_note": id_note})
            
            if result.deleted_count == 0:
                return SNResponse.error("Speaker note not found", 404)
            
            return SNResponse.success({"deleted_id_note": id_note}, "Speaker note deleted successfully")
        return SNResponse.error("No collection found", 500)
    except Exception as e:
        return SNResponse.error(f"Failed to delete speaker note: {str(e)}", 500)

# Delete all speaker notes
@router_speaker_note.delete("/", response_model=SNResponse)
async def delete_all_speaker_notes():
    """Delete all speaker notes."""
    from app import get_collection
    collection = get_collection("SPEAKER_NOTES")
    
    try:
        if collection is not None:
            result = collection.delete_many({})
            
            return SNResponse.success(
                {"deleted_count": result.deleted_count}, 
                f"All speaker notes deleted successfully. {result.deleted_count} notes removed."
            )
        return SNResponse.error("No collection found", 500)
    except Exception as e:
        return SNResponse.error(f"Failed to delete all speaker notes: {str(e)}", 500)