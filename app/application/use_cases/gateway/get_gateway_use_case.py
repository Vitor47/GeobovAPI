from dataclasses import dataclass, field

from app.application.dtos.gateway_dto import GatewayResponseDTO
from app.application.steps.gateway import GetGatewayStep
from app.domain.repositories.gateway_repository_abstract import (
    GatewayRepositoryAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class GetGatewayUseCase(BaseUseCase):
    repository: GatewayRepositoryAbstract
    gateway_id: int
    company_id: int
    data: GatewayResponseDTO | None = field(init=False, default=None)

    def __post_init__(self):
        super().__init__(steps=[GetGatewayStep])
