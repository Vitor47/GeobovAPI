from dataclasses import dataclass, field

from app.application.dtos.device_dto import DeviceCreateDTO, DeviceResponseDTO
from app.application.steps.device import CreateDeviceStep
from app.domain.repositories.device_repository_abstract import (
    DeviceRepositoryAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class CreateDeviceUseCase(BaseUseCase):
    repository: DeviceRepositoryAbstract
    payload: DeviceCreateDTO
    data: DeviceResponseDTO | None = field(init=False, default=None)

    def __post_init__(self):
        super().__init__(steps=[CreateDeviceStep])
