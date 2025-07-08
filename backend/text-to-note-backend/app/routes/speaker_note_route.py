from fastapi import APIRouter, Body
from datetime import datetime
from typing import List
from ..models.response.response_model import SNResponse
from ..models.speaker_note.sn_request_model import SNCreateRequest, SNUpdateRequest, SNDeleteByIdsRequest

router_speaker_note = APIRouter(prefix="/speaker_notes", tags=["speaker_notes"])

# Create a speaker_note
@router_speaker_note.post("/", response_model=SNResponse)
async def create_speaker_note(request: SNCreateRequest):
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
            
            for speaker_note_create in request.data:
                # Convert Pydantic model to dict for MongoDB
                speaker_note_dump = speaker_note_create.model_dump()
                
                # Add auto-incremented id_note and timestamps (local time)
                current_time = datetime.now()  # Use local timezone
                speaker_note_dump["id_note"] = next_id
                speaker_note_dump["schema_version"] = "1.0.0"
                speaker_note_dump["created_at"] = current_time
                speaker_note_dump["updated_at"] = current_time
                
                # Set default commands if not provided
                if "commands" not in speaker_note_dump:
                    speaker_note_dump["commands"] = []
                
                next_id += 1
                
                result = collection.insert_one(speaker_note_dump)
                speaker_note_dump["_id"] = str(result.inserted_id)
                created_notes.append(speaker_note_dump)
            
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
async def update_speaker_notes(request: SNUpdateRequest):
    """Update multiple speaker notes."""
    from app import get_collection
    collection = get_collection("SPEAKER_NOTES")
    
    if not request.data:
        return SNResponse.error("Data array is required", 400)
    
    try:
        if collection is not None:
            updated_notes = []
            for speaker_note_update in request.data:
                # id_note is guaranteed to exist because of SpeakerNoteUpdate model
                id_note = speaker_note_update.id_note
                
                # Convert to dict and exclude None values and id_note
                update_data = {k: v for k, v in speaker_note_update.model_dump(exclude={'id_note'}).items() if v is not None}
                update_data["updated_at"] = datetime.now()  # Always update timestamp
                
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

# Delete multiple speaker notes by IDs
@router_speaker_note.delete("/ids", response_model=SNResponse)
async def delete_speaker_notes_by_ids(request: SNDeleteByIdsRequest):
    """Delete multiple speaker notes by their IDs."""
    from app import get_collection
    collection = get_collection("SPEAKER_NOTES")
    
    if not request.ids_note:
        return SNResponse.error("ids_note array is required", 400)
    
    try:
        if collection is not None:
            result = collection.delete_many({"id_note": {"$in": request.ids_note}})
            
            return SNResponse.success(
                {"deleted_count": result.deleted_count}, 
                f"Speaker notes with ids {request.ids_note} deleted successfully. {result.deleted_count} notes removed."
            )
        return SNResponse.error("No collection found", 500)
    except Exception as e:
        return SNResponse.error(f"Failed to delete speaker notes: {str(e)}", 500)

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

            return SNResponse.success({"deleted_id_note": id_note}, f"Speaker note with id {id_note} deleted successfully")
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