from app.application.dtos.gateway_dto import GatewayResponseDTO
from app.domain.steps.base_use_case_step import BaseUseCaseStep


class GetGatewayStep(BaseUseCaseStep):
    def _run(self):
        gateway = self.use_case.repository.get_gateway_by_id_and_company_id(
            self.use_case.gateway_id,
            self.use_case.company_id,
        )

        if not gateway:
            return

        self.use_case.data = GatewayResponseDTO(
            id=gateway.id,
            serial_number=gateway.serial_number,
            name=gateway.name,
            company_id=gateway.company_id,
            is_active=gateway.is_active,
            last_seen_at=gateway.last_seen_at,
            api_key=None,
        )
