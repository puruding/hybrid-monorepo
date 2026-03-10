"""Tests for main module."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


def test_health_check(client: TestClient) -> None:
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "copilot"


def test_chat(client: TestClient) -> None:
    """Test chat endpoint."""
    response = client.post(
        "/chat",
        json={
            "session_id": "session-001",
            "message": "What security incidents occurred today?",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "session-001"
    assert "response" in data
    assert "suggestions" in data
