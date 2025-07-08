import os

# MongoDB Configuration for Docker Development
# Use host.docker.internal to connect to host machine from Docker container
MONGO_URI = os.getenv("MONGO_URI", "mongodb://host.docker.internal:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "speech_to_note")
COLLECTIONS = [
    "SPEAKER_NOTES",
    "COMMANDS",
]