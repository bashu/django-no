from no.backends.base import BaseBackend


class PoliteBackend(BaseBackend):
    def get_reason(self):
        return "No, thank you."
