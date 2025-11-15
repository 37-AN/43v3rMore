"""Tests for FastAPI endpoints."""

import pytest


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_get_signals_unauthorized(client):
    """Test signals endpoint without auth."""
    response = client.get("/api/v1/signals")
    assert response.status_code == 403  # No auth header
