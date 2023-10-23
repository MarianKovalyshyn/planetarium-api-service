from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView

from planetarium.views import CreateUserView

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/planetarium/",
        include("planetarium.urls", namespace="planetarium"),
    ),
    path("api/doc/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/doc/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/user/register/", CreateUserView.as_view(), name="create")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
