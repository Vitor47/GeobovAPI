from datetime import datetime, timedelta, timezone

import pytest
from bson import ObjectId

from app.adapters.repositories.cattle_data_repository import CattleDataRepository
from app.application.dtos.cattle_data_dto import CattleDataCreateDTO


@pytest.mark.integration
def test_create_cattle_data_persists_record_when_payload_is_valid(mongo_db):
    repository = CattleDataRepository(db=mongo_db)
    payload = CattleDataCreateDTO(
        cattle_id=1,
        lat=-23.55,
        lon=-46.63,
        company_id=10,
    )

    result = repository.create_cattle_data(payload)

    assert result.id is not None
    assert result.cattle_id == 1
    assert result.company_id == 10
    assert result.lat == -23.55
    assert result.lon == -46.63

    stored = mongo_db["cattle_telemetry"].find_one({"_id": ObjectId(result.id)})
    assert stored is not None
    assert stored["lat"] == -23.55
    assert "sequence" not in stored


@pytest.mark.integration
def test_create_cattle_data_persists_lora_fields_when_provided(mongo_db):
    repository = CattleDataRepository(db=mongo_db)
    payload = CattleDataCreateDTO(
        cattle_id=1,
        lat=-29.6732,
        lon=-53.8113,
        company_id=10,
        protocol_version=1,
        sequence=27,
        satellites=9,
        hdop=1.2,
        rssi=-83,
        snr=6.75,
    )

    result = repository.create_cattle_data(payload)

    assert result.protocol_version == 1
    assert result.sequence == 27
    assert result.satellites == 9
    assert result.hdop == 1.2
    assert result.rssi == -83
    assert result.snr == 6.75

    stored = mongo_db["cattle_telemetry"].find_one({"_id": ObjectId(result.id)})
    assert stored["sequence"] == 27
    assert stored["rssi"] == -83


@pytest.mark.integration
def test_get_cattle_data_by_id_and_company_id_returns_none_when_not_found(mongo_db):
    repository = CattleDataRepository(db=mongo_db)

    result = repository.get_cattle_data_by_id_and_company_id(
        telemetry_id="507f1f77bcf86cd799439011",
        company_id=10,
    )

    assert result is None


@pytest.mark.integration
def test_get_cattle_data_by_company_id_returns_only_company_records(mongo_db):
    repository = CattleDataRepository(db=mongo_db)
    repository.create_cattle_data(
        CattleDataCreateDTO(
            cattle_id=1,
            lat=-23.55,
            lon=-46.63,
            company_id=10,
        )
    )
    repository.create_cattle_data(
        CattleDataCreateDTO(
            cattle_id=2,
            lat=-22.0,
            lon=-45.0,
            company_id=99,
        )
    )

    results = repository.get_cattle_data_by_company_id(10)

    assert len(results) == 1
    assert results[0].company_id == 10


@pytest.mark.integration
def test_downsample_raw_telemetry_aggregates_and_deletes_old_samples(mongo_db):
    repository = CattleDataRepository(db=mongo_db)
    repository.ensure_indexes()

    # Fixed timestamps inside the same 30-minute bucket.
    bucket_start = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    mongo_db["cattle_telemetry"].insert_many(
        [
            {
                "cattle_id": 1,
                "company_id": 10,
                "lat": -23.0,
                "lon": -46.0,
                "timestamp": bucket_start + timedelta(minutes=1),
            },
            {
                "cattle_id": 1,
                "company_id": 10,
                "lat": -24.0,
                "lon": -47.0,
                "timestamp": bucket_start + timedelta(minutes=5),
            },
        ]
    )

    deleted = repository.downsample_raw_telemetry(
        older_than=datetime(2026, 6, 1, tzinfo=timezone.utc),
        interval_minutes=30,
    )

    assert deleted == 2
    assert mongo_db["cattle_telemetry"].count_documents({}) == 0
    history = list(mongo_db["cattle_telemetry_history"].find({}))
    assert len(history) == 1
    assert history[0]["lat"] == pytest.approx(-23.5)
    assert history[0]["lon"] == pytest.approx(-46.5)
