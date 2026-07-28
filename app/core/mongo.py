from pymongo import MongoClient
from pymongo.database import Database

from app.core.config import settings


class _MongoClientHolder:
    """Process-wide MongoDB client holder (avoids module-level global)."""

    client: MongoClient | None = None


def get_mongo_client() -> MongoClient:
    """Return a process-wide MongoDB client (lazy singleton)."""
    if _MongoClientHolder.client is None:
        _MongoClientHolder.client = MongoClient(settings.MONGO_URL)
    return _MongoClientHolder.client


def get_mongo_db() -> Database:
    """Return the application MongoDB database handle."""
    client = get_mongo_client()
    return client.get_database(settings.MONGO_DB_NAME)


def close_mongo_client() -> None:
    """Close the shared MongoDB client if it was opened."""
    if _MongoClientHolder.client is not None:
        _MongoClientHolder.client.close()
        _MongoClientHolder.client = None
