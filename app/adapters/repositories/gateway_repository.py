import secrets
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.adapters.models.company import Company
from app.adapters.models.gateway import Gateway
from app.domain.repositories.gateway_repository_abstract import (
    GatewayRepositoryAbstract,
)


class GatewayRepository(GatewayRepositoryAbstract):

    def __init__(self, db: Session):
        self.db = db

    def create_gateway(self, data, **kwargs: Any) -> Gateway:
        company = self.db.query(Company).filter(Company.id == data.company_id).first()
        if not company:
            raise ValueError("Company not found")

        serial_exists = (
            self.db.query(Gateway)
            .filter(Gateway.serial_number == data.serial_number)
            .first()
        )
        if serial_exists:
            raise ValueError("Gateway serial number already registered")

        db_gateway = Gateway(
            serial_number=data.serial_number,
            name=data.name,
            company_id=data.company_id,
            api_key=secrets.token_urlsafe(32),
        )
        self.db.add(db_gateway)
        self.db.commit()
        self.db.refresh(db_gateway)
        return db_gateway

    def get_gateway_by_id_and_company_id(self, gateway_id: int, company_id: int):
        return (
            self.db.query(Gateway)
            .filter(
                Gateway.id == gateway_id,
                Gateway.company_id == company_id,
            )
            .first()
        )

    def get_gateways_by_company_id(self, company_id: int):
        return self.db.query(Gateway).filter(Gateway.company_id == company_id).all()

    def get_gateway_by_api_key(self, api_key: str):
        return (
            self.db.query(Gateway)
            .filter(
                Gateway.api_key == api_key,
                Gateway.is_active.is_(True),
            )
            .first()
        )

    def update_last_seen(self, gateway_id: int) -> None:
        stmt = (
            update(Gateway)
            .where(Gateway.id == gateway_id)
            .values(last_seen_at=datetime.now(timezone.utc))
        )
        self.db.execute(stmt)
        self.db.commit()
