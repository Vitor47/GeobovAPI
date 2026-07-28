from dataclasses import dataclass, field

from app.application.dtos.cattle_dto import CattleResponseDTO, CattleUpdateDTO
from app.application.steps.cattle import UpdateCattleStep
from app.domain.repositories.cattle_repository_abstract import (
    CattleRepositoryAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class UpdateCattleUseCase(BaseUseCase):
    repository: CattleRepositoryAbstract
    cattle_id: int
    company_id: int
    payload: CattleUpdateDTO
    data: CattleResponseDTO | None = field(init=False, default=None)

    def __post_init__(self):
        super().__init__(steps=[UpdateCattleStep])
