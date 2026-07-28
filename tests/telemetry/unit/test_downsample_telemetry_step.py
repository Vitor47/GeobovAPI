from datetime import datetime, timezone

import pytest

from app.application.steps.telemetry.downsample_telemetry_step import (
    DownsampleTelemetryStep,
)
from app.application.use_cases.telemetry.downsample_telemetry_use_case import (
    DownsampleTelemetryUseCase,
)


@pytest.mark.unit
def test_downsample_telemetry_step_sets_deleted_count_when_repository_returns(mocker):
    mock_repository = mocker.Mock()
    mock_repository.downsample_raw_telemetry.return_value = 42

    older_than = datetime(2026, 1, 1, tzinfo=timezone.utc)
    use_case = DownsampleTelemetryUseCase(
        repository=mock_repository,
        older_than=older_than,
        interval_minutes=30,
    )

    DownsampleTelemetryStep(use_case=use_case).run()

    assert use_case.deleted_count == 42
    mock_repository.downsample_raw_telemetry.assert_called_once_with(
        older_than=older_than,
        interval_minutes=30,
    )
