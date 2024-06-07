"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path("", views.home, name="home")
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path("", Home.as_view(), name="home")
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path("blog/", include("blog.urls"))
"""
import debug_toolbar
from django.conf.urls.static import static
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework import routers

from activities.urls import router as activities_router
from core import settings
from core.base.admin import my_admin_site
from interacts.urls import router as interacts_router
from schools.urls import router as schools_router
from users.urls import router as users_router

schema_view = get_schema_view(
    openapi.Info(
        title="Training Point Management API",
        default_version="v1",
        description="APIs for Training Point Management project",
        contact=openapi.Contact(email="linearteam.404@gmail.com"),
        license=openapi.License(name="(Trần Thanh Hiệp - Nguyễn Song Hậu)@2024"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ],
)

router = routers.DefaultRouter()
router.registry.extend(activities_router.registry)
router.registry.extend(interacts_router.registry)
router.registry.extend(schools_router.registry)
router.registry.extend(users_router.registry)

urlpatterns = [
    path("admin/", my_admin_site.urls),
    path("api/v1/", include(router.urls)),
    path("ckeditor5/", include("django_ckeditor_5.urls"), name="ck_editor_5_upload_file"),
    path("__debug__/", include(debug_toolbar.urls)),
    path("api/v1/o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
]

urlpatterns += static(prefix=settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(prefix=settings.STATIC_URL, document_root=settings.STATIC_ROOT)
