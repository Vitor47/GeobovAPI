from dataclasses import dataclass, field
from datetime import datetime

from app.application.steps.telemetry import DownsampleTelemetryStep
from app.domain.repositories.cattle_data_repository_abstract import (
    CattleDataRepositoryAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class DownsampleTelemetryUseCase(BaseUseCase):
    repository: CattleDataRepositoryAbstract
    older_than: datetime
    interval_minutes: int
    deleted_count: int = field(init=False, default=0)

    def __post_init__(self):
        super().__init__(steps=[DownsampleTelemetryStep])
