from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.cache_utils.user_cache import (
    get_cached_session,
    is_token_revoked,
)
from app.core.security import decode_access_token

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Accept a JWT only when its id is still the active Redis session.

    Revoked and unknown tokens stop here. They are not written back to Redis
    and they are not counted as login attempts.
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    jti = payload.get("jti")
    if not user_id or not isinstance(jti, str) or not jti:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    if is_token_revoked(jti):
        raise HTTPException(status_code=401, detail="Token revoked")

    cached_user = get_cached_session(user_id)
    if cached_user is None or cached_user.jti != jti:
        raise HTTPException(status_code=401, detail="Token revoked")

    return cached_user
