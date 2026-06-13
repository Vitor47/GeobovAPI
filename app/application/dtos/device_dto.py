from datetime import datetime


class DeviceCreateDTO:
    def __init__(
        self,
        serial_number: str,
        cattle_id: int,
        company_id: int,
        name: str | None = None,
        transmission_interval_minutes: int = 5,
    ):
        self.serial_number = serial_number
        self.cattle_id = cattle_id
        self.company_id = company_id
        self.name = name
        self.transmission_interval_minutes = transmission_interval_minutes


class DeviceResponseDTO:
    def __init__(
        self,
        id: int,
        serial_number: str,
        name: str | None,
        cattle_id: int,
        company_id: int,
        api_key: str,
        is_active: bool,
        transmission_interval_minutes: int,
        last_seen_at: datetime | None = None,
    ):
        self.id = id
        self.serial_number = serial_number
        self.name = name
        self.cattle_id = cattle_id
        self.company_id = company_id
        self.api_key = api_key
        self.is_active = is_active
        self.transmission_interval_minutes = transmission_interval_minutes
        self.last_seen_at = last_seen_at


class DeviceTelemetryIngestDTO:
    def __init__(
        self,
        lat: float,
        lon: float,
        movement: float = 0.0,
        temperature: float = 0.0,
    ):
        self.lat = lat
        self.lon = lon
        self.movement = movement
        self.temperature = temperature


class DeviceTelemetryResponseDTO:
    def __init__(
        self,
        device_id: int,
        cattle_id: int,
        cattle_data_id: int,
        lat: float,
        lon: float,
        movement: float,
        temperature: float,
    ):
        self.device_id = device_id
        self.cattle_id = cattle_id
        self.cattle_data_id = cattle_data_id
        self.lat = lat
        self.lon = lon
        self.movement = movement
        self.temperature = temperature
