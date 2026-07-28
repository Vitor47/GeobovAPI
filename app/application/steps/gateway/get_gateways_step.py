from app.application.dtos.gateway_dto import GatewayResponseDTO
from app.domain.steps.base_use_case_step import BaseUseCaseStep


class GetGatewaysStep(BaseUseCaseStep):
    def _run(self):
        gateways = self.use_case.repository.get_gateways_by_company_id(
            self.use_case.company_id
        )

        self.use_case.data = [
            GatewayResponseDTO(
                id=g.id,
                serial_number=g.serial_number,
                name=g.name,
                company_id=g.company_id,
                is_active=g.is_active,
                last_seen_at=g.last_seen_at,
                api_key=None,
            )
            for g in gateways
        ]
