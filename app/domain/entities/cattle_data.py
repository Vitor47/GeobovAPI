from dataclasses import dataclass
from datetime import datetime


@dataclass
class CattleData:
    """Domain entity representing a cattle GPS telemetry sample."""

    id: str
    cattle_id: int
    company_id: int
    lat: float
    lon: float
    timestamp: datetime
    protocol_version: int | None = None
    sequence: int | None = None
    satellites: int | None = None
    hdop: float | None = None
    rssi: int | None = None
    snr: float | None = None
