from fastapi.testclient import TestClient
import pytest
import json

class TestSpeakerNote:
    """Test class for Speaker Note endpoints"""
    
    def test_create_speaker_note(self, test_client: TestClient):
        """Test creating a new speaker note"""
        test_data = {
            "data": [
                {
                    "title": "Test Note",
                    "content": "This is a test note content",
                    "commands": ["save", "export"]
                }
            ]
        }
        
        response = test_client.post("/speaker_notes/", json=test_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 201
        assert response_data["message"] == "Speaker notes created successfully"
        assert len(response_data["data"]) == 1
        
        created_note = response_data["data"][0]
        assert created_note["title"] == "Test Note"
        assert created_note["content"] == "This is a test note content"
        assert created_note["commands"] == ["save", "export"]
        assert "id_note" in created_note
        assert "created_at" in created_note
        assert "updated_at" in created_note
        assert created_note["schema_version"] == "1.0.0"
    
    def test_create_multiple_speaker_notes(self, test_client: TestClient):
        """Test creating multiple speaker notes"""
        test_data = {
            "data": [
                {
                    "title": "First Note",
                    "content": "First note content",
                    "commands": ["save"]
                },
                {
                    "title": "Second Note", 
                    "content": "Second note content",
                    "commands": ["export"]
                }
            ]
        }
        
        response = test_client.post("/speaker_notes/", json=test_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 201
        assert len(response_data["data"]) == 2
        
        # Check id_note incrementation
        first_note = response_data["data"][0]
        second_note = response_data["data"][1]
        assert second_note["id_note"] == first_note["id_note"] + 1
    
    def test_create_speaker_note_missing_title(self, test_client: TestClient):
        """Test creating speaker note with missing title"""
        test_data = {
            "data": [
                {
                    "content": "Content without title",
                    "commands": []
                }
            ]
        }
        
        response = test_client.post("/speaker_notes/", json=test_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_create_speaker_note_empty_data(self, test_client: TestClient):
        """Test creating speaker note with empty data array"""
        test_data = {"data": []}
        
        response = test_client.post("/speaker_notes/", json=test_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 400
        assert "Data array is required" in response_data["message"]
    
    def test_get_all_speaker_notes(self, test_client: TestClient):
        """Test getting all speaker notes"""
        # First create some notes
        test_data = {
            "data": [
                {
                    "title": "Note 1",
                    "content": "Content 1",
                    "commands": ["save"]
                },
                {
                    "title": "Note 2",
                    "content": "Content 2", 
                    "commands": ["export"]
                }
            ]
        }
        test_client.post("/speaker_notes/", json=test_data)
        
        # Then get all notes
        response = test_client.get("/speaker_notes/")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 200
        assert response_data["message"] == "Speaker notes retrieved successfully"
        assert len(response_data["data"]) == 2
    
    def test_get_empty_speaker_notes(self, test_client: TestClient):
        """Test getting speaker notes when none exist"""
        response = test_client.get("/speaker_notes/")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 200
        assert response_data["data"] == []
    
    def test_update_speaker_notes(self, test_client: TestClient):
        """Test updating speaker notes"""
        # First create a note
        create_data = {
            "data": [
                {
                    "title": "Original Title",
                    "content": "Original content",
                    "commands": ["save"]
                }
            ]
        }
        create_response = test_client.post("/speaker_notes/", json=create_data)
        created_note = create_response.json()["data"][0]
        note_id = created_note["id_note"]
        
        # Then update it
        update_data = {
            "data": [
                {
                    "id_note": note_id,
                    "title": "Updated Title",
                    "content": "Updated content"
                }
            ]
        }
        
        response = test_client.put("/speaker_notes/", json=update_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 200
        assert response_data["message"] == "Speaker notes updated successfully"
        
        updated_note = response_data["data"][0]
        assert updated_note["title"] == "Updated Title"
        assert updated_note["content"] == "Updated content"
        assert updated_note["commands"] == ["save"]  # Should keep original commands
    
    def test_update_nonexistent_speaker_note(self, test_client: TestClient):
        """Test updating a speaker note that doesn't exist"""
        update_data = {
            "data": [
                {
                    "id_note": 99999,
                    "title": "Non-existent note"
                }
            ]
        }
        
        response = test_client.put("/speaker_notes/", json=update_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 404
        assert "not found" in response_data["message"]
    
    def test_delete_speaker_note(self, test_client: TestClient):
        """Test deleting a specific speaker note"""
        # First create a note
        create_data = {
            "data": [
                {
                    "title": "Note to delete",
                    "content": "This will be deleted",
                    "commands": []
                }
            ]
        }
        create_response = test_client.post("/speaker_notes/", json=create_data)
        created_note = create_response.json()["data"][0]
        note_id = created_note["id_note"]
        
        # Then delete it
        response = test_client.delete(f"/speaker_notes/{note_id}")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 200
        assert response_data["data"]["deleted_id_note"] == note_id
        
        # Verify it's deleted
        get_response = test_client.get("/speaker_notes/")
        get_data = get_response.json()
        assert len(get_data["data"]) == 0
    
    def test_delete_nonexistent_speaker_note(self, test_client: TestClient):
        """Test deleting a speaker note that doesn't exist"""
        response = test_client.delete("/speaker_notes/99999")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 404
        assert "not found" in response_data["message"]
    
    def test_delete_all_speaker_notes(self, test_client: TestClient):
        """Test deleting all speaker notes"""
        # First create some notes
        create_data = {
            "data": [
                {
                    "title": "Note 1",
                    "content": "Content 1",
                    "commands": []
                },
                {
                    "title": "Note 2", 
                    "content": "Content 2",
                    "commands": []
                }
            ]
        }
        test_client.post("/speaker_notes/", json=create_data)
        
        # Then delete all
        response = test_client.delete("/speaker_notes/")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 200
        assert response_data["data"]["deleted_count"] == 2
        
        # Verify all are deleted
        get_response = test_client.get("/speaker_notes/")
        get_data = get_response.json()
        assert len(get_data["data"]) == 0
    
    def test_delete_speaker_notes_by_ids(self, test_client):
        """Test deleting multiple speaker notes by their IDs"""
        # First create some notes
        create_data = {
            "data": [
                {
                    "title": "Note 1",
                    "content": "Content 1",
                    "commands": []
                },
                {
                    "title": "Note 2", 
                    "content": "Content 2",
                    "commands": []
                },
                {
                    "title": "Note 3",
                    "content": "Content 3", 
                    "commands": []
                }
            ]
        }
        create_response = test_client.post("/speaker_notes/", json=create_data)
        created_notes = create_response.json()["data"]
        
        # Get IDs of first two notes
        ids_to_delete = [created_notes[0]["id_note"], created_notes[1]["id_note"]]
        
        # Delete by IDs
        delete_data = {
            "ids_note": ids_to_delete
        }
        response = test_client.request(
            "DELETE",
            "/speaker_notes/ids",
            json=delete_data
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 200
        assert response_data["data"]["deleted_count"] == 2
        assert "deleted successfully" in response_data["message"]
        
        # Verify only one note remains
        get_response = test_client.get("/speaker_notes/")
        get_data = get_response.json()
        assert len(get_data["data"]) == 1
        assert get_data["data"][0]["id_note"] == created_notes[2]["id_note"]
    
    def test_delete_speaker_notes_by_empty_ids(self, test_client):
        """Test deleting speaker notes with empty IDs array"""
        delete_data = {
            "ids_note": []
        }
        response = test_client.request(
            "DELETE",
            "/speaker_notes/ids",
            json=delete_data
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 400
        assert "required" in response_data["message"]
    
    def test_delete_speaker_notes_by_nonexistent_ids(self, test_client):
        """Test deleting speaker notes with non-existent IDs"""
        delete_data = {
            "ids_note": [99999, 88888]
        }
        response = test_client.request(
            "DELETE",
            "/speaker_notes/ids",
            json=delete_data
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 200
        assert response_data["data"]["deleted_count"] == 0
