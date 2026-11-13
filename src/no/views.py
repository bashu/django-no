from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.template import loader
from django.views.decorators.csrf import requires_csrf_token

from . import get_reason


def render_error(
    request: HttpRequest,
    exception: Exception | None,
    template_name: str,
    fallback: str,
) -> str:
    template = loader.select_template([template_name, fallback])
    context = {"reason": get_reason(), "exception": str(exception or "")}
    return template.render(context, request)


@requires_csrf_token
def permission_denied(
    request: HttpRequest,
    exception: Exception,
    template_name: str = "403.html",
) -> HttpResponse:
    """
    403 handler that tells users why not.

    handler403 = "no.views.permission_denied"
    """
    content = render_error(request, exception, template_name, "no/403.html")
    return HttpResponseForbidden(content)


@requires_csrf_token
def too_many_requests(
    request: HttpRequest,
    exception: Exception | None = None,
    template_name: str = "429.html",
) -> HttpResponse:
    """
    429 view for rate limiters, e.g. django-ratelimit.

    RATELIMIT_VIEW = "no.views.too_many_requests"
    """
    content = render_error(request, exception, template_name, "no/429.html")
    return HttpResponse(content, status=429)
