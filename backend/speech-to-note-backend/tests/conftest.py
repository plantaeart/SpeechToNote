import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient
from app.main import app
from app.configs.config import config

# Test database configuration
TEST_DATABASE_NAME = f"{config.DATABASE_NAME}_test"
TEST_COLLECTIONS = ["SPEAKER_NOTES_TEST", "COMMANDS_TEST"]

@pytest.fixture(scope="session")
def test_db():
    """Setup and teardown test database"""
    test_client = MongoClient(config.MONGO_URI)
    test_db = test_client[TEST_DATABASE_NAME]
    
    yield test_db
    
    try:
        test_client.drop_database(TEST_DATABASE_NAME)
        print(f"🗑️ Test database {TEST_DATABASE_NAME} dropped after all tests completed.")
    except Exception as cleanup_error:
        print(f"Error dropping test database: {cleanup_error}")
    finally:
        test_client.close()

@pytest.fixture(autouse=True)
def mock_get_collection(mocker, test_db):
    """Mock the get_collection function to use test collections"""
    def mock_get_collection_func(collection_name: str = "SPEAKER_NOTES"):
        collection_map = {
            "SPEAKER_NOTES": "SPEAKER_NOTES_TEST",
            "COMMANDS": "COMMANDS_TEST"
        }
        test_collection_name = collection_map.get(collection_name, f"{collection_name}_TEST")
        return test_db[test_collection_name]
    
    mocker.patch("app.main.get_collection", side_effect=mock_get_collection_func)

@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app"""
    with TestClient(app) as client:
        yield client

@pytest.fixture(autouse=True)
def clean_collections(test_db):
    """Clean up collections before and after each test"""
    try:
        for collection_name in TEST_COLLECTIONS:
            test_db[collection_name].delete_many({})
        
        yield
        
        for collection_name in TEST_COLLECTIONS:
            test_db[collection_name].delete_many({})
        
    except Exception as e:
        print(f"Error during test execution: {e}")
        raise