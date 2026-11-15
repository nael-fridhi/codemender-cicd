import pytest
from fastapi.testclient import TestClient

from app import db
from app.main import app


@pytest.fixture(autouse=True)
def temp_database(tmp_path, monkeypatch):
    test_db = tmp_path / "test_cloudvault.db"
    monkeypatch.setattr(db, "DEFAULT_DB_PATH", str(test_db))
    db.init_db(str(test_db))
    yield


def test_health_check():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_get_note():
    with TestClient(app) as client:
        create_resp = client.post(
            "/notes",
            json={
                "owner": "alice",
                "title": "Runbook",
                "content": "Rotate service account keys quarterly.",
            },
        )
        assert create_resp.status_code == 201
        created = create_resp.json()
        assert created["owner"] == "alice"
        assert created["title"] == "Runbook"

        get_resp = client.get(f"/notes/{created['id']}")
        assert get_resp.status_code == 200
        assert get_resp.json() == created


def test_list_notes_filters_by_owner():
    with TestClient(app) as client:
        client.post("/notes", json={"owner": "alice", "title": "A1", "content": "c1"})
        client.post("/notes", json={"owner": "bob", "title": "B1", "content": "c2"})

        resp = client.get("/notes", params={"owner": "alice"})
        assert resp.status_code == 200
        notes = resp.json()
        assert len(notes) == 1
        assert notes[0]["owner"] == "alice"
        assert notes[0]["title"] == "A1"


def test_get_missing_note_returns_404():
    with TestClient(app) as client:
        resp = client.get("/notes/99999")
    assert resp.status_code == 404
