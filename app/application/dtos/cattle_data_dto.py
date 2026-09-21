from datetime import datetime

from app.domain.entities.cattle_data import CattleData


class CattleDataCreateDTO:
    def __init__(
        self,
        cattle_id: int,
        lat: float,
        lon: float,
        company_id: int,
        protocol_version: int | None = None,
        sequence: int | None = None,
        satellites: int | None = None,
        hdop: float | None = None,
        rssi: int | None = None,
        snr: float | None = None,
    ):
        self.cattle_id = cattle_id
        self.lat = lat
        self.lon = lon
        self.company_id = company_id
        self.protocol_version = protocol_version
        self.sequence = sequence
        self.satellites = satellites
        self.hdop = hdop
        self.rssi = rssi
        self.snr = snr


class CattleDataResponseDTO:
    def __init__(
        self,
        id: str,
        cattle_id: int,
        lat: float,
        lon: float,
        timestamp: datetime | None = None,
        protocol_version: int | None = None,
        sequence: int | None = None,
        satellites: int | None = None,
        hdop: float | None = None,
        rssi: int | None = None,
        snr: float | None = None,
    ):
        self.id = id
        self.cattle_id = cattle_id
        self.lat = lat
        self.lon = lon
        self.timestamp = timestamp
        self.protocol_version = protocol_version
        self.sequence = sequence
        self.satellites = satellites
        self.hdop = hdop
        self.rssi = rssi
        self.snr = snr

    @classmethod
    def from_entity(cls, record: CattleData) -> "CattleDataResponseDTO":
        return cls(
            id=record.id,
            cattle_id=record.cattle_id,
            lat=record.lat,
            lon=record.lon,
            timestamp=record.timestamp,
            protocol_version=record.protocol_version,
            sequence=record.sequence,
            satellites=record.satellites,
            hdop=record.hdop,
            rssi=record.rssi,
            snr=record.snr,
        )
