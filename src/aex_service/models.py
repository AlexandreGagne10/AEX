"""Modèles Pydantic décrivant les contrats REST du service AEX."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator


class ErrorResponse(BaseModel):
    code: str
    message: str
    retryable: bool
    details: Optional[Dict[str, Any]] = None


class ErrorEnvelope(BaseModel):
    error: ErrorResponse


class IngestOptions(BaseModel):
    generate_thumbnail: bool = Field(default=False, description="Déclenche la génération de miniatures.")


class IngestRequest(BaseModel):
    path: str = Field(..., min_length=3, description="Chemin complet du média à ingérer.")
    source: str = Field(..., min_length=1, max_length=64, description="Origine déclarée de l'ingestion.")
    ingest_options: IngestOptions | None = Field(default=None)

    @field_validator("path")
    def validate_path(cls, value: str) -> str:
        if "//" not in value:
            raise ValueError("Le chemin doit contenir un schéma explicite (ex: s3://bucket/key.jpg).")
        return value


class IngestResponse(BaseModel):
    image_id: str
    status: str
    ingested_at: datetime


class ConfigDocument(BaseModel):
    document: Dict[str, Any]
    updated_by: str = Field(..., min_length=1, max_length=64)


class ConfigResponse(BaseModel):
    namespace: str
    document: Dict[str, Any]
    version: int
    updated_at: datetime
    updated_by: str


class JobRequest(BaseModel):
    type: str
    payload: Dict[str, Any]
    priority: str = Field("NORMAL", description="Priorité du job.")
    schedule_at: Optional[datetime] = Field(default=None)

    @field_validator("priority")
    def validate_priority(cls, value: str) -> str:
        allowed = {"LOW", "NORMAL", "HIGH"}
        if value not in allowed:
            raise ValueError(f"La priorité doit être l'une de {sorted(allowed)}.")
        return value


class JobResponse(BaseModel):
    job_id: str
    status: str
    priority: str
    schedule_at: Optional[datetime]
