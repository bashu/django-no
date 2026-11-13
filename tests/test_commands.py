from collections.abc import Callable
from io import StringIO
from pathlib import Path

from django.core.management import CommandError
from django.core.management import call_command

import pytest
from pytest_django import Settings

from no.backends.local import from_path


@pytest.fixture
def no_command() -> Callable[..., str]:
    def run_command(*args: str) -> str:
        output = StringIO()
        call_command("no", *args, stdout=output)
        return output.getvalue()

    return run_command


class TestNoCommand:
    def test_output(self, no_command: Callable[..., str]) -> None:
        assert no_command().removesuffix("\n") in from_path()

    def test_configured_backend(
        self,
        settings: Settings,
        custom_reasons_file: Path,
        no_command: Callable[..., str],
    ) -> None:
        settings.NO = {"OPTIONS": {"path": str(custom_reasons_file)}}

        assert no_command() == "Nope.\n"

    def test_arguments(self, no_command: Callable[..., str]) -> None:
        with pytest.raises(CommandError, match="unrecognized arguments: please"):
            no_command("please")
