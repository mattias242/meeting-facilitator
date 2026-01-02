"""Test configuration and shared fixtures."""

import pytest
from collections.abc import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.main import app
from app.db.session import Base, get_db


# Test database (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session")
def db() -> Generator[Session, None, None]:
    """Create test database session."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create test client with database override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_idoarrt_markdown() -> str:
    """Sample IDOARRT markdown for testing."""
    return """# Testmöte

# Intent
Testa mötesfacilitering

# Desired Outcomes
- Testa systemet
- Verifiera funktioner

# Agenda
1. Introduktion (5 min)
2. Demo (10 min)
3. Diskussion (15 min)

# Roles
- Facilitator: Anna
- Notetaker: Björn

# Rules
- Håll tider
- En person i taget

# Time
Total: 30 minutes"""
