from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TelemetryCreate(BaseModel):
    cattle_id: int = Field(description="Linked cattle entity ID.")
    lat: float = Field(
        ge=-90,
        le=90,
        description="Latitude in decimal degrees.",
        examples=[-23.5505],
    )
    lon: float = Field(
        ge=-180,
        le=180,
        description="Longitude in decimal degrees.",
        examples=[-46.6333],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cattle_id": 1,
                "lat": -23.5505,
                "lon": -46.6333,
            }
        }
    )


class TelemetryResponse(BaseModel):
    id: str = Field(description="Telemetry document ID (MongoDB ObjectId).")
    cattle_id: int = Field(description="Linked cattle entity ID.")
    lat: float = Field(description="Latitude in decimal degrees.")
    lon: float = Field(description="Longitude in decimal degrees.")
    timestamp: datetime | None = Field(
        default=None,
        description="Sample timestamp (UTC).",
    )
    protocol_version: int | None = Field(
        default=None,
        description="LoRa packet protocol version, when ingested via gateway.",
    )
    sequence: int | None = Field(
        default=None,
        description="Collar transmission sequence number, when present.",
    )
    satellites: int | None = Field(
        default=None,
        description="GPS satellite count, when present.",
    )
    hdop: float | None = Field(
        default=None,
        description="Horizontal dilution of precision, when present.",
    )
    rssi: int | None = Field(
        default=None,
        description="Gateway SX127x RSSI (dBm), when present.",
    )
    snr: float | None = Field(
        default=None,
        description="Gateway SX127x SNR (dB), when present.",
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "cattle_id": 1,
                "lat": -23.5505,
                "lon": -46.6333,
                "timestamp": "2026-06-10T12:00:00Z",
            }
        },
    )
