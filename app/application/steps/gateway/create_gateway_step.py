from app.application.dtos.gateway_dto import GatewayResponseDTO
from app.domain.steps.base_use_case_step import BaseUseCaseStep


class CreateGatewayStep(BaseUseCaseStep):
    def _run(self):
        gateway = self.use_case.repository.create_gateway(self.use_case.payload)

        self.use_case.data = GatewayResponseDTO(
            id=gateway.id,
            serial_number=gateway.serial_number,
            name=gateway.name,
            company_id=gateway.company_id,
            api_key=gateway.api_key,
            is_active=gateway.is_active,
            last_seen_at=gateway.last_seen_at,
        )
