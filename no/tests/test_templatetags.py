import json

from django.template import Context
from django.template import Template
from django.template import TemplateSyntaxError
from django.utils.html import escape

import pytest

from no.backends.local import from_path


@pytest.fixture
def reasons_file(tmp_path):
    path = tmp_path / "reasons.json"
    path.write_text(json.dumps(["Nope."]), encoding="utf-8")
    return path


def render(source, context=None):
    return Template("{% load no %}" + source).render(Context(context))


class TestNoTag:
    def test_render(self):
        assert render("{% no %}") in {escape(reason) for reason in from_path()}

    def test_as_variable(self, settings, reasons_file):
        settings.NO = {"OPTIONS": {"path": str(reasons_file)}}
        assert render("{% no as reason %}") == ""
        assert render("{% no as reason %}[{{ reason }}]") == "[Nope.]"

    def test_syntax_error(self):
        with pytest.raises(TemplateSyntaxError):
            render("{% no please %}")
