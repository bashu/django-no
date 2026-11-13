import json
from pathlib import Path

import pytest
from pytest_django import Settings


@pytest.fixture
def custom_reasons_file(tmp_path: Path) -> Path:
    path = tmp_path / "reasons.json"
    path.write_text(json.dumps(["Nope."]), encoding="utf-8")
    return path


@pytest.fixture
def custom_reasons_settings(settings: Settings, custom_reasons_file: Path) -> None:
    settings.NO = {"OPTIONS": {"path": str(custom_reasons_file)}}
