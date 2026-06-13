class CattleDataEntitie:
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
