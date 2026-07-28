from fastapi import APIRouter, Response
from pydantic import BaseModel, ConfigDict, Field
from pymongo.errors import PyMongoError
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.cache_utils.user_cache import redis_client
from app.core.database import engine
from app.core.mongo import get_mongo_client

router = APIRouter(tags=["Health"])


class HealthChecks(BaseModel):
    database: bool = Field(description="PostgreSQL connectivity.")
    redis: bool = Field(description="Redis connectivity.")
    mongo: bool = Field(description="MongoDB connectivity.")


class HealthResponse(BaseModel):
    status: str = Field(description="Overall status: ok or degraded.")
    checks: HealthChecks

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ok",
                "checks": {"database": True, "redis": True, "mongo": True},
            }
        }
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description=(
        "Verifies PostgreSQL, Redis, and MongoDB connectivity. "
        "Used by Docker healthchecks."
    ),
)
def health_check(response: Response) -> dict:
    checks = {
        "database": False,
        "redis": False,
        "mongo": False,
    }

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        checks["database"] = True
    except SQLAlchemyError:
        pass

    try:
        checks["redis"] = bool(redis_client.ping())
    except RedisError:
        pass

    try:
        get_mongo_client().admin.command("ping")
        checks["mongo"] = True
    except PyMongoError:
        pass

    healthy = all(checks.values())
    response.status_code = 200 if healthy else 503

    return {
        "status": "ok" if healthy else "degraded",
        "checks": checks,
    }
