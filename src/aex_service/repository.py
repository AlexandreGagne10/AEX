"""Implémentations en mémoire simulant le stockage du noyau AEX."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Dict
from uuid import uuid4

from .errors import ConfigNotFoundError, DuplicateIngestError, InvalidScheduleError


@dataclass
class IngestedImage:
    image_id: str
    path: str
    source: str
    status: str
    ingested_at: datetime
    ingest_options: Dict[str, Any]


@dataclass
class StoredConfig:
    namespace: str
    document: Dict[str, Any]
    version: int
    updated_at: datetime
    updated_by: str


@dataclass
class StoredJob:
    job_id: str
    type: str
    payload: Dict[str, Any]
    priority: str
    schedule_at: datetime | None
    enqueued_at: datetime
    status: str = field(default="queued")
    leased_at: datetime | None = None


class InMemoryRepository:
    """Stocke les données dans des structures Python en mémoire."""

    def __init__(self) -> None:
        self._images_by_path: Dict[str, IngestedImage] = {}
        self._configs: Dict[str, StoredConfig] = {}
        self._jobs: Dict[str, StoredJob] = {}
        self._lock = Lock()

    def register_ingest(self, *, path: str, source: str, ingest_options: Dict[str, Any] | None) -> IngestedImage:
        options = ingest_options or {}
        with self._lock:
            if path in self._images_by_path:
                raise DuplicateIngestError(path)
            image = IngestedImage(
                image_id=str(uuid4()),
                path=path,
                source=source,
                status="PENDING_HASH",
                ingested_at=datetime.now(tz=timezone.utc),
                ingest_options=options,
            )
            self._images_by_path[path] = image
            return image

    def save_config(self, *, namespace: str, document: Dict[str, Any], updated_by: str) -> StoredConfig:
        with self._lock:
            previous = self._configs.get(namespace)
            version = (previous.version + 1) if previous else 1
            stored = StoredConfig(
                namespace=namespace,
                document=document,
                version=version,
                updated_at=datetime.now(tz=timezone.utc),
                updated_by=updated_by,
            )
            self._configs[namespace] = stored
            return stored

    def get_config(self, namespace: str) -> StoredConfig:
        config = self._configs.get(namespace)
        if not config:
            raise ConfigNotFoundError(namespace)
        return config

    def enqueue_job(
        self,
        *,
        job_type: str,
        payload: Dict[str, Any],
        priority: str,
        schedule_at: datetime | None,
    ) -> StoredJob:
        now = datetime.now(tz=timezone.utc)
        if schedule_at is not None:
            if schedule_at.tzinfo is None:
                schedule_at = schedule_at.replace(tzinfo=timezone.utc)
            if schedule_at < now:
                raise InvalidScheduleError()
        with self._lock:
            job = StoredJob(
                job_id=str(uuid4()),
                type=job_type,
                payload=payload,
                priority=priority,
                schedule_at=schedule_at,
                enqueued_at=now,
            )
            self._jobs[job.job_id] = job
            return job

    def lease_next_job(self, *, job_type: str) -> StoredJob | None:
        """Retourne le prochain job prêt pour le type demandé."""

        now = datetime.now(tz=timezone.utc)
        priority_order = {"HIGH": 0, "NORMAL": 1, "LOW": 2}
        with self._lock:
            candidates = [
                job
                for job in self._jobs.values()
                if job.type == job_type
                and job.status == "queued"
                and (job.schedule_at is None or job.schedule_at <= now)
            ]
            if not candidates:
                return None
            candidates.sort(
                key=lambda job: (
                    priority_order.get(job.priority, 1),
                    job.schedule_at or job.enqueued_at,
                    job.enqueued_at,
                )
            )
            job = candidates[0]
            job.status = "dispatched"
            job.leased_at = now
            return job


repository = InMemoryRepository()
"""Instance globale simple pour usage dans l'application FastAPI."""
