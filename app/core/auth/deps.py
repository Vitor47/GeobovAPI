from typing import Annotated

from fastapi import Depends, Header, HTTPException

from app.core.cache_utils.user_cache import CachedUser
from app.core.dependencies import get_current_user
from app.domain.auth.role_permissions import user_has_permission
from app.domain.enums.permission_enum import PermissionEnum


def require_permission(permission: PermissionEnum):
    def checker(
        current_user: CachedUser = Depends(get_current_user),
    ) -> CachedUser:
        if not user_has_permission(
            current_user.role, current_user.is_superuser, permission
        ):
            raise HTTPException(status_code=403, detail="Forbidden")
        return current_user

    return checker


def require_superuser(
    current_user: CachedUser = Depends(get_current_user),
) -> CachedUser:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Superuser access required")
    return current_user


def resolve_company_id(
    current_user: CachedUser = Depends(get_current_user),
    x_company_id: Annotated[int | None, Header(alias="X-Company-Id")] = None,
) -> int:
    if current_user.is_superuser:
        if x_company_id is None:
            raise HTTPException(
                status_code=400,
                detail="X-Company-Id header is required for superuser requests",
            )
        return x_company_id

    membership_ids = list(current_user.company_ids or [])

    if x_company_id is not None:
        if x_company_id not in membership_ids:
            raise HTTPException(
                status_code=403,
                detail="User is not a member of the requested company",
            )
        return x_company_id

    if (
        current_user.company_id is not None
        and current_user.company_id in membership_ids
    ):
        return current_user.company_id

    if membership_ids:
        return membership_ids[0]

    raise HTTPException(
        status_code=400,
        detail="User is not linked to a company",
    )


# Plain Depends aliases — use with @cbv controllers
CanCreateCattleDep = Depends(require_permission(PermissionEnum.CATTLE_CREATE))
CanReadCattleDep = Depends(require_permission(PermissionEnum.CATTLE_READ))
CanUpdateCattleDep = Depends(require_permission(PermissionEnum.CATTLE_UPDATE))
CanCreateUserDep = Depends(require_permission(PermissionEnum.USER_CREATE))
CanReadUserDep = Depends(require_permission(PermissionEnum.USER_READ))
CanReadCompanyDep = Depends(require_permission(PermissionEnum.COMPANY_READ))
CanCreateDeviceDep = Depends(require_permission(PermissionEnum.DEVICE_CREATE))
CanReadDeviceDep = Depends(require_permission(PermissionEnum.DEVICE_READ))
CanCreateGatewayDep = Depends(require_permission(PermissionEnum.GATEWAY_CREATE))
CanReadGatewayDep = Depends(require_permission(PermissionEnum.GATEWAY_READ))
CurrentUserDep = Depends(get_current_user)
SuperUserDep = Depends(require_superuser)
CompanyIdDep = Depends(resolve_company_id)

# Annotated aliases — use with function-based routes
CurrentUser = Annotated[CachedUser, CurrentUserDep]
SuperUser = Annotated[CachedUser, SuperUserDep]
CompanyId = Annotated[int, CompanyIdDep]
CanCreateCattle = Annotated[CachedUser, CanCreateCattleDep]
CanReadCattle = Annotated[CachedUser, CanReadCattleDep]
CanUpdateCattle = Annotated[CachedUser, CanUpdateCattleDep]
CanCreateUser = Annotated[CachedUser, CanCreateUserDep]
CanReadUser = Annotated[CachedUser, CanReadUserDep]
CanReadCompany = Annotated[CachedUser, CanReadCompanyDep]
CanCreateDevice = Annotated[CachedUser, CanCreateDeviceDep]
CanReadDevice = Annotated[CachedUser, CanReadDeviceDep]
CanCreateGateway = Annotated[CachedUser, CanCreateGatewayDep]
CanReadGateway = Annotated[CachedUser, CanReadGatewayDep]
