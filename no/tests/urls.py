from django.core.exceptions import PermissionDenied
from django.urls import path


def forbidden(request):
    msg = "Staff only"
    raise PermissionDenied(msg)


urlpatterns = [
    path("forbidden/", forbidden),
]

handler403 = "no.views.permission_denied"
