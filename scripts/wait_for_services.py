"""Wait until PostgreSQL and Redis are ready before starting the API."""

from __future__ import annotations

import sys
import time

from redis import Redis
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from app.core.config import settings

MAX_RETRIES = 30
RETRY_DELAY_SECONDS = 2


def wait_for_database() -> None:
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print("PostgreSQL is ready.")
            return
        except OperationalError as error:
            print(
                f"PostgreSQL not ready ({attempt}/{MAX_RETRIES}): {error}",
                flush=True,
            )
            time.sleep(RETRY_DELAY_SECONDS)

    raise RuntimeError("PostgreSQL did not become ready in time.")


def wait_for_redis() -> None:
    client = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
        socket_connect_timeout=2,
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if client.ping():
                print("Redis is ready.")
                return
        except Exception as error:
            print(
                f"Redis not ready ({attempt}/{MAX_RETRIES}): {error}",
                flush=True,
            )
            time.sleep(RETRY_DELAY_SECONDS)

    raise RuntimeError("Redis did not become ready in time.")


def main() -> None:
    wait_for_database()
    wait_for_redis()


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
