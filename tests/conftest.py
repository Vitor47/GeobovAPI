import os
from collections.abc import Generator
from unittest.mock import Mock

import mongomock
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.adapters.models import Cattle, Company
from app.core.database import Base
from app.domain.enums.role_enum import RoleEnum

# Set test environment variables before importing app modules.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("REDIS_DB", "0")
os.environ.setdefault("SESSION_CACHE_TTL_SECONDS", "86400")
os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("MONGO_DB_NAME", "cow_track_test")
os.environ.setdefault("TELEMETRY_RAW_RETENTION_DAYS", "30")
os.environ.setdefault("TELEMETRY_HISTORY_INTERVAL_MINUTES", "30")
os.environ.setdefault("ADMIN_ENABLED", "false")
os.environ.setdefault("APP_ENV", "local")
os.environ.setdefault("APP_PORT", "8000")
os.environ.setdefault("SUPERUSER_EMAIL", "admin@example.com")
os.environ.setdefault("SUPERUSER_PASSWORD", "changeme")
os.environ.setdefault("SUPERUSER_FULL_NAME", "Super Admin")


@pytest.fixture
def db_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(db_engine) -> Generator[Session, None, None]:
    session_factory = sessionmaker(bind=db_engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def mongo_db():
    client = mongomock.MongoClient()
    yield client["cow_track_test"]
    client.close()


@pytest.fixture
def seeded_company(db_session) -> Company:
    company = Company(name="Test Company")
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


@pytest.fixture
def seeded_cattle(db_session, seeded_company) -> Cattle:
    cattle = Cattle(tag="TAG-001", company_id=seeded_company.id, name="Cattle 1")
    db_session.add(cattle)
    db_session.commit()
    db_session.refresh(cattle)
    return cattle


@pytest.fixture
def mock_admin_user():
    user = Mock()
    user.id = 1
    user.company_id = 1
    user.company_ids = [1]
    user.full_name = "Admin User"
    user.email = "admin@test.com"
    user.is_superuser = False
    user.role = RoleEnum.ADMIN
    return user
