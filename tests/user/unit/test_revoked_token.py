import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.cache_utils.user_cache import CachedUser
from app.core.dependencies import get_current_user


def _credentials() -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")


@pytest.mark.unit
def test_get_current_user_rejects_revoked_token_without_restoring_session(mocker):
    mocker.patch(
        "app.core.dependencies.decode_access_token",
        return_value={"sub": "1", "jti": "blocked-token"},
    )
    mocker.patch("app.core.dependencies.is_token_revoked", return_value=True)
    restore = mocker.patch("app.core.cache_utils.user_cache.cache_user_from_payload")

    with pytest.raises(HTTPException) as caught:
        get_current_user(_credentials())

    assert caught.value.status_code == 401
    assert caught.value.detail == "Token revoked"
    restore.assert_not_called()


@pytest.mark.unit
def test_get_current_user_rejects_missing_session_without_restoring_it(mocker):
    mocker.patch(
        "app.core.dependencies.decode_access_token",
        return_value={"sub": "1", "jti": "missing-session"},
    )
    mocker.patch("app.core.dependencies.is_token_revoked", return_value=False)
    mocker.patch("app.core.dependencies.get_cached_session", return_value=None)
    restore = mocker.patch("app.core.cache_utils.user_cache.cache_user_from_payload")

    with pytest.raises(HTTPException) as caught:
        get_current_user(_credentials())

    assert caught.value.status_code == 401
    restore.assert_not_called()


@pytest.mark.unit
def test_get_current_user_returns_session_when_jti_matches(mocker):
    cached = CachedUser(
        id=1,
        email="admin@test.com",
        full_name="Admin",
        company_id=10,
        role="admin",
        is_superuser=False,
        company_ids=[10],
        jti="active-token",
    )
    mocker.patch(
        "app.core.dependencies.decode_access_token",
        return_value={"sub": "1", "jti": "active-token"},
    )
    mocker.patch("app.core.dependencies.is_token_revoked", return_value=False)
    mocker.patch("app.core.dependencies.get_cached_session", return_value=cached)

    user = get_current_user(_credentials())

    assert user.id == 1
    assert user.jti == "active-token"


@pytest.mark.unit
def test_revoke_token_deletes_session_and_blocks_jti(mocker):
    mock_redis = mocker.patch("app.core.cache_utils.user_cache.redis_client")

    from app.core.cache_utils.user_cache import revoke_token

    revoke_token(1, "blocked-token")

    mock_redis.delete.assert_called_once_with("session:user:1")
    mock_redis.setex.assert_called_once()
    assert mock_redis.setex.call_args.args[0] == "revoked:jti:blocked-token"
