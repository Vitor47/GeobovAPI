from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.core.config import settings


def build_token_payload(user) -> dict[str, Any]:
    company_ids = list(getattr(user, "company_ids", []) or [])
    return {
        "sub": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "company_id": user.company_id,
        "company_ids": company_ids,
        "role": user.role.name if user.role else None,
        "is_superuser": bool(getattr(user, "is_superuser", False)),
    }


def create_access_token(data: dict[str, Any]) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except jwt.InvalidTokenError:
        return None
