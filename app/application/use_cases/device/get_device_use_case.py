from dataclasses import dataclass, field

from app.application.dtos.device_dto import DeviceResponseDTO
from app.application.steps.device import GetDeviceStep
from app.domain.repositories.device_repository_abstract import (
    DeviceRepositoryAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class GetDeviceUseCase(BaseUseCase):
    repository: DeviceRepositoryAbstract
    device_id: int
    company_id: int
    data: DeviceResponseDTO | None = field(init=False, default=None)

    def __post_init__(self):
        super().__init__(steps=[GetDeviceStep])
