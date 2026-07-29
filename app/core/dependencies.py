from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.cache_utils.user_cache import (
    cache_user_from_payload,
    get_cached_session,
)
from app.core.security import decode_access_token

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Prefer the JWT being presented so active company_id matches this token
    # (e.g. after POST /users/switch-company), not a stale Redis snapshot.
    cached_user = get_cached_session(user_id)
    if cached_user is None:
        return cache_user_from_payload(payload)

    token_company_id = payload.get("company_id")
    if token_company_id is not None:
        try:
            token_company_id = int(token_company_id)
        except (TypeError, ValueError):
            token_company_id = None
    cached_company_id = cached_user.company_id
    if cached_company_id is not None:
        try:
            cached_company_id = int(cached_company_id)
        except (TypeError, ValueError):
            cached_company_id = None
    if token_company_id is not None and cached_company_id != token_company_id:
        return cache_user_from_payload(payload)

    return cached_user
