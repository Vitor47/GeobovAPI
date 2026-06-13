from app.domain.enums.permission_enum import PermissionEnum
from app.domain.enums.role_enum import RoleEnum

ROLE_PERMISSIONS: dict[RoleEnum, frozenset[PermissionEnum]] = {
    RoleEnum.ADMIN: frozenset(
        {
            PermissionEnum.CATTLE_CREATE,
            PermissionEnum.CATTLE_READ,
            PermissionEnum.USER_CREATE,
            PermissionEnum.USER_READ,
            PermissionEnum.COMPANY_READ,
            PermissionEnum.DEVICE_CREATE,
            PermissionEnum.DEVICE_READ,
        }
    ),
    RoleEnum.MANAGER: frozenset(
        {
            PermissionEnum.CATTLE_CREATE,
            PermissionEnum.CATTLE_READ,
            PermissionEnum.USER_READ,
            PermissionEnum.COMPANY_READ,
            PermissionEnum.DEVICE_CREATE,
            PermissionEnum.DEVICE_READ,
        }
    ),
    RoleEnum.VIEWER: frozenset(
        {
            PermissionEnum.CATTLE_READ,
            PermissionEnum.USER_READ,
            PermissionEnum.COMPANY_READ,
            PermissionEnum.DEVICE_READ,
        }
    ),
}


def user_has_permission(
    role: str | None,
    is_superuser: bool,
    permission: PermissionEnum,
) -> bool:
    if is_superuser:
        return True

    if role is None:
        return False

    try:
        role_enum = RoleEnum(role)
    except ValueError:
        return False

    return permission in ROLE_PERMISSIONS.get(role_enum, frozenset())
