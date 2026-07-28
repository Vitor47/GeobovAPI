import pytest


@pytest.mark.component
def test_gateway_ingest_returns_422_when_api_key_is_missing(client):
    response = client.post(
        "/api/v1/gateways/ingest",
        json={
            "device_serial": "LORA-COLLAR-001",
            "lat": -23.55,
            "lon": -46.63,
        },
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
