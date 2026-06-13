from dataclasses import dataclass, field

from app.application.dtos.company_dto import (
    CompanyCreateDTO,
    CompanyResponseDTO,
)
from app.application.steps.company import CreateCompanyStep
from app.domain.repositories.company_repository_abstract import (
    CompanyRepositoryAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class CreateCompanyUseCase(BaseUseCase):
    repository: CompanyRepositoryAbstract
    payload: CompanyCreateDTO
    data: CompanyResponseDTO | None = field(init=False, default=None)

    def __post_init__(self):
        super().__init__(steps=[CreateCompanyStep])
