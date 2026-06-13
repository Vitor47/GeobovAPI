import json
from dataclasses import dataclass
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


def _session_key(user_id: int | str) -> str:
    return f"session:user:{user_id}"


def _resolve_role_name(role: Any) -> str | None:
    if role is None:
        return None
    if hasattr(role, "name"):
        return str(getattr(role, "name"))
    return str(role)


def serialize_user(user: Any) -> dict[str, Any]:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": getattr(user, "full_name", ""),
        "company_id": user.company_id,
        "role": _resolve_role_name(getattr(user, "role", None)),
        "is_superuser": bool(getattr(user, "is_superuser", False)),
    }


def serialize_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": int(payload["sub"]),
        "email": payload.get("email"),
        "full_name": payload.get("full_name", ""),
        "company_id": payload.get("company_id"),
        "role": payload.get("role"),
        "is_superuser": bool(payload.get("is_superuser", False)),
    }


def deserialize_user(data: dict[str, Any]) -> CachedUser:
    return CachedUser(
        id=int(data["id"]),
        email=str(data["email"]),
        full_name=str(data.get("full_name", "")),
        company_id=data.get("company_id"),
        role=data.get("role"),
        is_superuser=bool(data.get("is_superuser", False)),
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


def invalidate_user_session(user_id: int | str) -> None:
    redis_client.delete(_session_key(user_id))
