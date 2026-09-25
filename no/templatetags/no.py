from django import template

from no import get_reason

register = template.Library()


@register.simple_tag(name="no")
def no_tag():
    """
    Render a reason to say no.

    {% no %}
    {% no as reason %}
    """
    return get_reason()
