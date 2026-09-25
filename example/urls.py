from django.urls import path
from django.views.generic import TemplateView

from .views import forbidden

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
    path("forbidden/", forbidden, name="forbidden"),
]

handler403 = "no.views.permission_denied"
