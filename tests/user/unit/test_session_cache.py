import json
from unittest.mock import Mock

import pytest

from app.core.cache_utils.user_cache import (
    cache_user_from_payload,
    get_cached_session,
    invalidate_user_session,
)
from app.core.security import build_token_payload


@pytest.mark.unit
def test_build_token_payload_includes_company_and_superuser(mocker):
    user = Mock()
    user.id = 1
    user.email = "admin@test.com"
    user.full_name = "Admin"
    user.company_id = 10
    user.company_ids = [10, 20]
    user.is_superuser = True
    user.role = Mock()
    user.role.name = "admin"

    payload = build_token_payload(user)

    assert payload["sub"] == "1"
    assert payload["company_id"] == 10
    assert payload["company_ids"] == [10, 20]
    assert payload["is_superuser"] is True
    assert payload["role"] == "admin"


@pytest.mark.unit
def test_get_cached_session_returns_user_when_session_exists(mocker):
    user_data = {
        "id": 1,
        "email": "admin@test.com",
        "full_name": "Admin",
        "company_id": 10,
        "company_ids": [10, 20],
        "role": "admin",
        "is_superuser": False,
    }
    mocker.patch(
        "app.core.cache_utils.user_cache.redis_client.get",
        return_value=json.dumps(user_data),
    )

    cached = get_cached_session(1)

    assert cached.id == 1
    assert cached.company_id == 10
    assert cached.company_ids == [10, 20]
    assert cached.role == "admin"


@pytest.mark.unit
def test_cache_user_from_payload_stores_session(mocker):
    mock_redis = mocker.patch("app.core.cache_utils.user_cache.redis_client")
    payload = {
        "sub": "1",
        "email": "admin@test.com",
        "full_name": "Admin",
        "company_id": 10,
        "company_ids": [10, 20],
        "role": "admin",
        "is_superuser": False,
    }

    user = cache_user_from_payload(payload)

    assert user.email == "admin@test.com"
    assert user.company_ids == [10, 20]
    mock_redis.setex.assert_called_once()


@pytest.mark.unit
def test_invalidate_user_session_deletes_cache(mocker):
    mock_redis = mocker.patch("app.core.cache_utils.user_cache.redis_client")

    invalidate_user_session(1)

    mock_redis.delete.assert_called_once_with("session:user:1")
