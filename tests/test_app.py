from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient

from aex_core import create_app


def get_client() -> TestClient:
    app = create_app()
    return TestClient(app)


def test_ingest_image_creates_metadata() -> None:
    client = get_client()

    payload = {"path": "/tmp/image.png", "size_bytes": 123}
    response = client.post("/images", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["path"] == payload["path"]
    assert body["size_bytes"] == payload["size_bytes"]
    assert body["status"] == "ingested"
    assert UUID(body["id"])  # valide le format


def test_ingest_duplicate_returns_existing() -> None:
    client = get_client()
    payload = {"path": "/tmp/duplicate.png", "size_bytes": 55}

    first = client.post("/images", json=payload)
    second = client.post("/images", json=payload)

    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]


def test_get_image_returns_404_when_missing() -> None:
    client = get_client()
    missing_id = "5b160e38-0a61-4300-8f30-6fa0a37e0cfa"

    response = client.get(f"/images/{missing_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Image introuvable"


def test_list_images_returns_items() -> None:
    client = get_client()
    payload1 = {"path": "/tmp/a.png", "size_bytes": 1}
    payload2 = {"path": "/tmp/b.png", "size_bytes": 2}

    client.post("/images", json=payload1)
    client.post("/images", json=payload2)

    response = client.get("/images")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert {item["path"] for item in body} == {payload1["path"], payload2["path"]}
