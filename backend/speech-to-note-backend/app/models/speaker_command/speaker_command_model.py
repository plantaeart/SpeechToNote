from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SpeakerCommandCreate(BaseModel):
    """Modèle pour la création d'une commande"""
    command_name: str = Field(..., min_length=1, max_length=100, description="Nom de la commande")
    command_vocal: List[str] = Field(..., description="Liste des commandes vocales")
    command_description: Optional[str] = Field(None, description="Description de la commande")
    html_tag_start: Optional[str] = Field(None, max_length=50, description="Balise HTML de début")
    html_tag_end: Optional[str] = Field(None, max_length=50, description="Balise HTML de fin")


class SpeakerCommandUpdate(BaseModel):
    """Modèle pour la mise à jour d'une commande"""
    id_command: int = Field(..., description="Identifiant unique de la commande")
    command_name: Optional[str] = Field(None, min_length=1, max_length=100)
    command_vocal: Optional[List[str]] = Field(None, description="Liste des commandes vocales")
    command_description: Optional[str] = None
    html_tag_start: Optional[str] = Field(None, max_length=50, description="Balise HTML de début")
    html_tag_end: Optional[str] = Field(None, max_length=50, description="Balise HTML de fin")


class SpeakerCommand(BaseModel):
    """Modèle complet pour une commande avec ID"""
    id_command: Optional[int] = Field(None, description="Identifiant unique de la commande")
    command_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nom de la commande")
    command_vocal: Optional[List[str]] = Field(None, description="Liste des commandes vocales")
    command_description: Optional[str] = Field(None, description="Description de la commande")
    html_tag_start: Optional[str] = Field(None, description="Balise HTML de début")
    html_tag_end: Optional[str] = Field(None, description="Balise HTML de fin")
    schema_version: Optional[str] = Field(default="1.0.1", description="Version du schéma de données")
    created_at: Optional[datetime] = Field(None, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de dernière modification")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "command_name": "titre",
                "command_vocal": ["titre", "titres"],
                "command_description": "Formate le texte suivant comme un titre principal",
                "html_tag_start": "<h1>",
                "html_tag_end": "</h1>",
            }
        }
