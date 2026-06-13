from dataclasses import dataclass, field

from app.application.dtos.cattle_data_dto import CattleDataResponseDTO
from app.application.steps.cattle import GetCattlesStep
from app.domain.repositories.cattle_repository_abstract import (
    CattleRepositoryAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class GetCattlesUseCase(BaseUseCase):
    repository: CattleRepositoryAbstract
    company_id: int
    data: list[CattleDataResponseDTO] = field(init=False, default_factory=list)

    def __post_init__(self):
        super().__init__(steps=[GetCattlesStep])
