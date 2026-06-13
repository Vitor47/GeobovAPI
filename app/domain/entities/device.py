from datetime import datetime


class Device:
    def __init__(
        self,
        id: int,
        serial_number: str,
        name: str | None,
        cattle_id: int,
        company_id: int,
        is_active: bool,
        transmission_interval_minutes: int,
        last_seen_at: datetime | None = None,
    ):
        self.id = id
        self.serial_number = serial_number
        self.name = name
        self.cattle_id = cattle_id
        self.company_id = company_id
        self.is_active = is_active
        self.transmission_interval_minutes = transmission_interval_minutes
        self.last_seen_at = last_seen_at
