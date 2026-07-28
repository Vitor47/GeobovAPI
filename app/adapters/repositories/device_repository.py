from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.adapters.models.cattle import Cattle
from app.adapters.models.device import Device
from app.domain.repositories.device_repository_abstract import (
    DeviceRepositoryAbstract,
)


class DeviceRepository(DeviceRepositoryAbstract):

    def __init__(self, db: Session):
        self.db = db

    def create_device(self, data, **kwargs: Any) -> Device:
        cattle = (
            self.db.query(Cattle)
            .filter(
                Cattle.id == data.cattle_id,
                Cattle.company_id == data.company_id,
            )
            .first()
        )
        if not cattle:
            raise ValueError("Cattle not found for this company")

        existing = (
            self.db.query(Device).filter(Device.cattle_id == data.cattle_id).first()
        )
        if existing:
            raise ValueError("Cattle already has a device registered")

        serial_exists = (
            self.db.query(Device)
            .filter(Device.serial_number == data.serial_number)
            .first()
        )
        if serial_exists:
            raise ValueError("Serial number already registered")

        db_device = Device(
            serial_number=data.serial_number,
            name=data.name,
            cattle_id=data.cattle_id,
            company_id=data.company_id,
            transmission_interval_minutes=data.transmission_interval_minutes,
        )
        self.db.add(db_device)
        self.db.commit()
        self.db.refresh(db_device)
        return db_device

    def get_device_by_id_and_company_id(self, device_id: int, company_id: int):
        return (
            self.db.query(Device)
            .filter(
                Device.id == device_id,
                Device.company_id == company_id,
            )
            .first()
        )

    def get_devices_by_company_id(self, company_id: int):
        return self.db.query(Device).filter(Device.company_id == company_id).all()

    def get_active_device_by_serial_and_company(
        self,
        serial_number: str,
        company_id: int,
    ) -> Optional[Device]:
        return (
            self.db.query(Device)
            .filter(
                Device.serial_number == serial_number,
                Device.company_id == company_id,
                Device.is_active.is_(True),
            )
            .first()
        )

    def update_last_seen(self, device_id: int) -> None:
        stmt = (
            update(Device)
            .where(Device.id == device_id)
            .values(last_seen_at=datetime.now(timezone.utc))
        )
        self.db.execute(stmt)
        self.db.commit()
