from dataclasses import dataclass, field

from app.application.dtos.gateway_dto import GatewayResponseDTO
from app.application.steps.gateway import GetGatewaysStep
from app.domain.repositories.gateway_repository_abstract import (
    GatewayRepositoryAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class GetGatewaysUseCase(BaseUseCase):
    repository: GatewayRepositoryAbstract
    company_id: int
    data: list[GatewayResponseDTO] | None = field(init=False, default=None)

    def __post_init__(self):
        super().__init__(steps=[GetGatewaysStep])
