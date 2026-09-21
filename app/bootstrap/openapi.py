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

## Admin panel

Browse and edit cadastral data (companies, cattle, devices, gateways, users) at `/admin`.
Login with a superuser email/password (same credentials from setup/seed).

## Gateway telemetry

LoRa collars send a 17-byte binary packet (`cow_id` + GPS + sequence).
The farm gateway decodes it, adds SX127x RSSI/SNR, and forwards JSON to
`POST /api/v1/gateways/ingest` using `X-Gateway-Api-Key` received when
the gateway is registered. The API resolves gateway → company → `cow_id`
(Cattle.id) and stores telemetry.
"""

TAGS_METADATA = [
    {
        "name": "Users",
        "description": "Login, logout, session management, and user creation.",
    },
    {
        "name": "Cattle",
        "description": "Cattle animal registration, updates, and farmer observations.",
    },
    {
        "name": "Telemetry",
        "description": (
            "Cattle GPS telemetry records (latitude, longitude, timestamp, "
            "and optional LoRa RF quality fields)."
        ),
    },
    {
        "name": "Devices",
        "description": "LoRa GPS collar registration (serial linked to cattle).",
    },
    {
        "name": "Gateways",
        "description": "LoRa receivers that authenticate and forward collar telemetry.",
    },
    {
        "name": "Companies",
        "description": "Company lookup for authenticated users.",
    },
    {
        "name": "Health",
        "description": "Liveness checks for PostgreSQL, Redis, and MongoDB.",
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
    "GatewayApiKey": {
        "type": "apiKey",
        "in": "header",
        "name": "X-Gateway-Api-Key",
        "description": "Gateway API key returned on gateway registration.",
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
