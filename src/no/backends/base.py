from typing import Any


class BaseBackend:
    def __init__(self, **options: Any) -> None:
        self.options = options

    def get_reason(self) -> str:
        raise NotImplementedError
