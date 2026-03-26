import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Marketing Service"


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Marketing Service API"


def test_list_campaigns():
    response = client.get("/api/v1/campaigns")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_campaign_by_id():
    response = client.get("/api/v1/campaigns/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1


def test_get_nonexistent_campaign():
    response = client.get("/api/v1/campaigns/9999")
    assert response.status_code == 404


def test_create_campaign():
    payload = {
        "name": "Test Campaign",
        "description": "A test campaign",
        "budget": 5000.0,
        "start_date": "2025-09-01",
        "end_date": "2025-12-31",
        "target_audience": "Test audience",
    }
    response = client.post("/api/v1/campaigns", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Campaign"
    assert data["status"] == "draft"


def test_filter_campaigns_by_status():
    response = client.get("/api/v1/campaigns?status=active")
    assert response.status_code == 200
    data = response.json()
    for campaign in data:
        assert campaign["status"] == "active"


def test_list_users():
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_user():
    payload = {
        "name": "Test User",
        "email": "testuser@example.com",
        "phone": "+1-555-9999",
        "campaign_id": 1,
    }
    response = client.post("/api/v1/users", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"
    assert data["subscribed"] is True


def test_get_stats():
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for stat in data:
        assert "campaign_id" in stat
        assert "total_users" in stat
        assert "budget" in stat
