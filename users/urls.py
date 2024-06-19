from django.urls import include, path
from rest_framework import routers

from users import views

router = routers.DefaultRouter()
router.register(prefix='all-users', viewset=views.AllUsersViewSet, basename='all-users')
router.register(prefix="accounts", viewset=views.AccountViewSet, basename="accounts")
router.register(prefix="students", viewset=views.StudentViewSet, basename="students")
router.register(prefix="assistants", viewset=views.AssistantViewSet, basename="assistants")

urlpatterns = [path("", include(router.urls))]
