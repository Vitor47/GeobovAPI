from typing import cast

from app.core.cache_utils.user_cache import redis_client


def _attempt_key(bucket: str) -> str:
    return f"attempts:{bucket}"


def attempt_count(bucket: str) -> int:
    """Return how many failures or hits are stored for this bucket."""
    raw = cast(str | None, redis_client.get(_attempt_key(bucket)))
    if raw is None:
        return 0
    return int(raw)


def is_attempt_limited(bucket: str, limit: int) -> bool:
    """True when the bucket is already at the limit. Does not record a new hit."""
    return attempt_count(bucket) >= limit


def register_attempt(bucket: str, window_seconds: int) -> int:
    """Count one attempt and start the window on the first hit."""
    key = _attempt_key(bucket)
    count = cast(int, redis_client.incr(key))
    if count == 1:
        redis_client.expire(key, window_seconds)
    return count


def clear_attempts(bucket: str) -> None:
    redis_client.delete(_attempt_key(bucket))


def client_ip(real_ip: str | None, peer: str | None) -> str:
    """Prefer the proxy's X-Real-IP. Nginx overwrites that header."""
    if real_ip:
        return real_ip.split(",")[0].strip()
    if peer:
        return peer
    return "unknown"
