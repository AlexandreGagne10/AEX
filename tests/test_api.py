from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from aex_service.api import get_repository
from aex_service.main import create_app
from aex_service.repository import InMemoryRepository


@pytest.fixture()
def client() -> TestClient:
    app = create_app()
    repo = InMemoryRepository()
    app.dependency_overrides[get_repository] = lambda: repo
    app.state.test_repo = repo
    return TestClient(app)


def test_ingest_media_success(client: TestClient) -> None:
    response = client.post(
        "/ingest",
        json={
            "path": "s3://bucket/image.jpg",
            "source": "batch-import",
            "ingest_options": {"generate_thumbnail": True},
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "PENDING_HASH"
    assert "image_id" in payload
    assert "ingested_at" in payload


def test_ingest_media_duplicate(client: TestClient) -> None:
    body = {
        "path": "s3://bucket/duplicate.jpg",
        "source": "api",
    }
    first = client.post("/ingest", json=body)
    assert first.status_code == 201
    second = client.post("/ingest", json=body)
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "INGEST_DUPLICATE"


def test_put_and_get_config(client: TestClient) -> None:
    put_resp = client.put(
        "/config/vector",
        json={
            "document": {"dim": 512, "model": "clip"},
            "updated_by": "integration-test",
        },
    )
    assert put_resp.status_code == 200
    payload = put_resp.json()
    assert payload["version"] == 1
    get_resp = client.get("/config/vector")
    assert get_resp.status_code == 200
    assert get_resp.json()["document"] == {"dim": 512, "model": "clip"}


def test_get_config_missing_returns_404(client: TestClient) -> None:
    response = client.get("/config/unknown")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CONFIG_NOT_FOUND"


def test_enqueue_job_success(client: TestClient) -> None:
    schedule = datetime.now(tz=timezone.utc) + timedelta(minutes=5)
    response = client.post(
        "/jobs",
        json={
            "type": "embedding",
            "payload": {"image_id": "uuid", "embedding_kind": "clip"},
            "priority": "HIGH",
            "schedule_at": schedule.isoformat(),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "queued"
    assert data["priority"] == "HIGH"
    returned = datetime.fromisoformat(data["schedule_at"])
    delta = abs((returned - schedule).total_seconds())
    assert delta < 1


def test_enqueue_job_with_past_schedule_rejected(client: TestClient) -> None:
    past = datetime.now(tz=timezone.utc) - timedelta(minutes=1)
    response = client.post(
        "/jobs",
        json={
            "type": "embedding",
            "payload": {"image_id": "uuid"},
            "schedule_at": past.isoformat(),
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_SCHEDULE"


def test_pull_next_job_returns_204_when_queue_empty(client: TestClient) -> None:
    response = client.post("/jobs/next", params={"type": "embedding"})
    assert response.status_code == 204


def test_pull_next_job_respects_priority(client: TestClient) -> None:
    low = client.post(
        "/jobs",
        json={
            "type": "embedding",
            "payload": {"image_id": "low"},
            "priority": "LOW",
        },
    )
    assert low.status_code == 201
    high = client.post(
        "/jobs",
        json={
            "type": "embedding",
            "payload": {"image_id": "high"},
            "priority": "HIGH",
        },
    )
    assert high.status_code == 201
    first = client.post("/jobs/next", params={"type": "embedding"})
    assert first.status_code == 200
    payload = first.json()
    assert payload["job_id"] == high.json()["job_id"]
    assert payload["payload"] == {"image_id": "high"}
    assert payload["status"] == "dispatched"
    second = client.post("/jobs/next", params={"type": "embedding"})
    assert second.status_code == 200
    assert second.json()["job_id"] == low.json()["job_id"]
    final = client.post("/jobs/next", params={"type": "embedding"})
    assert final.status_code == 204


def test_pull_next_job_skips_future_schedule(client: TestClient) -> None:
    schedule = datetime.now(tz=timezone.utc) + timedelta(minutes=10)
    response = client.post(
        "/jobs",
        json={
            "type": "embedding",
            "payload": {"image_id": "future"},
            "schedule_at": schedule.isoformat(),
        },
    )
    assert response.status_code == 201
    pull = client.post("/jobs/next", params={"type": "embedding"})
    assert pull.status_code == 204
