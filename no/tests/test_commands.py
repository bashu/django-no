import json
from io import StringIO

from django.core.management import CommandError
from django.core.management import call_command

import pytest

from no.backends.local import from_path


@pytest.fixture
def reasons_file(tmp_path):
    path = tmp_path / "reasons.json"
    path.write_text(json.dumps(["Nope."]), encoding="utf-8")
    return path


def run(*args):
    out = StringIO()
    call_command("no", *args, stdout=out)
    return out.getvalue()


class TestNoCommand:
    def test_output(self):
        assert run().removesuffix("\n") in from_path()

    def test_configured_backend(self, settings, reasons_file):
        settings.NO = {"OPTIONS": {"path": str(reasons_file)}}
        assert run() == "Nope.\n"

    def test_arguments(self):
        with pytest.raises(CommandError):
            run("please")
