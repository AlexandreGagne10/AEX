"""Services applicatifs du noyau AEX."""

from __future__ import annotations

from typing import Iterable, Tuple
from uuid import UUID

from .models import ImageCreate, ImageMetadata, ImageStatus, build_metadata
from .repository import ImageRepository


class ImageService:
    """Encapsule la logique métier liée aux images."""

    def __init__(self, repository: ImageRepository) -> None:
        self._repository = repository

    def ingest(self, payload: ImageCreate) -> Tuple[ImageMetadata, bool]:
        """Ingest une image et indique si elle vient d'être créée."""

        existing = self._repository.find_by_path(payload.path)
        if existing:
            return existing, False

        metadata = build_metadata(payload)
        metadata.status = ImageStatus.INGESTED
        saved = self._repository.add(metadata)
        return saved, True

    def get(self, image_id: UUID) -> ImageMetadata | None:
        return self._repository.get(image_id)

    def list(self) -> Iterable[ImageMetadata]:
        return self._repository.list()
