import asyncio

import pytest
from starlette.requests import Request

from app.bootstrap.admin.auth import AdminAuth


def _make_request(session: dict | None = None) -> Request:
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/admin/login",
        "headers": [],
        "session": session if session is not None else {},
    }
    return Request(scope)


@pytest.mark.unit
def test_admin_auth_login_succeeds_for_superuser(mocker):
    user = mocker.Mock()
    user.id = 1
    user.email = "admin@example.com"
    user.is_superuser = True
    user.authenticate.return_value = True

    db = mocker.Mock()
    db.query.return_value.filter.return_value.first.return_value = user
    mocker.patch(
        "app.bootstrap.admin.auth.SessionFactory.create",
        return_value=db,
    )

    request = _make_request()

    async def fake_form():
        return {"username": "admin@example.com", "password": "changeme"}

    request.form = fake_form  # type: ignore[method-assign]

    auth = AdminAuth(secret_key="test-secret")
    assert asyncio.run(auth.login(request)) is True
    assert request.session["admin_user_id"] == 1
    assert request.session["admin_email"] == "admin@example.com"
    db.close.assert_called_once()


@pytest.mark.unit
def test_admin_auth_login_rejects_non_superuser(mocker):
    user = mocker.Mock()
    user.is_superuser = False
    user.authenticate.return_value = True

    db = mocker.Mock()
    db.query.return_value.filter.return_value.first.return_value = user
    mocker.patch(
        "app.bootstrap.admin.auth.SessionFactory.create",
        return_value=db,
    )

    request = _make_request()

    async def fake_form():
        return {"username": "farmer@example.com", "password": "secret"}

    request.form = fake_form  # type: ignore[method-assign]

    auth = AdminAuth(secret_key="test-secret")
    assert asyncio.run(auth.login(request)) is False


@pytest.mark.unit
def test_admin_auth_authenticate_clears_session_when_user_lost_superuser(mocker):
    user = mocker.Mock()
    user.is_superuser = False

    db = mocker.Mock()
    db.query.return_value.filter.return_value.first.return_value = user
    mocker.patch(
        "app.bootstrap.admin.auth.SessionFactory.create",
        return_value=db,
    )

    request = _make_request(session={"admin_user_id": 1})
    auth = AdminAuth(secret_key="test-secret")

    assert asyncio.run(auth.authenticate(request)) is False
    assert request.session == {}
