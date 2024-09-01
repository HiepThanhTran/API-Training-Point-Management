from django.contrib.auth.hashers import check_password
from rest_framework import generics, parsers, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from activities import serializers as activities_serializers
from base import paginators
from base import perms
from schools import serializers as schools_serializer
from schools.models import Semester
from users import serializers as users_serializers
from users.models import Account, Assistant, Specialist, Student
from utils import dao


class AccountViewSet(viewsets.ViewSet):
	queryset = Account.objects.filter(is_active=True)
	serializer_class = users_serializers.AccountSerializer
	parser_classes = [parsers.MultiPartParser, ]

	def get_permissions(self):
		if self.action in ["get_authenticated_account", "partial_update_authenticated_account"]:
			return [permissions.IsAuthenticated()]

		if self.action in ["create_assistant_account"]:
			return [perms.HasInSpeacialistGroup()]

		return [permissions.AllowAny()]

	@action(methods=["get"], detail=False, url_path="me")
	def get_authenticated_account(self, request):
		serializer = self.serializer_class(request.user)
		return Response(data=serializer.data, status=status.HTTP_200_OK)

	@action(methods=["patch"], detail=False, url_path="me/update")
	def partial_update_authenticated_account(self, request):
		old_password = request.data.get("old_password", None)
		new_password = request.data.get("new_password", None)

		if old_password and new_password:
			if not check_password(old_password, request.user.password):
				return Response(data={"detail": "Mật khẩu cũ không chính xác"}, status=status.HTTP_400_BAD_REQUEST)

		serializer = users_serializers.AccountUpdateSerializer(
			instance=request.user,
			data=request.data,
			context={"request": request},
			partial=True,
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		return Response(data=self.serializer_class(request.user).data, status=status.HTTP_200_OK)

	@action(methods=["post"], detail=False, url_path="students/register")
	def create_student_account(self, request):
		return self._create_account(request=request)

	@action(methods=["post"], detail=False, url_path="assistants/register")
	def create_assistant_account(self, request):
		return self._create_account(request=request)

	def _create_account(self, request):
		serializer = self.serializer_class(data=request.data)

		if not serializer.is_valid(raise_exception=False):
			return Response(data={"detail": "Người dùng đã có tài khoản"}, status=status.HTTP_400_BAD_REQUEST)

		serializer.save()
		return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class AllUsersViewSet(viewsets.ViewSet):
	def list(self, request):
		name = request.query_params.get('name', '').strip().lower()

		specialist_accounts = Account.objects.filter(specialist__isnull=False).select_related('specialist')
		assistant_accounts = Account.objects.filter(assistant__isnull=False).select_related('assistant')
		combined_accounts = list(specialist_accounts) + list(assistant_accounts)

		combined_accounts = dao.filter_by_full_name(queryset=combined_accounts, search=name) if name else combined_accounts

		paginator = paginators.UserPagination()
		paginated_accounts = paginator.paginate_queryset(combined_accounts, request)
		serializer = users_serializers.AccountSerializer(paginated_accounts, many=True)

		return paginator.get_paginated_response(serializer.data)


class AssistantViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
	queryset = Assistant.objects.select_related("faculty").filter(is_active=True)
	serializer_class = users_serializers.AssistantSerializer
	pagination_class = paginators.AssistantPagination

	def get_queryset(self):
		queryset = self.queryset

		if self.action.__eq__("list"):
			hasAccount = self.request.query_params.get("has_account")
			if hasAccount and hasAccount.capitalize() in ["True", "False"]:
				queryset = queryset.filter(account__isnull=not (hasAccount.capitalize() == 'True'))

			code = self.request.query_params.get("code")
			queryset = queryset.filter(code__icontains=code) if code else queryset

		return queryset


class SpecialistViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
	queryset = Specialist.objects.select_related("faculty").filter(is_active=True)
	serializer_class = users_serializers.SpecialistSerializer


class StudentViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
	queryset = Student.objects.select_related("faculty", "major", "sclass", "academic_year", "educational_system").filter(is_active=True)
	serializer_class = users_serializers.StudentSerializer
	pagination_class = paginators.StudentPagination

	def get_queryset(self):
		queryset = self.queryset

		if self.action.__eq__("get_activities"):
			return queryset.prefetch_related("registrations")

		if self.action.__eq__("get_points"):
			return queryset.prefetch_related("points")

		return queryset

	def get_permissions(self):
		if self.action in ["get_activities", "get_points"]:
			return [perms.HasInStudentGroup()]

		if self.action in ["get_semesters"]:
			return [permissions.AllowAny()]

		return [perms.HasInAssistantGroup()]

	@action(methods=['get'], detail=True, url_path='semesters')
	def get_semesters(self, request, pk=None):
		student = self.get_object()
		student_academic_year = student.academic_year

		semesters = Semester.objects.filter(
			academic_year__start_date__year__gte=student_academic_year.start_date.year,
			academic_year__start_date__year__lt=student_academic_year.end_date.year
		).order_by("-start_date")

		serializer = schools_serializer.SemesterSerializer(semesters, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(methods=["get"], detail=True, url_path="activities")
	def get_activities(self, request, pk=None):
		registrations = self.get_object().registrations.select_related("activity").filter(is_active=True)

		partd = request.query_params.get("partd")
		if partd and partd.capitalize() in ["True", "False"]:
			registrations = registrations.filter(is_attendance=partd.capitalize())

		name = request.query_params.get("name")
		if name:
			activities = [
				registration.activity
				for registration in registrations
				if name.lower() in registration.activity.name.lower()
			]
		else:
			activities = [registration.activity for registration in registrations]

		paginator = paginators.ActivityPagination()
		page = paginator.paginate_queryset(queryset=activities, request=request)
		if page is not None:
			serializer = activities_serializers.ActivitySerializer(page, many=True)
			return paginator.get_paginated_response(serializer.data)

		serializer = activities_serializers.ActivitySerializer(activities, many=True)
		return Response(data=serializer.data, status=status.HTTP_200_OK)

	@action(methods=["get"], detail=True, url_path="points/(?P<semester_code>[^/.]+)")
	def get_points(self, request, pk=None, semester_code=None):
		semester = get_object_or_404(queryset=Semester, code=semester_code)
		student_summary, training_points = dao.statistics_by_student(semester=semester, student=self.get_object())

		criterion_id = request.query_params.get("criterion_id")
		if criterion_id:
			student_summary["training_points"] = training_points.filter(criterion_id=criterion_id)

		return Response(data=student_summary, status=status.HTTP_200_OK)
