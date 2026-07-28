from app.application.dtos.address_dto import AddressResponseDTO
from app.domain.steps.base_use_case_step import BaseUseCaseStep


class LookupAddressStep(BaseUseCaseStep):
    def _run(self):
        address = self.use_case.gateway.lookup_by_postal_code(
            postal_code=self.use_case.payload.postal_code,
            country_code=self.use_case.payload.country,
        )
        if address is None:
            self.use_case.data = None
            return

        self.use_case.data = AddressResponseDTO(
            street=address.street,
            city=address.city,
            state=address.state,
            postal_code=address.postal_code,
            country_code=address.country_code,
            neighborhood=address.neighborhood,
            address_line=address.to_address_line(),
        )
