from app.core.cache_utils.user_cache import cache_user_session
from app.core.security import build_token_payload, create_access_token
from app.domain.steps.base_use_case_step import BaseUseCaseStep


class AuthenticateUserStep(BaseUseCaseStep):
    def _run(self):
        email = self.use_case.email
        password = self.use_case.password

        user = self.use_case.repository.get_user_by_email(email)

        if not user or not user.authenticate(password):
            return

        cache_user_session(user)

        token = create_access_token(build_token_payload(user))

        self.use_case.data = {
            "access_token": token,
            "token_type": "bearer",
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "company_id": user.company_id,
            "role": user.role.name if user.role else None,
            "is_superuser": user.is_superuser,
        }
