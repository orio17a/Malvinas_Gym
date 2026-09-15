"""
URL configuration for the Malvinas GYM project.

https://docs.djangoproject.com/en/6.1/topics/http/urls/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Login/logout listos para usar (registration/login.html) para que
    # @login_required en las vistas de gestión tenga a dónde redirigir.
    path("accounts/", include("django.contrib.auth.urls")),
    path("dashboard/", include("apps.dashboard.urls", namespace="dashboard")),
    path("socios/", include("apps.socios.urls")),
    path("actividades/", include("apps.actividades.urls")),
    path("", include("apps.core.urls", namespace="core")),
]

# Sirve archivos de media (apto físico, etc.) en desarrollo. En producción
# esto lo debe resolver el servidor web (nginx/whitenoise), no Django.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
