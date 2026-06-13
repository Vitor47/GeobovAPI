import os
from collections.abc import Generator
from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.adapters.models.cattle  # noqa: F401  # pylint: disable=unused-import
import app.adapters.models.device  # noqa: F401  # pylint: disable=unused-import
import app.adapters.models.role  # noqa: F401  # pylint: disable=unused-import
import app.adapters.models.user  # noqa: F401  # pylint: disable=unused-import
from app.adapters.models.cattle import Cattle
from app.adapters.models.company import Company
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
def seeded_company(db_session) -> Company:
    company = Company(name="Test Company")
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


@pytest.fixture
def seeded_cattle(db_session, seeded_company) -> Cattle:
    cattle = Cattle(tag="TAG-001", company_id=seeded_company.id)
    db_session.add(cattle)
    db_session.commit()
    db_session.refresh(cattle)
    return cattle


@pytest.fixture
def mock_admin_user():
    user = Mock()
    user.id = 1
    user.company_id = 1
    user.full_name = "Admin User"
    user.email = "admin@test.com"
    user.is_superuser = False
    user.role = RoleEnum.ADMIN
    return user
