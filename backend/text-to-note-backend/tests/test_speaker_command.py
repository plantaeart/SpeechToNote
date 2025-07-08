from fastapi.testclient import TestClient
import pytest

class TestSpeakerCommand:
    """Test class for Speaker Command endpoints"""
    
    def test_create_speaker_command(self, test_client):
        """Test creating a new speaker command"""
        test_data = {
            "data": [
                {
                    "command_name": "save_note",
                    "command_vocal": "sauvegarder la note",
                    "command_description": "Sauvegarde la note en cours"
                }
            ]
        }
        
        response = test_client.post("/speaker_commands/", json=test_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 201
        assert response_data["message"] == "Speaker commands created successfully"
        assert len(response_data["data"]) == 1
        
        created_command = response_data["data"][0]
        assert created_command["command_name"] == "save_note"
        assert created_command["command_vocal"] == "sauvegarder la note"
        assert created_command["command_description"] == "Sauvegarde la note en cours"
        assert "id_command" in created_command
        assert "created_at" in created_command
        assert "updated_at" in created_command
        assert created_command["schema_version"] == "1.0.0"
    
    def test_create_speaker_command_without_description(self, test_client):
        """Test creating speaker command without description"""
        test_data = {
            "data": [
                {
                    "command_name": "export_pdf",
                    "command_vocal": "exporter en PDF"
                }
            ]
        }
        
        response = test_client.post("/speaker_commands/", json=test_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 201
        
        created_command = response_data["data"][0]
        assert created_command["command_name"] == "export_pdf"
        assert created_command["command_vocal"] == "exporter en PDF"
        assert created_command["command_description"] is None
    
    def test_create_multiple_speaker_commands(self, test_client):
        """Test creating multiple speaker commands"""
        test_data = {
            "data": [
                {
                    "command_name": "save_note",
                    "command_vocal": "sauvegarder",
                    "command_description": "Save command"
                },
                {
                    "command_name": "delete_note",
                    "command_vocal": "supprimer",
                    "command_description": "Delete command"
                }
            ]
        }
        
        response = test_client.post("/speaker_commands/", json=test_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 201
        assert len(response_data["data"]) == 2
        
        # Check id_command incrementation
        first_command = response_data["data"][0]
        second_command = response_data["data"][1]
        assert second_command["id_command"] == first_command["id_command"] + 1
    
    def test_create_speaker_command_missing_name(self, test_client):
        """Test creating speaker command with missing command_name"""
        test_data = {
            "data": [
                {
                    "command_vocal": "commande sans nom"
                }
            ]
        }
        
        response = test_client.post("/speaker_commands/", json=test_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_create_speaker_command_missing_vocal(self, test_client):
        """Test creating speaker command with missing command_vocal"""
        test_data = {
            "data": [
                {
                    "command_name": "test_command"
                }
            ]
        }
        
        response = test_client.post("/speaker_commands/", json=test_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_get_all_speaker_commands(self, test_client):
        """Test getting all speaker commands"""
        # First create some commands
        test_data = {
            "data": [
                {
                    "command_name": "command_1",
                    "command_vocal": "première commande",
                    "command_description": "First command"
                },
                {
                    "command_name": "command_2",
                    "command_vocal": "deuxième commande",
                    "command_description": "Second command"
                }
            ]
        }
        test_client.post("/speaker_commands/", json=test_data)
        
        # Then get all commands
        response = test_client.get("/speaker_commands/")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 200
        assert response_data["message"] == "Speaker commands retrieved successfully"
        assert len(response_data["data"]) == 2
    
    def test_get_empty_speaker_commands(self, test_client):
        """Test getting speaker commands when none exist"""
        response = test_client.get("/speaker_commands/")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 200
        assert response_data["data"] == []
    
    def test_update_speaker_commands(self, test_client):
        """Test updating speaker commands"""
        # First create a command
        create_data = {
            "data": [
                {
                    "command_name": "original_command",
                    "command_vocal": "commande originale",
                    "command_description": "Original description"
                }
            ]
        }
        create_response = test_client.post("/speaker_commands/", json=create_data)
        created_command = create_response.json()["data"][0]
        command_id = created_command["id_command"]
        
        # Then update it
        update_data = {
            "data": [
                {
                    "id_command": command_id,
                    "command_name": "updated_command",
                    "command_description": "Updated description"
                }
            ]
        }
        
        response = test_client.put("/speaker_commands/", json=update_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 200
        assert response_data["message"] == "Speaker commands updated successfully"
        
        updated_command = response_data["data"][0]
        assert updated_command["command_name"] == "updated_command"
        assert updated_command["command_description"] == "Updated description"
        assert updated_command["command_vocal"] == "commande originale"  # Should keep original vocal
    
    def test_update_nonexistent_speaker_command(self, test_client):
        """Test updating a speaker command that doesn't exist"""
        update_data = {
            "data": [
                {
                    "id_command": 99999,
                    "command_name": "non_existent"
                }
            ]
        }
        
        response = test_client.put("/speaker_commands/", json=update_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 404
        assert "not found" in response_data["message"]
    
    def test_delete_speaker_command(self, test_client):
        """Test deleting a specific speaker command"""
        # First create a command
        create_data = {
            "data": [
                {
                    "command_name": "command_to_delete",
                    "command_vocal": "à supprimer",
                    "command_description": "This will be deleted"
                }
            ]
        }
        create_response = test_client.post("/speaker_commands/", json=create_data)
        created_command = create_response.json()["data"][0]
        command_id = created_command["id_command"]
        
        # Then delete it
        response = test_client.delete(f"/speaker_commands/{command_id}")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 200
        assert response_data["data"]["deleted_id_command"] == command_id
        
        # Verify it's deleted
        get_response = test_client.get("/speaker_commands/")
        get_data = get_response.json()
        assert len(get_data["data"]) == 0
    
    def test_delete_nonexistent_speaker_command(self, test_client):
        """Test deleting a speaker command that doesn't exist"""
        response = test_client.delete("/speaker_commands/99999")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 404
        assert "not found" in response_data["message"]
    
    def test_delete_all_speaker_commands(self, test_client):
        """Test deleting all speaker commands"""
        # First create some commands
        create_data = {
            "data": [
                {
                    "command_name": "command_1",
                    "command_vocal": "première",
                    "command_description": "First"
                },
                {
                    "command_name": "command_2",
                    "command_vocal": "deuxième", 
                    "command_description": "Second"
                }
            ]
        }
        test_client.post("/speaker_commands/", json=create_data)
        
        # Then delete all
        response = test_client.delete("/speaker_commands/")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 200
        assert response_data["data"]["deleted_count"] == 2
        
        # Verify all are deleted
        get_response = test_client.get("/speaker_commands/")
        get_data = get_response.json()
        assert len(get_data["data"]) == 0
        
        # Verify all are deleted
        get_response = test_client.get("/speaker_commands/")
        get_data = get_response.json()
        assert len(get_data["data"]) == 0
        get_response = test_client.get("/speaker_commands/")
        get_data = get_response.json()
        assert len(get_data["data"]) == 0
