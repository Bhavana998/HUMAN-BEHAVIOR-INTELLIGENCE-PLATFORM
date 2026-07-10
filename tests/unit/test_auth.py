import pytest
from fastapi.testclient import TestClient
from api.main import app
from database.session import SessionLocal
from core.security import get_password_hash

client = TestClient(app)


def test_register():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "test123",
            "full_name": "Test User",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"