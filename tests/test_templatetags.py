from collections.abc import Callable
from pathlib import Path
from typing import Any

from django.template import Context
from django.template import Template
from django.template import TemplateSyntaxError
from django.utils.html import escape

import pytest
from pytest_django import Settings

from no.backends.local import from_path


@pytest.fixture
def no_tag() -> Callable[..., str]:
    def render_template(source: str, context: dict[str, Any] | None = None) -> str:
        return Template("{% load no %}" + source).render(Context(context))

    return render_template


class TestNoTag:
    def test_render(self, no_tag: Callable[..., str]) -> None:
        assert no_tag("{% no %}") in {escape(reason) for reason in from_path()}

    def test_as_variable(
        self,
        settings: Settings,
        custom_reasons_file: Path,
        no_tag: Callable[..., str],
    ) -> None:
        settings.NO = {"OPTIONS": {"path": str(custom_reasons_file)}}

        assert no_tag("{% no as reason %}") == ""
        assert no_tag("{% no as reason %}[{{ reason }}]") == "[Nope.]"

    def test_syntax_error(self, no_tag: Callable[..., str]) -> None:
        with pytest.raises(
            TemplateSyntaxError,
            match="'no' received too many positional arguments",
        ):
            no_tag("{% no please %}")
