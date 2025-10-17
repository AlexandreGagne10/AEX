"""Définition des erreurs applicatives normalisées pour AEX."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class AEXError(Exception):
    """Exception applicative mappée sur le format d'erreur AEX."""

    code: str
    message: str
    status_code: int = 400
    retryable: bool = False
    details: Dict[str, Any] | None = None

    def as_payload(self) -> Dict[str, Any]:
        """Retourne la représentation JSON de l'erreur."""

        payload: Dict[str, Any] = {
            "error": {
                "code": self.code,
                "message": self.message,
                "retryable": self.retryable,
            }
        }
        if self.details:
            payload["error"]["details"] = self.details
        return payload


class DuplicateIngestError(AEXError):
    def __init__(self, path: str) -> None:
        super().__init__(
            code="INGEST_DUPLICATE",
            message=f"Une image est déjà enregistrée pour le chemin '{path}'.",
            status_code=409,
            retryable=False,
        )


class ConfigNotFoundError(AEXError):
    def __init__(self, namespace: str) -> None:
        super().__init__(
            code="CONFIG_NOT_FOUND",
            message=f"Aucune configuration trouvée pour l'espace de noms '{namespace}'.",
            status_code=404,
            retryable=False,
        )


class InvalidScheduleError(AEXError):
    def __init__(self) -> None:
        super().__init__(
            code="INVALID_SCHEDULE",
            message="L'horodatage fourni pour 'schedule_at' est antérieur à l'heure courante.",
            status_code=422,
            retryable=False,
        )
