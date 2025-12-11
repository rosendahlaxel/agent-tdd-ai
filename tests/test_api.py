import pytest
from fastapi.testclient import TestClient

from app.main import app, reset_state

client = TestClient(app)


@pytest.fixture(autouse=True)
def _reset_state():
    reset_state()


def test_health_endpoint_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_item_requires_min_length_name():
    response = client.post("/items", json={"name": "hi"})
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"].startswith("Name must be at least")


def test_create_item_returns_created_item():
    response = client.post("/items", json={"name": "Widget"})
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Widget"
    assert body["id"] == 1


def test_get_item_by_id_returns_item():
    client.post("/items", json={"name": "Gadget"})
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Gadget"}


def test_get_item_missing_returns_404():
    response = client.get("/items/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_list_items_returns_all():
    client.post("/items", json={"name": "First"})
    client.post("/items", json={"name": "Second"})
    response = client.get("/items")
    assert response.status_code == 200
    names = [item["name"] for item in response.json()]
    assert names == ["First", "Second"]

def test_list_items_returns_empty_list():
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == []


def test_delete_item_removes_item():
    client.post("/items", json={"name": "ToDelete"})
    response = client.delete("/items/1")
    assert response.status_code == 204
    get_response = client.get("/items/1")
    assert get_response.status_code == 404


def test_delete_item_missing_returns_404():
    response = client.delete("/items/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}

def test_delete_item_missing_is_idempotent():
    response = client.delete("/items/999")
    assert response.status_code == 204
    assert response.text == ""


def test_ids_increment_with_multiple_creations():
    first = client.post("/items", json={"name": "One"})
    second = client.post("/items", json={"name": "Two"})
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == 1
    assert second.json()["id"] == 2


def test_update_item_changes_name():
    client.post("/items", json={"name": "Original"})
    response = client.put("/items/1", json={"name": "Updated"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Updated"}

def test_create_item_trims_whitespace():
    response = client.post("/items", json={"name": "   Widget   "})
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Widget"


def test_update_item_creates_when_missing():
    response = client.put("/items/5", json={"name": "Created via update"})
    assert response.status_code == 201
    assert response.json() == {"id": 5, "name": "Created via update"}


def test_update_item_trims_whitespace():
    client.post("/items", json={"name": "Needs Trim"})
    response = client.put("/items/1", json={"name": "   Trimmed Name   "})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Trimmed Name"}


def test_create_item_rejects_duplicate_names():
    client.post("/items", json={"name": "Unique"})
    response = client.post("/items", json={"name": "Unique"})
    assert response.status_code == 409
    assert response.json()["detail"].lower().startswith("name already exists")


def test_reset_endpoint_clears_items():
    client.post("/items", json={"name": "First"})
    client.post("/items", json={"name": "Second"})
    reset_response = client.post("/reset")
    assert reset_response.status_code == 204

    list_response = client.get("/items")
    assert list_response.status_code == 200
    assert list_response.json() == []
