import os

# Must be set before importing the app, so tests never touch the real database.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key-for-automated-tests-0123456789"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models  # noqa: F401  (registers the tables)
from database import Base, get_db
from main import app


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def make_user(client):
    """Register a user, log in, and return the auth headers."""

    def _make_user(email="user@example.com", password="password123"):
        client.post("/auth/register", json={"email": email, "password": password})
        response = client.post(
            "/auth/login", data={"username": email, "password": password}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _make_user
