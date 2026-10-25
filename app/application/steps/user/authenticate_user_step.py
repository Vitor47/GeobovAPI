from app.core.cache_utils.user_cache import cache_user_from_payload
from app.core.security import (
    build_token_payload,
    create_access_token,
    decode_access_token,
)
from app.domain.steps.base_use_case_step import BaseUseCaseStep
from app.domain.use_cases.exceptions import StopUseCaseException


class AuthenticateUserStep(BaseUseCaseStep):
    def _run(self):
        email = self.use_case.email
        password = self.use_case.password

        user = self.use_case.repository.get_user_by_email(email)

        if not user or not user.authenticate(password):
            raise StopUseCaseException("Invalid credentials")

        company_ids = list(getattr(user, "company_ids", []) or [])
        active_company_id = user.company_id
        if active_company_id is None and company_ids:
            active_company_id = company_ids[0]

        payload = build_token_payload(user)
        payload["company_id"] = active_company_id
        payload["company_ids"] = company_ids

        token = create_access_token(payload)
        issued = decode_access_token(token)
        if issued is None:
            raise StopUseCaseException("Could not issue access token")
        cache_user_from_payload(issued)

        self.use_case.data = {
            "access_token": token,
            "token_type": "bearer",
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "company_id": active_company_id,
            "company_ids": company_ids,
            "role": user.role.name if user.role else None,
            "is_superuser": user.is_superuser,
        }
