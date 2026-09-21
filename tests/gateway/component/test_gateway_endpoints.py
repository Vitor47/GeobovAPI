import pytest

VALID_INGEST_PAYLOAD = {
    "protocol_version": 1,
    "cow_id": 1,
    "lat": -29.6732,
    "lon": -53.8113,
    "sequence": 27,
    "satellites": 9,
    "hdop": 1.2,
    "rssi": -83,
    "snr": 6.75,
}


@pytest.mark.component
def test_gateway_ingest_returns_422_when_api_key_is_missing(client):
    response = client.post(
        "/api/v1/gateways/ingest",
        json=VALID_INGEST_PAYLOAD,
    )

    assert response.status_code == 422


@pytest.mark.component
@pytest.mark.parametrize(
    "field,value",
    [
        ("protocol_version", 2),
        ("protocol_version", 0),
        ("cow_id", 0),
        ("cow_id", 65536),
        ("lat", -90.1),
        ("lat", 90.1),
        ("lon", -180.1),
        ("lon", 180.1),
        ("sequence", -1),
        ("satellites", -1),
        ("satellites", 256),
        ("hdop", -0.1),
        ("hdop", 25.6),
        ("rssi", -201),
        ("rssi", 21),
        ("snr", -30.1),
        ("snr", 30.1),
    ],
)
def test_gateway_ingest_returns_422_when_field_is_out_of_range(client, field, value):
    payload = {**VALID_INGEST_PAYLOAD, field: value}

    response = client.post(
        "/api/v1/gateways/ingest",
        json=payload,
        headers={"X-Gateway-Api-Key": "test-key"},
    )

    assert response.status_code == 422


@pytest.mark.component
@pytest.mark.parametrize(
    "missing_field",
    [
        "protocol_version",
        "cow_id",
        "lat",
        "lon",
        "sequence",
        "satellites",
        "hdop",
        "rssi",
        "snr",
    ],
)
def test_gateway_ingest_returns_422_when_required_field_is_missing(
    client, missing_field
):
    payload = {
        key: value
        for key, value in VALID_INGEST_PAYLOAD.items()
        if key != missing_field
    }

    response = client.post(
        "/api/v1/gateways/ingest",
        json=payload,
        headers={"X-Gateway-Api-Key": "test-key"},
    )

    assert response.status_code == 422


@pytest.mark.component
def test_create_gateway_returns_401_when_not_authenticated(client):
    response = client.post(
        "/api/v1/gateways/",
        json={"serial_number": "GW-001"},
    )

    assert response.status_code == 401


@pytest.mark.component
def test_device_ingest_route_is_removed(client):
    response = client.post(
        "/api/v1/devices/ingest",
        json={"lat": -23.55, "lon": -46.63},
        headers={"X-Device-Api-Key": "anything"},
    )

    # Path may match GET /{device_id} ("ingest") → 405, or no route → 404.
    assert response.status_code in {404, 405}
