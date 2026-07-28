from dataclasses import dataclass, field

from app.application.dtos.cattle_dto import CattleCreateDTO, CattleResponseDTO
from app.application.steps.cattle import CreateCattleStep
from app.domain.repositories.cattle_repository_abstract import (
    CattleRepositoryAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class CreateCattleUseCase(BaseUseCase):
    repository: CattleRepositoryAbstract
    payload: CattleCreateDTO
    data: CattleResponseDTO | None = field(init=False, default=None)

    def __post_init__(self):
        super().__init__(steps=[CreateCattleStep])
