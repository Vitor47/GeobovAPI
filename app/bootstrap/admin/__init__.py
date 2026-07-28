from pathlib import Path

from sqladmin import Admin

from app.bootstrap.admin.auth import AdminAuth
from app.bootstrap.admin.telemetry_view import TelemetryReadAdmin
from app.bootstrap.admin.views import (
    CattleAdmin,
    CompanyAdmin,
    DeviceAdmin,
    GatewayAdmin,
    RoleAdmin,
    UserAdmin,
)
from app.core.config import settings
from app.core.database import engine

_TEMPLATES_DIR = str(Path(__file__).resolve().parent / "templates")


def register_admin(app) -> Admin | None:
    """
    Mount SQLAdmin at /admin for PostgreSQL cadastral models and
    a read-only MongoDB telemetry browser.

    Disabled when ADMIN_ENABLED=false. Login requires an existing superuser
    (created via `python -m app.commands setup`).
    """
    if not settings.ADMIN_ENABLED:
        return None

    authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)
    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=authentication_backend,
        title="CowTrack Admin",
        base_url="/admin",
        templates_dir=_TEMPLATES_DIR,
    )
    admin.add_view(CompanyAdmin)
    admin.add_view(CattleAdmin)
    admin.add_view(DeviceAdmin)
    admin.add_view(GatewayAdmin)
    admin.add_view(UserAdmin)
    admin.add_view(RoleAdmin)
    admin.add_view(TelemetryReadAdmin)
    return admin
