from dataclasses import dataclass, field

from app.application.dtos.address_dto import (
    AddressLookupRequestDTO,
    AddressResponseDTO,
)
from app.application.steps.address import LookupAddressStep
from app.domain.gateways.address_lookup_gateway_abstract import (
    AddressLookupGatewayAbstract,
)
from app.domain.use_cases.base_use_case import BaseUseCase


@dataclass
class LookupAddressUseCase(BaseUseCase):
    gateway: AddressLookupGatewayAbstract
    payload: AddressLookupRequestDTO
    data: AddressResponseDTO | None = field(init=False, default=None)

    def __post_init__(self):
        super().__init__(steps=[LookupAddressStep])
