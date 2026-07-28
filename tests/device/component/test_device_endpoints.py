import pytest


@pytest.mark.component
def test_create_device_returns_401_when_not_authenticated(client):
    response = client.post(
        "/api/v1/devices/",
        json={
            "serial_number": "LORA-001",
            "cattle_id": 1,
        },
    )

    assert response.status_code == 401
