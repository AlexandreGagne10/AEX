"""Implémentations du dépôt d'images pour le noyau AEX."""

from __future__ import annotations

from typing import Dict, Iterable, Optional, Protocol
from uuid import UUID

from .models import ImageMetadata


class ImageRepository(Protocol):
    """Contrat minimal pour stocker les métadonnées d'images."""

    def add(self, metadata: ImageMetadata) -> ImageMetadata:
        """Persiste les métadonnées et les renvoie."""

    def get(self, image_id: UUID) -> Optional[ImageMetadata]:
        """Retourne une image par identifiant, ou ``None`` si introuvable."""

    def list(self) -> Iterable[ImageMetadata]:
        """Retourne un itérable de toutes les images connues."""

    def find_by_path(self, path: str) -> Optional[ImageMetadata]:
        """Retrouve une image à partir de son chemin source."""


class InMemoryImageRepository:
    """Stockage en mémoire pour prototyper l'API."""

    def __init__(self) -> None:
        self._items: Dict[UUID, ImageMetadata] = {}
        self._by_path: Dict[str, UUID] = {}

    def add(self, metadata: ImageMetadata) -> ImageMetadata:
        if metadata.path in self._by_path:
            existing = self._items[self._by_path[metadata.path]]
            return existing

        self._items[metadata.id] = metadata
        self._by_path[metadata.path] = metadata.id
        return metadata

    def get(self, image_id: UUID) -> Optional[ImageMetadata]:
        return self._items.get(image_id)

    def list(self) -> Iterable[ImageMetadata]:
        return list(self._items.values())

    def find_by_path(self, path: str) -> Optional[ImageMetadata]:
        identifier = self._by_path.get(path)
        if identifier is None:
            return None
        return self._items.get(identifier)


__all__ = ["ImageRepository", "InMemoryImageRepository"]
