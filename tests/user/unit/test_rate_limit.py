import pytest

from app.core.rate_limit import (
    client_ip,
    is_attempt_limited,
    register_attempt,
)


@pytest.mark.unit
def test_client_ip_prefers_proxy_header():
    assert client_ip("203.0.113.10", "172.16.0.1") == "203.0.113.10"


@pytest.mark.unit
def test_is_attempt_limited_reads_existing_count_without_increment(mocker):
    mock_redis = mocker.patch("app.core.rate_limit.redis_client")
    mock_redis.get.return_value = "10"

    assert is_attempt_limited("login:203.0.113.10", 10) is True
    mock_redis.incr.assert_not_called()


@pytest.mark.unit
def test_register_attempt_sets_window_on_first_failure(mocker):
    mock_redis = mocker.patch("app.core.rate_limit.redis_client")
    mock_redis.incr.return_value = 1

    count = register_attempt("login:203.0.113.10", 900)

    assert count == 1
    mock_redis.expire.assert_called_once_with("attempts:login:203.0.113.10", 900)
