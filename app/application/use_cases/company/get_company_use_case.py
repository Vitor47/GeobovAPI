from dataclasses import dataclass, field

from app.application.dtos.company_dto import CompanyResponseDTO
from app.application.steps.company.get_company_step import GetCompanyStep
from app.domain.repositories.company_repository_abstract import (
    CompanyRepositoryAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class GetCompanyUseCase(BaseUseCase):
    repository: CompanyRepositoryAbstract
    company_id: int
    data: CompanyResponseDTO | None = field(init=False, default=None)

    def __post_init__(self):
        super().__init__(steps=[GetCompanyStep])
