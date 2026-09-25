from django.core.exceptions import PermissionDenied


def forbidden(request):
    msg = "Members only"
    raise PermissionDenied(msg)
