from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class SpeakerNoteCreate(BaseModel):
    """Modèle pour la création d'une note"""
    title: str = Field(..., min_length=1, max_length=200, description="Titre de la note")
    content: str = Field(..., description="Contenu de la note")
    commands: Optional[List[str]] = Field(default=[], description="Liste des commandes associées")


class SpeakerNoteUpdate(BaseModel):
    """Modèle pour la mise à jour d'une note"""
    id_note: int = Field(..., description="Identifiant unique de la note")
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    commands: Optional[List[str]] = None


class SpeakerNote(BaseModel):
    """Modèle complet pour une note avec ID"""
    id_note: Optional[int] = Field(None, description="Identifiant unique de la note")
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Titre de la note")
    content: Optional[str] = Field(None, description="Contenu de la note")
    commands: Optional[List[str]] = Field(None, description="Liste des commandes associées")
    schema_version: Optional[str] = Field(default="1.0.0", description="Version du schéma de données")
    created_at: Optional[datetime] = Field(None, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de dernière modification")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "title": "Ma première note",
                "content": "Ceci est le contenu de ma note dictée vocalement",
            }
        }