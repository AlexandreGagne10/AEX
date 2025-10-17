"""Routes FastAPI exposant les services noyau d'AEX."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Body, Depends, Path, status
from fastapi.responses import JSONResponse

from .errors import AEXError
from .models import (
    ConfigDocument,
    ConfigResponse,
    ErrorEnvelope,
    IngestRequest,
    IngestResponse,
    JobRequest,
    JobResponse,
)
from .repository import InMemoryRepository, repository

router = APIRouter()


def get_repository() -> InMemoryRepository:
    return repository


@router.post(
    "/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {"model": ErrorEnvelope},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorEnvelope},
    },
)
def ingest_media(
    request: IngestRequest,
    repo: InMemoryRepository = Depends(get_repository),
) -> IngestResponse:
    image = repo.register_ingest(
        path=request.path,
        source=request.source,
        ingest_options=request.ingest_options.model_dump() if request.ingest_options else None,
    )
    return IngestResponse(
        image_id=image.image_id,
        status=image.status,
        ingested_at=image.ingested_at,
    )


@router.put(
    "/config/{namespace}",
    response_model=ConfigResponse,
    status_code=status.HTTP_200_OK,
)
def put_config(
    *,
    namespace: str = Path(..., min_length=1, max_length=64),
    document: ConfigDocument,
    repo: InMemoryRepository = Depends(get_repository),
) -> ConfigResponse:
    stored = repo.save_config(
        namespace=namespace,
        document=document.document,
        updated_by=document.updated_by,
    )
    return ConfigResponse(
        namespace=stored.namespace,
        document=stored.document,
        version=stored.version,
        updated_at=stored.updated_at,
        updated_by=stored.updated_by,
    )


@router.get(
    "/config/{namespace}",
    response_model=ConfigResponse,
    responses={status.HTTP_404_NOT_FOUND: {"model": ErrorEnvelope}},
)
def get_config(
    *,
    namespace: str = Path(..., min_length=1, max_length=64),
    repo: InMemoryRepository = Depends(get_repository),
) -> ConfigResponse:
    stored = repo.get_config(namespace)
    return ConfigResponse(
        namespace=stored.namespace,
        document=stored.document,
        version=stored.version,
        updated_at=stored.updated_at,
        updated_by=stored.updated_by,
    )


@router.post(
    "/jobs",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorEnvelope}},
)
def post_job(
    request: JobRequest = Body(...),
    repo: InMemoryRepository = Depends(get_repository),
) -> JobResponse:
    schedule_at: datetime | None = request.schedule_at
    job = repo.enqueue_job(
        job_type=request.type,
        payload=request.payload,
        priority=request.priority,
        schedule_at=schedule_at,
    )
    return JobResponse(
        job_id=job.job_id,
        status=job.status,
        priority=job.priority,
        schedule_at=job.schedule_at,
    )


async def handle_aex_error(_: Any, exc: AEXError):
    return JSONResponse(status_code=exc.status_code, content=exc.as_payload())


__all__ = ["router", "get_repository", "handle_aex_error"]
