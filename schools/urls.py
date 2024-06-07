from django.urls import path, include
from rest_framework import routers

from schools import views

router = routers.DefaultRouter()
router.register(prefix="classes", viewset=views.ClassViewSet, basename="classes")
router.register(prefix="semesters", viewset=views.SemesterViewSet, basename="semesters")
router.register(prefix="criterions", viewset=views.CriterionViewSet, basename="criterions")
router.register(prefix="statistics/(?P<semester_code>[1-9]+)", viewset=views.StatisticsViewSet, basename="statistics")

urlpatterns = [path("", include(router.urls))]
