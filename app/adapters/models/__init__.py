"""SQLAlchemy ORM models.

Importing this package registers every mapped class so relationships
like Company.gateways can resolve regardless of entrypoint import order.
"""

from app.adapters.models.cattle import Cattle
from app.adapters.models.company import Company
from app.adapters.models.device import Device
from app.adapters.models.gateway import Gateway
from app.adapters.models.role import Role
from app.adapters.models.user import User
from app.adapters.models.user_company import user_companies

__all__ = [
    "Cattle",
    "Company",
    "Device",
    "Gateway",
    "Role",
    "User",
    "user_companies",
]
