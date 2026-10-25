import json
from dataclasses import dataclass, field
from typing import Any

from redis import Redis

from app.core.config import settings

redis_client: Redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,
)


@dataclass
class CachedUser:
    id: int
    email: str
    full_name: str
    company_id: int | None
    role: str | None
    is_superuser: bool
    company_ids: list[int] = field(default_factory=list)
    jti: str | None = None


def _session_key(user_id: int | str) -> str:
    return f"session:user:{user_id}"


def _revoked_key(jti: str) -> str:
    return f"revoked:jti:{jti}"


def _resolve_role_name(role: Any) -> str | None:
    if role is None:
        return None
    if hasattr(role, "name"):
        return str(getattr(role, "name"))
    return str(role)


def _resolve_company_ids(user: Any) -> list[int]:
    company_ids = getattr(user, "company_ids", None)
    if company_ids is None:
        return []
    return [int(company_id) for company_id in company_ids]


def serialize_user(user: Any) -> dict[str, Any]:
    company_ids = _resolve_company_ids(user)
    return {
        "id": user.id,
        "email": user.email,
        "full_name": getattr(user, "full_name", ""),
        "company_id": user.company_id,
        "company_ids": company_ids,
        "role": _resolve_role_name(getattr(user, "role", None)),
        "is_superuser": bool(getattr(user, "is_superuser", False)),
    }


def serialize_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    company_ids = payload.get("company_ids") or []
    return {
        "id": int(payload["sub"]),
        "email": payload.get("email"),
        "full_name": payload.get("full_name", ""),
        "company_id": payload.get("company_id"),
        "company_ids": [int(item) for item in company_ids],
        "role": payload.get("role"),
        "is_superuser": bool(payload.get("is_superuser", False)),
        "jti": payload.get("jti"),
    }


def deserialize_user(data: dict[str, Any]) -> CachedUser:
    company_ids = data.get("company_ids") or []
    return CachedUser(
        id=int(data["id"]),
        email=str(data["email"]),
        full_name=str(data.get("full_name", "")),
        company_id=data.get("company_id"),
        company_ids=[int(item) for item in company_ids],
        role=data.get("role"),
        is_superuser=bool(data.get("is_superuser", False)),
        jti=data.get("jti"),
    )


def cache_user_session(user: Any) -> CachedUser:
    cached = deserialize_user(serialize_user(user))
    redis_client.setex(
        _session_key(cached.id),
        settings.SESSION_CACHE_TTL_SECONDS,
        json.dumps(serialize_user(user)),
    )
    return cached


def cache_user_from_payload(payload: dict[str, Any]) -> CachedUser:
    data = serialize_from_payload(payload)
    cached = deserialize_user(data)
    redis_client.setex(
        _session_key(cached.id),
        settings.SESSION_CACHE_TTL_SECONDS,
        json.dumps(data),
    )
    return cached


def get_cached_session(user_id: int | str) -> CachedUser | None:
    cached = redis_client.get(_session_key(user_id))
    if not isinstance(cached, str):
        return None
    return deserialize_user(json.loads(cached))


def is_token_revoked(jti: str) -> bool:
    return bool(redis_client.exists(_revoked_key(jti)))


def revoke_token(user_id: int | str, jti: str | None) -> None:
    """
    Drop the server session and keep the JWT id blocked until it would expire.

    A later request must not recreate the session from the token claims.
    """
    redis_client.delete(_session_key(user_id))
    if not jti:
        return
    ttl_seconds = max(int(settings.ACCESS_TOKEN_EXPIRE_MINUTES) * 60, 1)
    redis_client.setex(_revoked_key(jti), ttl_seconds, "1")


def invalidate_user_session(user_id: int | str, jti: str | None = None) -> None:
    revoke_token(user_id, jti)
