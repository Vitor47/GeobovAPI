from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DeviceCreate(BaseModel):
    serial_number: str = Field(
        description=(
            "Unique LoRa collar serial " "(hardware ID, optional last-seen tracking)."
        )
    )
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
                "serial_number": "LORA-COLLAR-001",
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
                "serial_number": "LORA-COLLAR-001",
                "name": "North pasture collar",
                "cattle_id": 1,
                "company_id": 1,
                "is_active": True,
                "transmission_interval_minutes": 5,
                "last_seen_at": "2026-06-10T12:00:00Z",
            }
        },
    )
