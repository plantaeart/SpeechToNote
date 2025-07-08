from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SpeakerCommandBase(BaseModel):
    """Modèle de base pour une commande de speaker"""
    command_name: str = Field(..., min_length=1, max_length=100, description="Nom de la commande")
    command_vocal: str = Field(..., min_length=1, max_length=200, description="Commande vocale")
    command_description: Optional[str] = Field(None, description="Description de la commande")

class SpeakerCommandUpdate(BaseModel):
    """Modèle pour la mise à jour d'une commande"""
    id_command: int = Field(..., description="Identifiant unique de la commande")
    command_name: Optional[str] = Field(None, min_length=1, max_length=100)
    command_vocal: Optional[str] = Field(None, min_length=1, max_length=200)
    command_description: Optional[str] = None


class SpeakerCommand(SpeakerCommandBase):
    """Modèle complet pour une commande avec ID"""
    id_command: Optional[int] = Field(None, description="Identifiant unique de la commande")
    schema_version: Optional[str] = Field(default="1.0.0", description="Version du schéma de données")
    created_at: Optional[datetime] = Field(None, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de dernière modification")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "command_name": "save_note",
                "command_vocal": "sauvegarder la note",
                "command_description": "Sauvegarde la note en cours dans la base de données",
            }
        }
