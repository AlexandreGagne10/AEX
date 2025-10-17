"""Point d'entrée FastAPI pour le service noyau AEX."""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from .api import handle_aex_error, router
from .errors import AEXError


def create_app() -> FastAPI:
    app = FastAPI(
        title="AEX Core Service",
        version="0.1.0",
        description="Implémentation de référence des endpoints noyau (ingestion, configuration, jobs).",
    )
    app.include_router(router)
    app.add_exception_handler(AEXError, handle_aex_error)
    return app


app = create_app()


def run() -> None:
    """Lance un serveur Uvicorn de développement."""

    uvicorn.run("aex_service.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":  # pragma: no cover - uniquement pour le lancement manuel
    run()
