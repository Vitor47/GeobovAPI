from datetime import datetime


class CattleDataCreateDTO:
    def __init__(
        self,
        cattle_id: int,
        lat: float,
        lon: float,
        company_id: int,
    ):
        self.cattle_id = cattle_id
        self.lat = lat
        self.lon = lon
        self.company_id = company_id


class CattleDataResponseDTO:
    def __init__(
        self,
        id: str,
        cattle_id: int,
        lat: float,
        lon: float,
        timestamp: datetime | None = None,
    ):
        self.id = id
        self.cattle_id = cattle_id
        self.lat = lat
        self.lon = lon
        self.timestamp = timestamp
