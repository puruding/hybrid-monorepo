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
    assert data["service"] == "triage"


def test_triage_incident(client: TestClient) -> None:
    """Test triage endpoint."""
    response = client.post(
        "/triage",
        json={
            "incident_id": "INC-001",
            "description": "Suspicious login detected",
            "severity": "high",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["incident_id"] == "INC-001"
    assert "classification" in data
    assert "confidence" in data
    assert "recommended_actions" in data
