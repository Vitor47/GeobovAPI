from dataclasses import dataclass, field

from app.application.dtos.cattle_dto import CattleResponseDTO
from app.application.steps.cattle import GetCattleStep
from app.domain.repositories.cattle_repository_abstract import (
    CattleRepositoryAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class GetCattleUseCase(BaseUseCase):
    repository: CattleRepositoryAbstract
    cattle_id: int
    company_id: int
    data: CattleResponseDTO | None = field(init=False, default=None)

    def __post_init__(self):
        super().__init__(steps=[GetCattleStep])
