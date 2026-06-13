from dataclasses import dataclass, field

from app.application.dtos.device_dto import DeviceResponseDTO
from app.application.steps.device import GetDevicesStep
from app.domain.repositories.device_repository_abstract import (
    DeviceRepositoryAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class GetDevicesUseCase(BaseUseCase):
    repository: DeviceRepositoryAbstract
    company_id: int
    data: list[DeviceResponseDTO] = field(init=False, default_factory=list)

    def __post_init__(self):
        super().__init__(steps=[GetDevicesStep])
