from app.application.dtos.cattle_data_dto import CattleDataResponseDTO
from app.domain.steps.base_use_case_step import BaseUseCaseStep
from app.domain.use_cases.exceptions import StopUseCaseException


class CreateTelemetryStep(BaseUseCaseStep):
    def _run(self):
        payload = self.use_case.payload
        cattle = self.use_case.cattle_repository.get_cattle_by_id_and_company_id(
            payload.cattle_id,
            payload.company_id,
        )
        if not cattle:
            raise StopUseCaseException("Cattle not found for this company")

        cattle_data = self.use_case.repository.create_cattle_data(payload)

        self.use_case.data = CattleDataResponseDTO(
            id=cattle_data.id,
            cattle_id=cattle_data.cattle_id,
            lat=cattle_data.lat,
            lon=cattle_data.lon,
            timestamp=cattle_data.timestamp,
        )
