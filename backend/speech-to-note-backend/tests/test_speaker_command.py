from fastapi.testclient import TestClient
import json

class TestSpeakerCommand:
    """Test class for Speaker Command endpoints"""
    
    def test_create_speaker_command(self, test_client: TestClient):
        """Test creating a new speaker command"""
        test_data = {
            "data": [
                {
                    "command_name": "titre",
                    "command_vocal": ["titre", "titres"],
                    "command_description": "Formate comme un titre principal",
                    "html_tag_start": "<h1>",
                    "html_tag_end": "</h1>"
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
        assert created_command["command_name"] == "titre"
        assert created_command["command_vocal"] == ["titre", "titres"]
        assert created_command["command_description"] == "Formate comme un titre principal"
        assert created_command["html_tag_start"] == "<h1>"
        assert created_command["html_tag_end"] == "</h1>"
        assert "id_command" in created_command
        assert "created_at" in created_command
        assert "updated_at" in created_command
        assert created_command["schema_version"] == "1.0.1"

    def test_migration_from_old_schema(self, test_client: TestClient):
        """Test that old schema documents are migrated when retrieved"""
        from app import get_collection
        from app.migrations.speaker_command_migrations import SpeakerCommandMigrations
        
        # Insert an old schema document directly
        collection = get_collection("COMMANDS")
        if collection is not None:
            old_doc = {
                "id_command": 999,
                "command_name": "old_command",
                "command_vocal": "single vocal command",  # Old string format
                "command_description": "Old format command",
                "schema_version": "1.0.0"  # Old version
            }
            collection.insert_one(old_doc)
            
            # Manually run migration before retrieving
            SpeakerCommandMigrations.run_migrations(collection)
            
            # Retrieve all commands - should show migrated data
            response = test_client.get("/speaker_commands/")
            
            assert response.status_code == 200
            response_data = response.json()
            
            # Find the migrated command
            migrated_command = None
            for cmd in response_data["data"]:
                if cmd["id_command"] == 999:
                    migrated_command = cmd
                    break
            
            assert migrated_command is not None
            assert migrated_command["schema_version"] == "1.0.1"
            assert isinstance(migrated_command["command_vocal"], list)
            assert migrated_command["command_vocal"] == ["single vocal command"]
            assert "html_tag_start" in migrated_command
            assert migrated_command["html_tag_start"] == ""  # Should be empty string from migration
            assert "html_tag_end" in migrated_command
            assert migrated_command["html_tag_end"] == ""  # Should be empty string from migration

    def test_create_speaker_command_without_html_tags(self, test_client: TestClient):
        """Test creating speaker command without HTML tags"""
        test_data = {
            "data": [
                {
                    "command_name": "pause",
                    "command_vocal": ["pause", "arrêt"]
                }
            ]
        }
        
        response = test_client.post("/speaker_commands/", json=test_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 201
        
        created_command = response_data["data"][0]
        assert created_command["command_name"] == "pause"
        assert created_command["command_vocal"] == ["pause", "arrêt"]
        assert created_command["html_tag_start"] is None
        assert created_command["html_tag_end"] is None

    def test_create_speaker_command_with_line_break(self, test_client: TestClient):
        """Test creating speaker command for line break"""
        test_data = {
            "data": [
                {
                    "command_name": "saut_ligne",
                    "command_vocal": ["saut de ligne", "nouvelle ligne"],
                    "command_description": "Insère un saut de ligne",
                    "html_tag_start": "<br>",
                    "html_tag_end": ""
                }
            ]
        }
        
        response = test_client.post("/speaker_commands/", json=test_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 201
        
        created_command = response_data["data"][0]
        assert created_command["command_vocal"] == ["saut de ligne", "nouvelle ligne"]
        assert created_command["html_tag_start"] == "<br>"
        assert created_command["html_tag_end"] == ""

    def test_create_speaker_command_empty_vocal_list(self, test_client: TestClient):
        """Test creating speaker command with empty vocal commands list"""
        test_data = {
            "data": [
                {
                    "command_name": "test",
                    "command_vocal": []
                }
            ]
        }
        
        response = test_client.post("/speaker_commands/", json=test_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 400
        assert "must contain at least one non-empty vocal command" in response_data["message"]

    def test_create_speaker_command_empty_vocal_strings(self, test_client: TestClient):
        """Test creating speaker command with empty strings in vocal commands"""
        test_data = {
            "data": [
                {
                    "command_name": "test",
                    "command_vocal": ["", "  ", "valid"]
                }
            ]
        }
        
        response = test_client.post("/speaker_commands/", json=test_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 400
        assert "must contain at least one non-empty vocal command" in response_data["message"]
    
    def test_create_multiple_speaker_commands(self, test_client: TestClient):
        """Test creating multiple speaker commands"""
        test_data = {
            "data": [
                {
                    "command_name": "titre",
                    "command_vocal": ["titre", "titres"],
                    "html_tag_start": "<h1>",
                    "html_tag_end": "</h1>"
                },
                {
                    "command_name": "sous_titre",
                    "command_vocal": ["sous-titre", "sous titre"],
                    "html_tag_start": "<h2>",
                    "html_tag_end": "</h2>"
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
    
    def test_create_speaker_command_missing_name(self, test_client: TestClient):
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
    
    def test_create_speaker_command_missing_vocal(self, test_client: TestClient):
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
    
    def test_get_all_speaker_commands(self, test_client: TestClient):
        """Test getting all speaker commands"""
        # First create some commands
        test_data = {
            "data": [
                {
                    "command_name": "command_1",
                    "command_vocal": ["première commande"],
                    "command_description": "First command",
                    "html_tag_start": "<p>",
                    "html_tag_end": "</p>"
                },
                {
                    "command_name": "command_2",
                    "command_vocal": ["deuxième commande"],
                    "command_description": "Second command",
                    "html_tag_start": "<p>",
                    "html_tag_end": "</p>"
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
    
    def test_get_empty_speaker_commands(self, test_client: TestClient):
        """Test getting speaker commands when none exist"""
        response = test_client.get("/speaker_commands/")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 200
        assert response_data["data"] == []
    
    def test_update_speaker_commands(self, test_client: TestClient):
        """Test updating speaker commands"""
        # First create a command
        create_data = {
            "data": [
                {
                    "command_name": "original_command",
                    "command_vocal": ["commande originale"],
                    "command_description": "Original description",
                    "html_tag_start": "<p>",
                    "html_tag_end": "</p>"
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
                    "command_vocal": ["commande mise à jour", "updated command"],
                    "command_description": "Updated description",
                    "html_tag_start": "<h3>",
                    "html_tag_end": "</h3>"
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
        assert updated_command["command_vocal"] == ["commande mise à jour", "updated command"]
        assert updated_command["command_description"] == "Updated description"
        assert updated_command["html_tag_start"] == "<h3>"
        assert updated_command["html_tag_end"] == "</h3>"

    def test_update_speaker_command_empty_vocal_list(self, test_client: TestClient):
        """Test updating speaker command with empty vocal commands list"""
        # First create a command
        create_data = {
            "data": [
                {
                    "command_name": "test_command",
                    "command_vocal": ["test"],
                    "html_tag_start": "<p>",
                    "html_tag_end": "</p>"
                }
            ]
        }
        create_response = test_client.post("/speaker_commands/", json=create_data)
        command_id = create_response.json()["data"][0]["id_command"]
        
        # Try to update with empty vocal list
        update_data = {
            "data": [
                {
                    "id_command": command_id,
                    "command_vocal": []
                }
            ]
        }
        
        response = test_client.put("/speaker_commands/", json=update_data)
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 400
        assert "must contain at least one non-empty vocal command" in response_data["message"]

    def test_update_nonexistent_speaker_command(self, test_client: TestClient):
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
    
    def test_delete_speaker_command(self, test_client: TestClient):
        """Test deleting a specific speaker command"""
        # First create a command
        create_data = {
            "data": [
                {
                    "command_name": "command_to_delete",
                    "command_vocal": ["à supprimer"],
                    "command_description": "This will be deleted",
                    "html_tag_start": "<p>",
                    "html_tag_end": "</p>"
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
    
    def test_delete_nonexistent_speaker_command(self, test_client: TestClient):
        """Test deleting a speaker command that doesn't exist"""
        response = test_client.delete("/speaker_commands/99999")
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 404
        assert "not found" in response_data["message"]
    
    def test_delete_all_speaker_commands(self, test_client: TestClient):
        """Test deleting all speaker commands"""
        # First create some commands
        create_data = {
            "data": [
                {
                    "command_name": "command_1",
                    "command_vocal": ["première"],
                    "command_description": "First",
                    "html_tag_start": "<p>",
                    "html_tag_end": "</p>"
                },
                {
                    "command_name": "command_2",
                    "command_vocal": ["deuxième"],
                    "command_description": "Second",
                    "html_tag_start": "<p>",
                    "html_tag_end": "</p>"
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
    
    def test_delete_speaker_commands_by_ids(self, test_client: TestClient):
        """Test deleting multiple speaker commands by their IDs"""
        # First create some commands
        create_data = {
            "data": [
                {
                    "command_name": "command_1",
                    "command_vocal": ["première commande"],
                    "command_description": "First command",
                    "html_tag_start": "<p>",
                    "html_tag_end": "</p>"
                },
                {
                    "command_name": "command_2",
                    "command_vocal": ["deuxième commande"],
                    "command_description": "Second command",
                    "html_tag_start": "<p>",
                    "html_tag_end": "</p>"
                },
                {
                    "command_name": "command_3",
                    "command_vocal": ["troisième commande"],
                    "command_description": "Third command",
                    "html_tag_start": "<p>",
                    "html_tag_end": "</p>"
                }
            ]
        }
        create_response = test_client.post("/speaker_commands/", json=create_data)
        created_commands = create_response.json()["data"]
        
        # Get IDs of first two commands
        ids_to_delete = [created_commands[0]["id_command"], created_commands[1]["id_command"]]
        
        # Delete by IDs
        delete_data = {
            "ids_command": ids_to_delete
        }
        response = test_client.request(
            "DELETE",
            "/speaker_commands/ids",
            json=delete_data
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 200
        assert response_data["data"]["deleted_count"] == 2
        assert "deleted successfully" in response_data["message"]
        
        # Verify only one command remains
        get_response = test_client.get("/speaker_commands/")
        get_data = get_response.json()
        assert len(get_data["data"]) == 1
        assert get_data["data"][0]["id_command"] == created_commands[2]["id_command"]
    
    def test_delete_speaker_commands_by_empty_ids(self, test_client: TestClient):
        """Test deleting speaker commands with empty IDs array"""
        delete_data = {
            "ids_command": []
        }
        response = test_client.request(
            "DELETE",
            "/speaker_commands/ids",
            json=delete_data
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 400
        assert "required" in response_data["message"]
    
    def test_delete_speaker_commands_by_nonexistent_ids(self, test_client: TestClient):
        """Test deleting speaker commands with non-existent IDs"""
        delete_data = {
            "ids_command": [99999, 88888]
        }
        response = test_client.request(
            "DELETE",
            "/speaker_commands/ids",
            json=delete_data
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status_code"] == 200
        assert response_data["data"]["deleted_count"] == 0
