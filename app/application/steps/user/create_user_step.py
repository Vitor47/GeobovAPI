from app.application.dtos.user_dto import UserResponseDTO
from app.domain.steps.base_use_case_step import BaseUseCaseStep


class CreateUserStep(BaseUseCaseStep):
    def _run(self):
        user = self.use_case.repository.create_user(self.use_case.payload)

        self.use_case.data = UserResponseDTO(
            id=user.id,
            full_name=user.full_name,
            birth_date=user.birth_date,
            email=user.email,
            company_id=user.company_id,
            role=self.use_case.payload.role,
        )
