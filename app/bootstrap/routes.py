from app.presentation.api.v1.endpoints import (
    cattle,
    company,
    device,
    gateway,
    telemetry,
    user,
)


def register_routes(app):
    app.include_router(user.router, prefix="/api/v1/users")
    app.include_router(cattle.router, prefix="/api/v1/cattle")
    app.include_router(telemetry.router, prefix="/api/v1/telemetry")
    app.include_router(device.router, prefix="/api/v1/devices")
    app.include_router(gateway.router, prefix="/api/v1/gateways")
    app.include_router(company.router, prefix="/api/v1/companies")
