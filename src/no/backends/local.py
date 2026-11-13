import json
import random
from functools import cache
from importlib.resources import files
from pathlib import Path
from typing import TYPE_CHECKING

from .base import BaseBackend

if TYPE_CHECKING:
    from importlib.resources.abc import Traversable


@cache
def from_path(path: str | Path | None = None) -> tuple[str, ...]:
    src: Traversable = Path(path) if path else files("no").joinpath("reasons.json")
    with src.open(encoding="utf-8") as f:
        return tuple(json.load(f))


class LocalBackend(BaseBackend):
    def get_reason(self) -> str:
        return random.choice(from_path(self.options.get("path")))  # noqa: S311
