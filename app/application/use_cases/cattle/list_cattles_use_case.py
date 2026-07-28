from dataclasses import dataclass, field

from app.application.dtos.cattle_dto import CattleResponseDTO
from app.application.steps.cattle import ListCattlesStep
from app.domain.repositories.cattle_repository_abstract import (
    CattleRepositoryAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class ListCattlesUseCase(BaseUseCase):
    repository: CattleRepositoryAbstract
    company_id: int
    data: list[CattleResponseDTO] = field(init=False, default_factory=list)

    def __post_init__(self):
        super().__init__(steps=[ListCattlesStep])
