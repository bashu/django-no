class BaseBackend:
    def __init__(self, **options):
        self.options = options

    def get_reason(self) -> str:
        raise NotImplementedError
