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
    protocol_version: int = Field(
        ge=1,
        le=1,
        description="LoRa packet protocol version. Only version 1 is supported.",
    )
    cow_id: int = Field(
        ge=1,
        le=65535,
        description="Numeric cattle identifier from the LoRa packet (Cattle.id).",
    )
    lat: float = Field(
        ge=-90,
        le=90,
        description="GPS latitude in decimal degrees (scaled from int32 / 1_000_000).",
        examples=[-29.6732],
    )
    lon: float = Field(
        ge=-180,
        le=180,
        description=(
            "GPS longitude in decimal degrees (scaled from int32 / 1_000_000)."
        ),
        examples=[-53.8113],
    )
    sequence: int = Field(
        ge=0,
        le=4_294_967_295,
        description="Sequential transmission number from the collar (uint32).",
    )
    satellites: int = Field(
        ge=0,
        le=255,
        description="GPS satellite count reported by the collar (uint8).",
    )
    hdop: float = Field(
        ge=0,
        le=25.5,
        description="Horizontal dilution of precision (HDOP, uint8 / 10).",
        examples=[1.2],
    )
    rssi: int = Field(
        ge=-200,
        le=20,
        description="RSSI measured by the SX127x on the gateway (dBm).",
        examples=[-83],
    )
    snr: float = Field(
        ge=-30,
        le=30,
        description="SNR measured by the SX127x on the gateway (dB).",
        examples=[6.75],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "protocol_version": 1,
                "cow_id": 1,
                "lat": -29.6732,
                "lon": -53.8113,
                "sequence": 27,
                "satellites": 9,
                "hdop": 1.2,
                "rssi": -83,
                "snr": 6.75,
            }
        }
    )


class GatewayTelemetryResponse(BaseModel):
    gateway_id: int
    device_id: int | None = Field(
        default=None,
        description="Linked collar device ID, if one is registered for this cattle.",
    )
    cattle_id: int
    cattle_data_id: str = Field(description="Created telemetry document ID.")
    protocol_version: int
    lat: float
    lon: float
    sequence: int
    satellites: int
    hdop: float
    rssi: int
    snr: float

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "gateway_id": 1,
                "device_id": 1,
                "cattle_id": 1,
                "cattle_data_id": "507f1f77bcf86cd799439011",
                "protocol_version": 1,
                "lat": -29.6732,
                "lon": -53.8113,
                "sequence": 27,
                "satellites": 9,
                "hdop": 1.2,
                "rssi": -83,
                "snr": 6.75,
            }
        },
    )
