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
    def __init__(
        self,
        protocol_version: int,
        cow_id: int,
        lat: float,
        lon: float,
        sequence: int,
        satellites: int,
        hdop: float,
        rssi: int,
        snr: float,
    ):
        self.protocol_version = protocol_version
        self.cow_id = cow_id
        self.lat = lat
        self.lon = lon
        self.sequence = sequence
        self.satellites = satellites
        self.hdop = hdop
        self.rssi = rssi
        self.snr = snr


class GatewayTelemetryResponseDTO:
    def __init__(
        self,
        gateway_id: int,
        cattle_id: int,
        cattle_data_id: str,
        protocol_version: int,
        lat: float,
        lon: float,
        sequence: int,
        satellites: int,
        hdop: float,
        rssi: int,
        snr: float,
        device_id: int | None = None,
    ):
        self.gateway_id = gateway_id
        self.device_id = device_id
        self.cattle_id = cattle_id
        self.cattle_data_id = cattle_data_id
        self.protocol_version = protocol_version
        self.lat = lat
        self.lon = lon
        self.sequence = sequence
        self.satellites = satellites
        self.hdop = hdop
        self.rssi = rssi
        self.snr = snr
