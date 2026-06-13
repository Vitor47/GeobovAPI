from dataclasses import dataclass, field

from app.application.dtos.company_dto import CompanyResponseDTO
from app.application.steps.company.list_companies_step import ListCompaniesStep
from app.domain.repositories.company_repository_abstract import (
    CompanyRepositoryAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class ListCompaniesUseCase(BaseUseCase):
    repository: CompanyRepositoryAbstract
    data: list[CompanyResponseDTO] = field(init=False, default_factory=list)

    def __post_init__(self):
        super().__init__(steps=[ListCompaniesStep])
