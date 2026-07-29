from typing import Sequence

from sqlalchemy.orm import Session

from app.adapters.models.company import Company
from app.domain.repositories.company_repository_abstract import (
    CompanyRepositoryAbstract,
)


class CompanyRepository(CompanyRepositoryAbstract):

    def __init__(self, db: Session):
        self.db = db

    def create_company(self, data):
        db_company = Company(**data.dict())

        self.db.add(db_company)
        self.db.commit()
        self.db.refresh(db_company)
        return db_company

    def get_company_by_id(self, company_id: int):
        return self.db.query(Company).filter(Company.id == company_id).first()

    def get_all_companies(self):
        return self.db.query(Company).all()

    def get_companies_by_ids(self, company_ids: Sequence[int]):
        if not company_ids:
            return []
        return (
            self.db.query(Company)
            .filter(Company.id.in_(list(company_ids)))
            .order_by(Company.name.asc())
            .all()
        )

    def delete_company(self, company_id: int):
        company = self.get_company_by_id(company_id)
        if company:
            self.db.delete(company)
            self.db.commit()
