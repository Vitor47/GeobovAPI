from enum import StrEnum


class PermissionEnum(StrEnum):
    CATTLE_CREATE = "cattle:create"
    CATTLE_READ = "cattle:read"
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    COMPANY_READ = "company:read"
    DEVICE_CREATE = "device:create"
    DEVICE_READ = "device:read"
