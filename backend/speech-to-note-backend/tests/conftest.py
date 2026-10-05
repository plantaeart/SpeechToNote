import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from app.main import app
from app.configs.config import config

# Test database configuration
TEST_DATABASE_NAME = f"{config.DATABASE_NAME}_test"
TEST_COLLECTIONS = ["SPEAKER_NOTES_TEST", "COMMANDS_TEST"]





@pytest.fixture(scope="session")
def mongo_available():
    """True when MongoDB is reachable AND we can actually write to it.

    A bare ping succeeds even against a server that requires authentication, so
    probe with a real write instead — otherwise every test errors out instead
    of skipping.
    """
    client = None
    try:
        client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=2000)
        client[TEST_DATABASE_NAME]["__probe__"].insert_one({"ok": 1})
        client[TEST_DATABASE_NAME]["__probe__"].delete_many({})
        return True
    except PyMongoError as error:
        print(
            f"\n⚠️  Cannot write to MongoDB at {config.MONGO_URI}: {error}\n"
            "   Database tests will be skipped. Point MONGO_URI at a MongoDB "
            "you control (see README).\n"
        )
        return False
    finally:
        if client is not None:
            client.close()


@pytest.fixture(scope="session")
def test_db(mongo_available):
    """Test database handle. Skips the test when MongoDB is unusable."""
    if not mongo_available:
        pytest.skip(f"MongoDB is not usable at {config.MONGO_URI} (see README)")

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


@pytest.fixture
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
def clean_collections(test_db, mock_get_collection):
    """Clean up collections before and after each test"""
    for collection_name in TEST_COLLECTIONS:
        test_db[collection_name].delete_many({})

    yield

    for collection_name in TEST_COLLECTIONS:
        test_db[collection_name].delete_many({})


@pytest.fixture
def test_client(test_db, mock_get_collection, clean_collections):
    """Create a test client for the FastAPI app"""
    with TestClient(app) as client:
        yield client