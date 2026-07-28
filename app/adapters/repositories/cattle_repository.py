from typing import Any

from sqlalchemy.orm import Session

from app.adapters.models.cattle import Cattle
from app.domain.repositories.cattle_repository_abstract import (
    CattleRepositoryAbstract,
)

UPDATABLE_FIELDS = (
    "tag",
    "name",
    "description",
    "birth_date",
    "weight",
    "breed",
    "gender",
    "color",
    "notes",
    "is_active",
)


class CattleRepository(CattleRepositoryAbstract):

    def __init__(self, db: Session):
        self.db = db

    def create_cattle(self, data: Any) -> Cattle:
        existing = (
            self.db.query(Cattle)
            .filter(
                Cattle.tag == data.tag,
                Cattle.company_id == data.company_id,
            )
            .first()
        )
        if existing:
            raise ValueError("Cattle tag already exists for this company")

        cattle = Cattle(
            tag=data.tag,
            name=data.name,
            description=data.description,
            birth_date=data.birth_date,
            weight=data.weight,
            breed=data.breed,
            gender=data.gender,
            color=data.color,
            notes=data.notes,
            company_id=data.company_id,
            is_active=True,
        )
        self.db.add(cattle)
        self.db.commit()
        self.db.refresh(cattle)
        return cattle

    def get_cattle_by_id_and_company_id(
        self,
        cattle_id: int,
        company_id: int,
    ) -> Cattle | None:
        return (
            self.db.query(Cattle)
            .filter(
                Cattle.id == cattle_id,
                Cattle.company_id == company_id,
            )
            .first()
        )

    def get_cattles_by_company_id(self, company_id: int) -> list[Cattle]:
        return (
            self.db.query(Cattle)
            .filter(Cattle.company_id == company_id)
            .order_by(Cattle.id.asc())
            .all()
        )

    def update_cattle(self, cattle_id: int, company_id: int, data: Any) -> Cattle:
        cattle = self.get_cattle_by_id_and_company_id(cattle_id, company_id)
        if cattle is None:
            raise ValueError("Cattle not found for this company")

        if data.tag is not None and data.tag != cattle.tag:
            conflict = (
                self.db.query(Cattle)
                .filter(
                    Cattle.tag == data.tag,
                    Cattle.company_id == company_id,
                    Cattle.id != cattle_id,
                )
                .first()
            )
            if conflict:
                raise ValueError("Cattle tag already exists for this company")

        for field_name in UPDATABLE_FIELDS:
            value = getattr(data, field_name, None)
            if value is not None:
                setattr(cattle, field_name, value)

        self.db.commit()
        self.db.refresh(cattle)
        return cattle
