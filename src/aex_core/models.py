"""Modèles de données pour le noyau AEX."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl


class ImageStatus(str, Enum):
    """Statut d'une image dans le pipeline d'ingestion."""

    PENDING = "pending"
    INGESTED = "ingested"
    FAILED = "failed"


class ImageCreate(BaseModel):
    """Payload d'ingestion minimal pour une image."""

    path: str = Field(..., min_length=1, description="Chemin source de l'image")
    size_bytes: int = Field(..., ge=0, description="Taille du fichier en octets")
    sha256: Optional[str] = Field(None, description="Empreinte SHA-256 si disponible")
    perceptual_hash: Optional[str] = Field(
        None, description="Empreinte perceptuelle (pHash) optionnelle"
    )
    source_url: Optional[HttpUrl] = Field(
        None, description="URL source si l'image provient d'un téléchargement"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "path": "/data/images/cat.png",
                    "size_bytes": 345678,
                    "sha256": "5f4dcc3b5aa765d61d8327deb882cf99",
                    "perceptual_hash": "ffd3a0c5a0f0c3f0",
                }
            ]
        }
    }


class ImageMetadata(BaseModel):
    """Représentation enrichie stockée côté noyau."""

    id: UUID = Field(default_factory=uuid4, description="Identifiant unique de l'image")
    path: str
    size_bytes: int
    status: ImageStatus = Field(default=ImageStatus.PENDING)
    sha256: Optional[str] = None
    perceptual_hash: Optional[str] = None
    source_url: Optional[HttpUrl] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "7b3f6b0a-6d6e-4cc5-9f17-763708b3ea2f",
                    "path": "/data/images/cat.png",
                    "size_bytes": 345678,
                    "status": "pending",
                    "created_at": "2025-10-17T12:34:56.123456+00:00",
                }
            ]
        },
    }


def build_metadata(payload: ImageCreate) -> ImageMetadata:
    """Crée une instance :class:`ImageMetadata` à partir d'un payload brut."""

    return ImageMetadata(**payload.model_dump())
