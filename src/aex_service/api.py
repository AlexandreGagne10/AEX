"""Routes FastAPI exposant les services noyau d'AEX."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Body, Depends, Path, Query, Response, status
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
    JobLeaseResponse,
    HealthResponse,
)
from .repository import InMemoryRepository, repository

router = APIRouter()


def get_repository() -> InMemoryRepository:
    return repository


@router.get("/health", response_model=HealthResponse)
def read_health() -> HealthResponse:
    """Expose un diagnostic léger pour la supervision."""

    return HealthResponse(status="ok", service="aex-core", timestamp=datetime.now(tz=timezone.utc))


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


@router.post(
    "/jobs/next",
    response_model=JobLeaseResponse,
    responses={status.HTTP_204_NO_CONTENT: {"description": "Aucun job disponible"}},
)
def pull_next_job(
    *,
    job_type: str = Query(..., alias="type", min_length=1, max_length=64),
    repo: InMemoryRepository = Depends(get_repository),
) -> JobLeaseResponse | Response:
    job = repo.lease_next_job(job_type=job_type)
    if job is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return JobLeaseResponse(
        job_id=job.job_id,
        type=job.type,
        payload=job.payload,
        priority=job.priority,
        schedule_at=job.schedule_at,
        status=job.status,
        leased_at=job.leased_at,
    )


async def handle_aex_error(_: Any, exc: AEXError):
    return JSONResponse(status_code=exc.status_code, content=exc.as_payload())


__all__ = ["router", "get_repository", "handle_aex_error"]
