from app.domain.steps.base_use_case_step import BaseUseCaseStep


class BaseUseCase:
    def __init__(self, steps: list[BaseUseCaseStep]):
        self.steps = steps

    def run(self):
        for step_class in self.steps:
            step = step_class(use_case=self)
            step.run()
