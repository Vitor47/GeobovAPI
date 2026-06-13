class BaseUseCaseStep:
    def __init__(self, use_case):
        self.use_case = use_case

    def _run(self):
        raise NotImplementedError

    def run(self):
        self._run()
