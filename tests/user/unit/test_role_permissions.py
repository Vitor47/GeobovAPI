import pytest

from app.domain.auth.role_permissions import user_has_permission
from app.domain.enums.permission_enum import PermissionEnum
from app.domain.enums.role_enum import RoleEnum


@pytest.mark.unit
@pytest.mark.parametrize(
    ("role", "permission", "expected"),
    [
        (RoleEnum.ADMIN, PermissionEnum.CATTLE_CREATE, True),
        (RoleEnum.MANAGER, PermissionEnum.CATTLE_CREATE, False),
        (RoleEnum.VIEWER, PermissionEnum.CATTLE_CREATE, False),
        (RoleEnum.MANAGER, PermissionEnum.CATTLE_READ, True),
        (RoleEnum.VIEWER, PermissionEnum.CATTLE_READ, True),
        (RoleEnum.MANAGER, PermissionEnum.CATTLE_UPDATE, True),
        (RoleEnum.VIEWER, PermissionEnum.CATTLE_UPDATE, False),
        (RoleEnum.MANAGER, PermissionEnum.USER_CREATE, False),
        (RoleEnum.ADMIN, PermissionEnum.USER_CREATE, True),
        (RoleEnum.MANAGER, PermissionEnum.DEVICE_CREATE, False),
        (RoleEnum.MANAGER, PermissionEnum.DEVICE_READ, False),
        (RoleEnum.VIEWER, PermissionEnum.DEVICE_CREATE, False),
        (RoleEnum.VIEWER, PermissionEnum.DEVICE_READ, False),
        (RoleEnum.MANAGER, PermissionEnum.GATEWAY_CREATE, False),
        (RoleEnum.ADMIN, PermissionEnum.GATEWAY_CREATE, True),
        (RoleEnum.MANAGER, PermissionEnum.COMPANY_READ, True),
        (RoleEnum.ADMIN, PermissionEnum.DEVICE_CREATE, True),
    ],
)
def test_user_has_permission_returns_expected_for_role(role, permission, expected):
    assert user_has_permission(role.value, False, permission) is expected


@pytest.mark.unit
def test_superuser_has_all_permissions():
    for permission in PermissionEnum:
        assert user_has_permission(None, True, permission) is True
