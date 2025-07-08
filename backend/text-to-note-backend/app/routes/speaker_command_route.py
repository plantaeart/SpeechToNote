from fastapi import APIRouter, HTTPException
from bson import ObjectId
from typing import Optional
from datetime import datetime
from ..models.response.response_model import SNResponse
from ..models.speaker_command.sc_request_model import SCRequest
from ..models.speaker_command.speaker_command_model import SpeakerCommand

"""

http://127.0.0.1:8000/docs pour le Swagger

"""

router_speaker_command = APIRouter(prefix="/speaker_commands", tags=["speaker_commands"])

# Create a speaker_command
@router_speaker_command.post("/", response_model=SNResponse)
async def create_speaker_command(request: SCRequest):
    """Create a new speaker command."""
    from app import get_collection
    collection = get_collection("COMMANDS")
    
    # Validate that we have data to process
    if not request.data:
        return SNResponse.error("Data array is required", 400)
    
    try:
        if collection is not None:
            created_commands = []
            
            # Get the highest id_command to continue the sequence
            last_command = collection.find_one({}, sort=[("id_command", -1)])
            next_id = (last_command["id_command"] + 1) if last_command and "id_command" in last_command else 1
            
            for speaker_command_create in request.data:
                # Convert Pydantic model to dict for MongoDB
                speaker_command_dump = speaker_command_create.model_dump()
                
                # Add auto-incremented id_command and timestamps (local time)
                current_time = datetime.now()  # Use local timezone
                speaker_command_dump["id_command"] = next_id
                speaker_command_dump["schema_version"] = "1.0.0"
                speaker_command_dump["created_at"] = current_time
                speaker_command_dump["updated_at"] = current_time
                
                next_id += 1
                
                result = collection.insert_one(speaker_command_dump)
                speaker_command_dump["_id"] = str(result.inserted_id)
                created_commands.append(speaker_command_dump)
            
            return SNResponse.success(created_commands, "Speaker commands created successfully", 201)
        return SNResponse.error("No collection found", 500)
    except Exception as e:
        return SNResponse.error(f"Failed to create speaker commands: {str(e)}", 500)

# Get all speaker commands
@router_speaker_command.get("/", response_model=SNResponse)
async def get_speaker_commands():
    """Get all speaker commands."""
    from app import get_collection
    
    collection = get_collection("COMMANDS")
    if collection is not None:
        try:
            # Get all speaker commands and convert ObjectId to string
            speaker_commands = list(collection.find({}))
            for command in speaker_commands:
                command["_id"] = str(command["_id"])
            
            return SNResponse.success(speaker_commands, "Speaker commands retrieved successfully")
        except Exception as e:
            return SNResponse.error(f"Failed to retrieve speaker commands: {str(e)}", 500)
    return SNResponse.error("No collection found", 500)

# Update speaker commands
@router_speaker_command.put("/", response_model=SNResponse)
async def update_speaker_commands(request: SCRequest):
    """Update multiple speaker commands."""
    from app import get_collection
    collection = get_collection("COMMANDS")
    
    if not request.data:
        return SNResponse.error("Data array is required", 400)
    
    try:
        if collection is not None:
            updated_commands = []
            for speaker_command_update in request.data:
                # Check if id_command exists in the model
                if not hasattr(speaker_command_update, 'id_command') or not speaker_command_update.id_command:
                    return SNResponse.error("id_command is required for all speaker commands to update", 400)
                
                id_command = speaker_command_update.id_command
                
                # Convert to dict and exclude None values and id_command
                update_data = {k: v for k, v in speaker_command_update.model_dump(exclude={'id_command'}).items() if v is not None}
                update_data["updated_at"] = datetime.now()  # Always update timestamp
                
                result = collection.update_one(
                    {"id_command": id_command},
                    {"$set": update_data}
                )
                
                if result.matched_count == 0:
                    return SNResponse.error(f"Speaker command with id_command {id_command} not found", 404)
                
                # Get the updated document
                updated_doc = collection.find_one({"id_command": id_command})
                if updated_doc:
                    updated_doc["_id"] = str(updated_doc["_id"])
                    updated_commands.append(updated_doc)
            
            return SNResponse.success(updated_commands, "Speaker commands updated successfully")
        return SNResponse.error("No collection found", 500)
    except Exception as e:
        return SNResponse.error(f"Failed to update speaker commands: {str(e)}", 500)

# Delete a specific speaker command
@router_speaker_command.delete("/{id_command}", response_model=SNResponse)
async def delete_speaker_command(id_command: int):
    """Delete a specific speaker command by ID."""
    from app import get_collection
    collection = get_collection("COMMANDS")
    
    try:
        if collection is not None:
            result = collection.delete_one({"id_command": id_command})
            
            if result.deleted_count == 0:
                return SNResponse.error("Speaker command not found", 404)

            return SNResponse.success({"deleted_id_command": id_command}, f"Speaker command with id {id_command} deleted successfully")
        return SNResponse.error("No collection found", 500)
    except Exception as e:
        return SNResponse.error(f"Failed to delete speaker command: {str(e)}", 500)

# Delete all speaker commands
@router_speaker_command.delete("/", response_model=SNResponse)
async def delete_all_speaker_commands():
    """Delete all speaker commands."""
    from app import get_collection
    collection = get_collection("COMMANDS")
    
    try:
        if collection is not None:
            result = collection.delete_many({})
            
            return SNResponse.success(
                {"deleted_count": result.deleted_count}, 
                f"All speaker commands deleted successfully. {result.deleted_count} commands removed."
            )
        return SNResponse.error("No collection found", 500)
    except Exception as e:
        return SNResponse.error(f"Failed to delete all speaker commands: {str(e)}", 500)
