class CattleDataCreateDTO:
    def __init__(
        self,
        cattle_id: int,
        lat: float,
        lon: float,
        movement: float,
        temperature: float,
        company_id: int,
    ):
        self.cattle_id = cattle_id
        self.lat = lat
        self.lon = lon
        self.movement = movement
        self.temperature = temperature
        self.company_id = company_id


class CattleDataResponseDTO:
    def __init__(
        self,
        id: int,
        cattle_id: int,
        lat: float,
        lon: float,
        movement: float,
        temperature: float,
    ):
        self.id = id
        self.cattle_id = cattle_id
        self.lat = lat
        self.lon = lon
        self.movement = movement
        self.temperature = temperature
