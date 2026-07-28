from datetime import datetime


class GatewayCreateDTO:
    def __init__(
        self,
        serial_number: str,
        company_id: int,
        name: str | None = None,
    ):
        self.serial_number = serial_number
        self.company_id = company_id
        self.name = name


class GatewayResponseDTO:
    def __init__(
        self,
        id: int,
        serial_number: str,
        name: str | None,
        company_id: int,
        is_active: bool,
        last_seen_at: datetime | None = None,
        api_key: str | None = None,
    ):
        self.id = id
        self.serial_number = serial_number
        self.name = name
        self.company_id = company_id
        self.is_active = is_active
        self.last_seen_at = last_seen_at
        # Only populated on create — never returned on list/get.
        self.api_key = api_key


class GatewayTelemetryIngestDTO:
    def __init__(self, device_serial: str, lat: float, lon: float):
        self.device_serial = device_serial
        self.lat = lat
        self.lon = lon


class GatewayTelemetryResponseDTO:
    def __init__(
        self,
        gateway_id: int,
        device_id: int,
        cattle_id: int,
        cattle_data_id: str,
        lat: float,
        lon: float,
    ):
        self.gateway_id = gateway_id
        self.device_id = device_id
        self.cattle_id = cattle_id
        self.cattle_data_id = cattle_data_id
        self.lat = lat
        self.lon = lon
