from dataclasses import dataclass, field

from app.application.dtos.cattle_data_dto import CattleDataResponseDTO
from app.application.steps.telemetry import GetTelemetryStep
from app.domain.repositories.cattle_data_repository_abstract import (
    CattleDataRepositoryAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class GetTelemetryUseCase(BaseUseCase):
    repository: CattleDataRepositoryAbstract
    telemetry_id: str
    company_id: int
    data: CattleDataResponseDTO | None = field(init=False, default=None)

    def __post_init__(self):
        super().__init__(steps=[GetTelemetryStep])
