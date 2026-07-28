from app.domain.steps.base_use_case_step import BaseUseCaseStep


class DownsampleTelemetryStep(BaseUseCaseStep):
    def _run(self):
        deleted = self.use_case.repository.downsample_raw_telemetry(
            older_than=self.use_case.older_than,
            interval_minutes=self.use_case.interval_minutes,
        )
        self.use_case.deleted_count = deleted
