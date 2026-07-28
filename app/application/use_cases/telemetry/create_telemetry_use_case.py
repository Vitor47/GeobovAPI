from dataclasses import dataclass, field

from app.application.dtos.cattle_data_dto import (
    CattleDataCreateDTO,
    CattleDataResponseDTO,
)
from app.application.steps.telemetry import CreateTelemetryStep
from app.domain.repositories.cattle_data_repository_abstract import (
    CattleDataRepositoryAbstract,
)
from app.domain.repositories.cattle_repository_abstract import (
    CattleRepositoryAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class CreateTelemetryUseCase(BaseUseCase):
    repository: CattleDataRepositoryAbstract
    cattle_repository: CattleRepositoryAbstract
    payload: CattleDataCreateDTO
    data: CattleDataResponseDTO | None = field(init=False, default=None)

    def __post_init__(self):
        super().__init__(steps=[CreateTelemetryStep])
