import pytest
import os
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import get_session
from app.config import settings

@pytest.fixture(name="session")
def session_fixture():
    # Use in-memory SQLite for tests to keep them fast
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session):
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="postgres_session")
def postgres_session_fixture():
    """PostgreSQL session fixture for integration tests"""
    # Use the actual PostgreSQL database for integration tests
    if settings.use_sqlite_fallback:
        # If fallback is enabled, use SQLite for testing
        engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
    else:
        # Use PostgreSQL for integration tests
        engine = create_engine(settings.database_url)

    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session