import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient
from app import app
from app.config_dev import MONGO_URI, DATABASE_NAME

# Test database configuration - USE A COMPLETELY SEPARATE DATABASE
TEST_DATABASE_NAME = f"{DATABASE_NAME}_test"
TEST_COLLECTIONS = ["SPEAKER_NOTES_TEST", "COMMANDS_TEST"]

@pytest.fixture(scope="session")
def test_db():
    """Setup and teardown test database"""
    # Setup: Create test database connection
    test_client = MongoClient(MONGO_URI)
    test_db = test_client[TEST_DATABASE_NAME]  # Use separate test database
    
    yield test_db
    
    # Teardown: Drop test database completely
    test_client.drop_database(TEST_DATABASE_NAME)
    test_client.close()

@pytest.fixture(autouse=True)
def mock_get_collection(monkeypatch, test_db):
    """Mock the get_collection function to use test collections"""
    def mock_get_collection_func(collection_name: str = "SPEAKER_NOTES"):
        collection_map = {
            "SPEAKER_NOTES": "SPEAKER_NOTES_TEST",
            "COMMANDS": "COMMANDS_TEST"
        }
        test_collection_name = collection_map.get(collection_name, f"{collection_name}_TEST")
        return test_db[test_collection_name]
    
    # Import and patch the get_collection function
    from app import get_collection
    monkeypatch.setattr("app.get_collection", mock_get_collection_func)

@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app"""
    with TestClient(app) as client:
        yield client

# clean collections and remove test database
@pytest.fixture(autouse=True)
def clean_collections(test_db):
    """Clean up collections before and after each test"""
    try:
        # Clear collections before each test
        for collection_name in TEST_COLLECTIONS:
            test_db[collection_name].delete_many({})
        
        yield
        
    except Exception as e:
        print(f"Error during test execution: {e}")
        raise
    finally:
        # Always delete database, even if error occurs
        try:
            test_db.client.drop_database(TEST_DATABASE_NAME)
            print(f"🗑️Test database {TEST_DATABASE_NAME} dropped after tests.")
        except Exception as cleanup_error:
            print(f"Error dropping test database: {cleanup_error}")