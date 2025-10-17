"""Définition des routes FastAPI pour le noyau AEX."""

from __future__ import annotations

from typing import Iterable
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from .models import ImageCreate, ImageMetadata
from .service import ImageService

router = APIRouter(prefix="/images", tags=["images"])


def get_image_service(request: Request) -> ImageService:
    service: ImageService = request.app.state.image_service
    return service


@router.post("", response_model=ImageMetadata, status_code=status.HTTP_201_CREATED)
async def ingest_image(
    payload: ImageCreate,
    response: Response,
    service: ImageService = Depends(get_image_service),
) -> ImageMetadata:
    metadata, created = service.ingest(payload)
    if not created:
        response.status_code = status.HTTP_200_OK
    return metadata


@router.get("/{image_id}", response_model=ImageMetadata)
async def get_image(
    image_id: UUID, service: ImageService = Depends(get_image_service)
) -> ImageMetadata:
    metadata = service.get(image_id)
    if metadata is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image introuvable")
    return metadata


@router.get("", response_model=list[ImageMetadata])
async def list_images(service: ImageService = Depends(get_image_service)) -> Iterable[ImageMetadata]:
    return list(service.list())


__all__ = ["router", "get_image_service"]
