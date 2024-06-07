from django.urls import path, include
from rest_framework import routers

from activities import views

router = routers.DefaultRouter()
router.register(prefix="bulletins", viewset=views.BulletinViewSet, basename="bulletins")
router.register(prefix="activities", viewset=views.ActivityViewSet, basename="activities")
router.register(prefix="reports", viewset=views.MissingActivityReportViewSet, basename="reports")

urlpatterns = [path("", include(router.urls))]
