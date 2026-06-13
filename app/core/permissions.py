"""Re-exports for backward compatibility. Prefer `app.core.auth.deps`."""

from app.core.auth.deps import (
    CanCreateCattle,
    CanCreateDevice,
    CanCreateUser,
    CanReadCattle,
    CanReadCompany,
    CanReadDevice,
    CanReadUser,
    CompanyId,
    CurrentUser,
    SuperUser,
    require_permission,
    require_superuser,
    resolve_company_id,
)

__all__ = [
    "CanCreateCattle",
    "CanCreateDevice",
    "CanCreateUser",
    "CanReadCattle",
    "CanReadCompany",
    "CanReadDevice",
    "CanReadUser",
    "CompanyId",
    "CurrentUser",
    "SuperUser",
    "require_permission",
    "require_superuser",
    "resolve_company_id",
]
