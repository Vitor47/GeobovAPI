from dataclasses import dataclass, field

from app.application.dtos.gateway_dto import (
    GatewayTelemetryIngestDTO,
    GatewayTelemetryResponseDTO,
)
from app.application.steps.gateway import IngestGatewayTelemetryStep
from app.domain.repositories.cattle_data_repository_abstract import (
    CattleDataRepositoryAbstract,
)
from app.domain.repositories.cattle_repository_abstract import (
    CattleRepositoryAbstract,
)
from app.domain.repositories.device_repository_abstract import (
    DeviceRepositoryAbstract,
)
from app.domain.repositories.gateway_repository_abstract import (
    GatewayRepositoryAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class IngestGatewayTelemetryUseCase(BaseUseCase):
    gateway_repository: GatewayRepositoryAbstract
    cattle_repository: CattleRepositoryAbstract
    device_repository: DeviceRepositoryAbstract
    cattle_data_repository: CattleDataRepositoryAbstract
    api_key: str
    payload: GatewayTelemetryIngestDTO
    data: GatewayTelemetryResponseDTO | None = field(init=False, default=None)

    def __post_init__(self):
        super().__init__(steps=[IngestGatewayTelemetryStep])
