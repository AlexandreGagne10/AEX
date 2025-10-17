"""Application FastAPI principale pour AEX."""

from __future__ import annotations

from fastapi import FastAPI

from .repository import InMemoryImageRepository
from .routes import router
from .service import ImageService


def create_app() -> FastAPI:
    """Instancie l'application FastAPI et ses dépendances."""

    app = FastAPI(
        title="AEX Core",
        version="0.1.0",
        summary="API noyau pour l'ingestion et la consultation de métadonnées d'images.",
    )

    repository = InMemoryImageRepository()
    image_service = ImageService(repository)
    app.state.image_service = image_service

    @app.get("/health", tags=["health"])  # pragma: no cover - trivial
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(router)
    return app


app = create_app()

__all__ = ["app", "create_app"]
