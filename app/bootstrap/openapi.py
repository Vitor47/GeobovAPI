from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

API_DESCRIPTION = """
CowTrack API tracks cattle in real time using LoRa GPS devices.

## Authentication

1. Call `POST /api/v1/users/login` with email and password.
2. Use the returned JWT as `Authorization: Bearer <token>` on protected routes.
3. Sessions are cached in Redis for 24 hours.

## Superuser

Superusers must send the `X-Company-Id` header to scope company-bound operations.

## Device telemetry

LoRa devices send GPS data to `POST /api/v1/devices/ingest` using the
`X-Device-Api-Key` header received when the device is registered.
"""

TAGS_METADATA = [
    {
        "name": "Users",
        "description": "Login, logout, session management, and user creation.",
    },
    {
        "name": "Cattle",
        "description": "Cattle telemetry records (location, movement, temperature).",
    },
    {
        "name": "Devices",
        "description": "LoRa GPS device registration and telemetry ingestion.",
    },
    {
        "name": "Companies",
        "description": "Company lookup for authenticated users.",
    },
    {
        "name": "Health",
        "description": "Liveness checks for PostgreSQL and Redis.",
    },
]

SECURITY_SCHEMES = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": (
            "JWT access token from `POST /api/v1/users/login`. "
            "Example: `Authorization: Bearer eyJhbGciOi...`"
        ),
    },
    "DeviceApiKey": {
        "type": "apiKey",
        "in": "header",
        "name": "X-Device-Api-Key",
        "description": "Device API key returned on device registration.",
    },
    "CompanyHeader": {
        "type": "apiKey",
        "in": "header",
        "name": "X-Company-Id",
        "description": "Required for superuser requests to select a company.",
    },
}


class DocumentedFastAPI(FastAPI):
    def openapi(self) -> dict[str, Any]:
        if self.openapi_schema:
            return self.openapi_schema

        schema = get_openapi(
            title=self.title,
            version=self.version,
            description=self.description,
            routes=self.routes,
            tags=TAGS_METADATA,
        )
        schema["components"]["securitySchemes"] = SECURITY_SCHEMES
        self.openapi_schema = schema
        return self.openapi_schema
