from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DeviceCreate(BaseModel):
    serial_number: str = Field(description="Unique LoRa device serial number.")
    cattle_id: int = Field(description="Cattle to link (one device per cattle).")
    name: str | None = Field(default=None, description="Optional friendly device name.")
    transmission_interval_minutes: int = Field(
        default=5,
        ge=1,
        description="Expected telemetry interval in minutes.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "serial_number": "LORA-001-A1B2",
                "cattle_id": 1,
                "name": "North pasture collar",
                "transmission_interval_minutes": 5,
            }
        }
    )


class DeviceResponse(BaseModel):
    id: int
    serial_number: str
    name: str | None
    cattle_id: int
    company_id: int
    api_key: str = Field(description="Secret key for telemetry ingestion.")
    is_active: bool
    transmission_interval_minutes: int
    last_seen_at: datetime | None = Field(
        default=None,
        description="Last successful telemetry ingest timestamp (UTC).",
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "serial_number": "LORA-001-A1B2",
                "name": "North pasture collar",
                "cattle_id": 1,
                "company_id": 1,
                "api_key": "xYz123_secure_key",
                "is_active": True,
                "transmission_interval_minutes": 5,
                "last_seen_at": "2026-06-10T12:00:00Z",
            }
        },
    )


class DeviceTelemetryIngest(BaseModel):
    lat: float = Field(description="GPS latitude.", examples=[-23.5505])
    lon: float = Field(description="GPS longitude.", examples=[-46.6333])
    movement: float = Field(default=0.0, ge=0, description="Movement index.")
    temperature: float = Field(default=0.0, description="Temperature in °C.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "lat": -23.5505,
                "lon": -46.6333,
                "movement": 8.0,
                "temperature": 38.1,
            }
        }
    )


class DeviceTelemetryResponse(BaseModel):
    device_id: int
    cattle_id: int
    cattle_data_id: int = Field(description="Created cattle telemetry record ID.")
    lat: float
    lon: float
    movement: float
    temperature: float

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "device_id": 1,
                "cattle_id": 1,
                "cattle_data_id": 42,
                "lat": -23.5505,
                "lon": -46.6333,
                "movement": 8.0,
                "temperature": 38.1,
            }
        },
    )
