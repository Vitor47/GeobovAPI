from dataclasses import dataclass, field

from app.application.dtos.cattle_data_dto import CattleDataResponseDTO
from app.application.steps.telemetry import ListTelemetryStep
from app.domain.repositories.cattle_data_repository_abstract import (
    CattleDataRepositoryAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class ListTelemetryUseCase(BaseUseCase):
    repository: CattleDataRepositoryAbstract
    company_id: int
    data: list[CattleDataResponseDTO] = field(init=False, default_factory=list)

    def __post_init__(self):
        super().__init__(steps=[ListTelemetryStep])
