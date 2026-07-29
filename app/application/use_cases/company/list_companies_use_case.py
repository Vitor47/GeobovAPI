from dataclasses import dataclass, field
from typing import Sequence

from app.application.dtos.company_dto import CompanyListResultDTO
from app.application.steps.company.list_companies_step import ListCompaniesStep
from app.domain.repositories.company_repository_abstract import (
    CompanyRepositoryAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class ListCompaniesUseCase(BaseUseCase):
    repository: CompanyRepositoryAbstract
    company_ids: Sequence[int] | None = None
    query: str | None = None
    page: int = 1
    page_size: int = 20
    data: CompanyListResultDTO | None = field(init=False, default=None)

    def __post_init__(self):
        super().__init__(steps=[ListCompaniesStep])
