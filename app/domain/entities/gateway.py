from datetime import datetime


class Gateway:
    def __init__(
        self,
        id: int,
        serial_number: str,
        name: str | None,
        company_id: int,
        is_active: bool,
        last_seen_at: datetime | None = None,
    ):
        self.id = id
        self.serial_number = serial_number
        self.name = name
        self.company_id = company_id
        self.is_active = is_active
        self.last_seen_at = last_seen_at
