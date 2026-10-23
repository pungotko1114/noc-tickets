import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:   # "with" runs startup, which creates the table
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_ticket(client):
    r = client.post("/tickets", json={"title": "ONT offline", "site": "MNL-01"})
    assert r.status_code == 201
    assert r.json()["priority"] == "P3"