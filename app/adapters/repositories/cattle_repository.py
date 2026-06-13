from sqlalchemy.orm import Session

from app.adapters.models.cattle import CattleData
from app.domain.repositories.cattle_repository_abstract import (
    CattleRepositoryAbstract,
)


class CattleRepository(CattleRepositoryAbstract):

    def __init__(self, db: Session):
        self.db = db

    def create_cattle(self, data):
        db_data = CattleData(
            cattle_id=data.cattle_id,
            lat=data.lat,
            lon=data.lon,
            movement=data.movement,
            temperature=data.temperature,
            company_id=data.company_id,
        )
        self.db.add(db_data)
        self.db.commit()
        self.db.refresh(db_data)
        return db_data

    def get_cattle_by_id_and_company_id(self, cattle_id: int, company_id: int):
        return (
            self.db.query(CattleData)
            .filter(
                CattleData.id == cattle_id,
                CattleData.company_id == company_id,
            )
            .first()
        )

    def get_cattles_by_company_id(self, company_id: int):
        return (
            self.db.query(CattleData)
            .filter(
                CattleData.company_id == company_id,
            )
            .all()
        )
