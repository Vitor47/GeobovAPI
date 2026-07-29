from collections.abc import Generator
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import get_current_user
from app.domain.enums.role_enum import RoleEnum
from app.main import create_app


@pytest.fixture(scope="session")
def app():
    return create_app()


@pytest.fixture
def client(app) -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


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


@pytest.fixture
def authenticated_client(app, mock_admin_user) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_current_user] = lambda: mock_admin_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
