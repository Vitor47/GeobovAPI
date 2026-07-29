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
        return self.db.query(Company).order_by(Company.name.asc()).all()

    def get_companies_by_ids(self, company_ids: Sequence[int]):
        if not company_ids:
            return []
        return (
            self.db.query(Company)
            .filter(Company.id.in_(list(company_ids)))
            .order_by(Company.name.asc())
            .all()
        )

    def search_companies(
        self,
        *,
        company_ids: Sequence[int] | None = None,
        query: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Company], int]:
        q = self.db.query(Company)

        if company_ids is not None:
            if not company_ids:
                return [], 0
            q = q.filter(Company.id.in_(list(company_ids)))

        normalized = (query or "").strip()
        if normalized:
            q = q.filter(Company.name.ilike(f"%{normalized}%"))

        total = q.count()
        safe_page = max(page, 1)
        safe_size = min(max(page_size, 1), 100)
        items = (
            q.order_by(Company.name.asc())
            .offset((safe_page - 1) * safe_size)
            .limit(safe_size)
            .all()
        )
        return items, total

    def delete_company(self, company_id: int):
        company = self.get_company_by_id(company_id)
        if company:
            self.db.delete(company)
            self.db.commit()
