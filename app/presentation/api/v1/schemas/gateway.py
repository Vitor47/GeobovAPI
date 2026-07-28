from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GatewayCreate(BaseModel):
    serial_number: str = Field(description="Unique LoRa gateway serial / hardware ID.")
    name: str | None = Field(
        default=None, description="Optional friendly gateway name."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "serial_number": "GW-FAZENDA-A-001",
                "name": "Barn receiver",
            }
        }
    )


class GatewayResponse(BaseModel):
    id: int
    serial_number: str
    name: str | None
    company_id: int
    is_active: bool
    last_seen_at: datetime | None = Field(
        default=None,
        description="Last successful telemetry forward timestamp (UTC).",
    )
    api_key: str | None = Field(
        default=None,
        description=(
            "Secret key for gateway ingest. Returned only when the gateway "
            "is created; omitted on list/get."
        ),
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "serial_number": "GW-FAZENDA-A-001",
                "name": "Barn receiver",
                "company_id": 1,
                "api_key": "xYz123_secure_key",
                "is_active": True,
                "last_seen_at": "2026-06-10T12:00:00Z",
            }
        },
    )


class GatewayTelemetryIngest(BaseModel):
    device_serial: str = Field(
        description=(
            "Collar serial from the LoRa packet " "(must match Device.serial_number)."
        )
    )
    lat: float = Field(description="GPS latitude.", examples=[-23.5505])
    lon: float = Field(description="GPS longitude.", examples=[-46.6333])

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "device_serial": "LORA-COLLAR-001",
                "lat": -23.5505,
                "lon": -46.6333,
            }
        }
    )


class GatewayTelemetryResponse(BaseModel):
    gateway_id: int
    device_id: int
    cattle_id: int
    cattle_data_id: str = Field(description="Created telemetry document ID.")
    lat: float
    lon: float

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "gateway_id": 1,
                "device_id": 1,
                "cattle_id": 1,
                "cattle_data_id": "507f1f77bcf86cd799439011",
                "lat": -23.5505,
                "lon": -46.6333,
            }
        },
    )
