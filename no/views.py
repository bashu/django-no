from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.template import loader
from django.views.decorators.csrf import requires_csrf_token

from no import get_reason


def render_error(request, exception, template_name, fallback):
    template = loader.select_template([template_name, fallback])
    context = {"reason": get_reason(), "exception": str(exception or "")}
    return template.render(context, request)


@requires_csrf_token
def permission_denied(request, exception, template_name="403.html"):
    """
    403 handler that tells users why not.

    handler403 = "no.views.permission_denied"
    """
    content = render_error(request, exception, template_name, "no/403.html")
    return HttpResponseForbidden(content)


@requires_csrf_token
def too_many_requests(request, exception=None, template_name="429.html"):
    """
    429 view for rate limiters, e.g. django-ratelimit.

    RATELIMIT_VIEW = "no.views.too_many_requests"
    """
    content = render_error(request, exception, template_name, "no/429.html")
    return HttpResponse(content, status=429)
