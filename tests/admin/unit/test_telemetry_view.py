import pytest

from app.bootstrap.admin.telemetry_view import (
    _format_optional_float,
    _format_optional_int,
)


@pytest.mark.unit
def test_format_optional_int_returns_dash_when_value_is_missing():
    assert _format_optional_int(None) == "—"


@pytest.mark.unit
def test_format_optional_int_returns_integer_string_when_value_is_present():
    assert _format_optional_int(-83) == "-83"
    assert _format_optional_int(27) == "27"


@pytest.mark.unit
def test_format_optional_float_returns_dash_when_value_is_missing():
    assert _format_optional_float(None, 1) == "—"


@pytest.mark.unit
def test_format_optional_float_formats_with_requested_digits():
    assert _format_optional_float(1.2, 1) == "1.2"
    assert _format_optional_float(6.75, 2) == "6.75"
