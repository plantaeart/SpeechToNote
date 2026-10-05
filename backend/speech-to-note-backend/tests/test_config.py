"""Tests for configuration loading and safe logging of credentials."""

import importlib
import sys
import types

import pytest


def load_main():
    """Import app.main with the MongoDB-dependent startup bypassed."""
    # app.main touches MongoClient at import time, so stub it out.
    pymongo = sys.modules.get("pymongo")
    stub = types.ModuleType("pymongo")

    class _NoOpClient:
        def __init__(self, *args, **kwargs):
            pass

    stub.MongoClient = _NoOpClient
    sys.modules["pymongo"] = stub
    try:
        return importlib.import_module("app.main")
    finally:
        if pymongo is not None:
            sys.modules["pymongo"] = pymongo
        else:
            del sys.modules["pymongo"]


@pytest.mark.parametrize(
    "uri, expected",
    [
        # No credentials -> unchanged
        ("mongodb://localhost:27017", "mongodb://localhost:27017"),
        # Password hidden, user kept
        (
            "mongodb://admin:sup3rs3cret@localhost:27017",
            "mongodb://admin:***@localhost:27017",
        ),
        # User with no password
        ("mongodb://admin@localhost:27017", "mongodb://admin:***@localhost:27017"),
        # +srv scheme with credentials
        (
            "mongodb+srv://user:pw@cluster0.example.mongodb.net",
            "mongodb+srv://user:***@cluster0.example.mongodb.net",
        ),
    ],
)
def test_mask_mongo_uri_hides_credentials(uri, expected):
    main = load_main()
    assert main._mask_mongo_uri(uri) == expected


def test_mask_mongo_uri_never_leaks_password():
    main = load_main()
    masked = main._mask_mongo_uri("mongodb://admin:hunter2@localhost:27017")
    assert "hunter2" not in masked


def test_config_loads_without_env_file():
    """A fresh clone must boot with no .env present (gitignored)."""
    config_mod = importlib.import_module("app.configs.config")
    assert config_mod.config.ENVIRONMENT
    assert config_mod.config.MONGO_URI
    assert config_mod.config.DATABASE_NAME


def test_cors_config_is_importable():
    cors = importlib.import_module("app.config_cors")
    origins = cors.CORS_CONFIG["allow_origins"]
    assert origins, "CORS must allow at least the local dev origins"
    assert all(isinstance(o, str) for o in origins)
