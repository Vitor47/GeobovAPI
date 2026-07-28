from datetime import datetime, timezone
from typing import Any, Optional

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.database import Database

from app.domain.entities.cattle_data import CattleData
from app.domain.repositories.cattle_data_repository_abstract import (
    CattleDataRepositoryAbstract,
)

RAW_COLLECTION = "cattle_telemetry"
HISTORY_COLLECTION = "cattle_telemetry_history"


class CattleDataRepository(CattleDataRepositoryAbstract):
    """MongoDB adapter for high-frequency and downsampled cattle telemetry."""

    def __init__(self, db: Database):
        self.db = db
        self.raw = db[RAW_COLLECTION]
        self.history = db[HISTORY_COLLECTION]

    def create_cattle_data(self, data: Any) -> CattleData:
        timestamp = datetime.now(timezone.utc)
        document = {
            "cattle_id": data.cattle_id,
            "company_id": data.company_id,
            "lat": data.lat,
            "lon": data.lon,
            "timestamp": timestamp,
        }
        result = self.raw.insert_one(document)
        return CattleData(
            id=str(result.inserted_id),
            cattle_id=data.cattle_id,
            company_id=data.company_id,
            lat=data.lat,
            lon=data.lon,
            timestamp=timestamp,
        )

    def get_cattle_data_by_id_and_company_id(
        self,
        telemetry_id: str,
        company_id: int,
    ) -> Optional[CattleData]:
        object_id = self._parse_object_id(telemetry_id)
        if object_id is None:
            return None

        document = self.raw.find_one({"_id": object_id, "company_id": company_id})
        if document is None:
            document = self.history.find_one(
                {"_id": object_id, "company_id": company_id}
            )
        if document is None:
            return None
        return self._to_entity(document)

    def get_cattle_data_by_company_id(self, company_id: int) -> list[CattleData]:
        query = {"company_id": company_id}
        raw_docs = list(self.raw.find(query).sort("timestamp", -1))
        history_docs = list(self.history.find(query).sort("timestamp", -1))
        return [self._to_entity(doc) for doc in raw_docs + history_docs]

    def ensure_indexes(self) -> None:
        self.raw.create_index(
            [("company_id", 1), ("cattle_id", 1), ("timestamp", -1)],
            name="tenant_cattle_timestamp",
        )
        self.raw.create_index([("timestamp", 1)], name="timestamp_asc")
        self.history.create_index(
            [("company_id", 1), ("cattle_id", 1), ("timestamp", -1)],
            name="tenant_cattle_timestamp",
        )
        self.history.create_index(
            [("company_id", 1), ("cattle_id", 1), ("timestamp", 1)],
            name="unique_history_bucket",
            unique=True,
        )

    def downsample_raw_telemetry(  # pylint: disable=too-many-locals
        self,
        older_than: datetime,
        interval_minutes: int,
    ) -> int:
        interval_seconds = interval_minutes * 60
        old_docs = list(self.raw.find({"timestamp": {"$lt": older_than}}))
        if not old_docs:
            return 0

        buckets: dict[tuple[int, int, datetime], dict] = {}
        for document in old_docs:
            timestamp = document["timestamp"]
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            epoch = int(timestamp.timestamp())
            bucket_epoch = epoch - (epoch % interval_seconds)
            bucket_ts = datetime.fromtimestamp(bucket_epoch, tz=timezone.utc)
            key = (int(document["company_id"]), int(document["cattle_id"]), bucket_ts)
            bucket = buckets.get(key)
            if bucket is None:
                buckets[key] = {
                    "lat_sum": float(document["lat"]),
                    "lon_sum": float(document["lon"]),
                    "sample_count": 1,
                    "raw_ids": [document["_id"]],
                }
            else:
                bucket["lat_sum"] += float(document["lat"])
                bucket["lon_sum"] += float(document["lon"])
                bucket["sample_count"] += 1
                bucket["raw_ids"].append(document["_id"])

        raw_ids_to_delete: list[ObjectId] = []
        for (company_id, cattle_id, bucket_ts), bucket in buckets.items():
            count = bucket["sample_count"]
            avg_lat = bucket["lat_sum"] / count
            avg_lon = bucket["lon_sum"] / count
            existing = self.history.find_one(
                {
                    "company_id": company_id,
                    "cattle_id": cattle_id,
                    "timestamp": bucket_ts,
                }
            )
            if existing is None:
                self.history.insert_one(
                    {
                        "company_id": company_id,
                        "cattle_id": cattle_id,
                        "lat": avg_lat,
                        "lon": avg_lon,
                        "timestamp": bucket_ts,
                        "sample_count": count,
                    }
                )
            else:
                previous_count = int(existing.get("sample_count", 0))
                total_count = previous_count + count
                merged_lat = (
                    (float(existing["lat"]) * previous_count) + (avg_lat * count)
                ) / total_count
                merged_lon = (
                    (float(existing["lon"]) * previous_count) + (avg_lon * count)
                ) / total_count
                self.history.update_one(
                    {"_id": existing["_id"]},
                    {
                        "$set": {
                            "lat": merged_lat,
                            "lon": merged_lon,
                            "sample_count": total_count,
                        }
                    },
                )
            raw_ids_to_delete.extend(bucket["raw_ids"])

        result = self.raw.delete_many({"_id": {"$in": raw_ids_to_delete}})
        return int(result.deleted_count)

    @staticmethod
    def _parse_object_id(value: str) -> Optional[ObjectId]:
        try:
            return ObjectId(value)
        except (InvalidId, TypeError):
            return None

    @staticmethod
    def _to_entity(document: dict) -> CattleData:
        return CattleData(
            id=str(document["_id"]),
            cattle_id=int(document["cattle_id"]),
            company_id=int(document["company_id"]),
            lat=float(document["lat"]),
            lon=float(document["lon"]),
            timestamp=document["timestamp"],
        )
