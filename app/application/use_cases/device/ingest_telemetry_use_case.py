from dataclasses import dataclass, field

from app.application.dtos.device_dto import (
    DeviceTelemetryIngestDTO,
    DeviceTelemetryResponseDTO,
)
from app.application.steps.device import IngestTelemetryStep
from app.domain.repositories.cattle_repository_abstract import (
    CattleRepositoryAbstract,
)
from app.domain.repositories.device_repository_abstract import (
    DeviceRepositoryAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class IngestTelemetryUseCase(BaseUseCase):
    device_repository: DeviceRepositoryAbstract
    cattle_repository: CattleRepositoryAbstract
    api_key: str
    payload: DeviceTelemetryIngestDTO
    data: DeviceTelemetryResponseDTO | None = field(init=False, default=None)

    def __post_init__(self):
        super().__init__(steps=[IngestTelemetryStep])
