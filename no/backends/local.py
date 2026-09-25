import json
import random
from functools import cache
from importlib.resources import files
from pathlib import Path

from .base import BaseBackend


@cache
def from_path(path=None):
    src = Path(path) if path else files("no").joinpath("reasons.json")
    with src.open(encoding="utf-8") as f:
        return tuple(json.load(f))


class LocalBackend(BaseBackend):
    def get_reason(self):
        return random.choice(from_path(self.options.get("path")))  # noqa: S311
