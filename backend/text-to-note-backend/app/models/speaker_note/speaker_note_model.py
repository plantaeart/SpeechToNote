from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone


class SpeakerNoteBase(BaseModel):
    """Modèle de base pour une note de speaker"""
    title: str = Field(..., min_length=1, max_length=200, description="Titre de la note")
    content: str = Field(..., description="Contenu de la note")
    commands: List[str] = Field(default=[], description="Liste des commandes associées")


class SpeakerNoteCreate(SpeakerNoteBase):
    """Modèle pour la création d'une note"""
    pass


class SpeakerNoteUpdate(BaseModel):
    """Modèle pour la mise à jour d'une note"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    commands: Optional[List[str]] = None


class SpeakerNote(SpeakerNoteBase):
    """Modèle complet pour une note avec ID"""
    id_note: int = Field(..., description="Identifiant unique de la note")
    schema_version: str = Field(default="1.1.0", description="Version du schéma de données")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Date de création")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Date de dernière modification")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id_note": 1,
                "title": "Ma première note",
                "content": "Ceci est le contenu de ma note dictée vocalement",
                "commands": ["save", "export"],
                "schema_version": "1.1.0",
                "created_at": "2025-07-08T10:30:00Z",
                "updated_at": "2025-07-08T10:30:00Z"
            }
        }