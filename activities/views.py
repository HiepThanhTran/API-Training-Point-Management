import csv

from django.db.models import Q
from rest_framework import generics, parsers, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from activities import serializers as activities_serializers
from activities.models import (
	Activity,
	ActivityRegistration,
	Bulletin,
	MissingActivityReport,
)
from base import paginators
from base import perms
from interacts import serializers as interacts_serializers
from users.models import Account, Student
from utils import dao, factory, validations


class BulletinViewSet(viewsets.ViewSet, generics.ListCreateAPIView, generics.RetrieveDestroyAPIView):
	queryset = Bulletin.objects.filter(is_active=True).order_by("-created_date")
	serializer_class = activities_serializers.BulletinSerializer
	pagination_class = paginators.BulletinPagination

	def get_queryset(self):
		queryset = self.queryset

		if self.action.__eq__("list"):
			name = self.request.query_params.get("name")
			queryset = queryset.annotate(unaccented_name=factory.Unaccent('name')).filter(
				Q(unaccented_name__icontains=name) | Q(name__icontains=name)) if name else queryset

		return queryset

	def get_permissions(self):
		if self.action in ["list", "retrieve"]:
			return [permissions.AllowAny()]

		return [perms.HasInAssistantGroup()]

	@action(methods=["post", "delete"], detail=True, url_path="activities")
	def add_or_remove_activity_of_bulletin(self, request, pk=None):
		activity_id = request.data.get("activity_id")
		activity = get_object_or_404(queryset=Activity, pk=activity_id)
		bulletin = self.get_object()
		activity_exists = bulletin.activities.filter(pk=activity.pk).exists()
		if request.method.__eq__("DELETE"):
			if not activity_exists:
				return Response(data={"detail": "Hoạt động không có trong bản tin"}, status=status.HTTP_400_BAD_REQUEST)

			bulletin.activities.remove(activity)
			return Response(status=status.HTTP_204_NO_CONTENT)

		if activity_exists:
			return Response(data={"detail": "Hoạt động đã có trong bản tin"}, status=status.HTTP_400_BAD_REQUEST)

		bulletin.activities.add(activity)
		serializer = activities_serializers.ActivitySerializer(activity)

		return Response(data=serializer.data, status=status.HTTP_200_OK)

	def partial_update(self, request, pk=None):
		serializer = self.get_serializer_class()(instance=self.get_object(), data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		return Response(data=serializer.data, status=status.HTTP_200_OK)


class ActivityViewSet(viewsets.ViewSet, generics.ListCreateAPIView, generics.RetrieveDestroyAPIView):
	queryset = Activity.objects.select_related("bulletin", "faculty", "semester", "criterion").filter(is_active=True).order_by("-created_date")
	serializer_class = activities_serializers.ActivitySerializer
	pagination_class = paginators.ActivityPagination
	parser_classes = [parsers.MultiPartParser, ]

	filter_params = ["bulletin_id", "faculty_id", "semester_id", "criterion_id", "organizer_id"]

	def get_queryset(self):
		queryset = self.queryset

		if self.action.__eq__("list"):
			for param in self.filter_params:
				value = self.request.query_params.get(param)
				queryset = queryset.filter(**{param: value}) if value else queryset

			name = self.request.query_params.get("name")
			queryset = queryset.annotate(unaccented_name=factory.Unaccent("name")).filter(
				Q(unaccented_name__icontains=name) | Q(name__icontains=name)) if name else queryset

			form = self.request.query_params.get("form")
			queryset = queryset.filter(organizational_form__iexact=form) if form else queryset

			start_date = self.request.query_params.get("start_date", "")
			if validations.validate_date_format(start_date):
				queryset = queryset.filter(start_date__gte=start_date)

			end_date = self.request.query_params.get("end_date", "")
			if validations.validate_date_format(end_date):
				queryset = queryset.filter(end_date__lte=end_date)

		queryset = queryset.prefetch_related("comments") if self.action.__eq__("comments") else queryset
		queryset = queryset.prefetch_related("likes") if self.action.__eq__("like_activity") else queryset
		queryset = queryset.prefetch_related("registrations") if self.action.__eq__("register_activity") else queryset
		queryset = queryset.prefetch_related("registrations", "reports") if self.action.__eq__("report_activity") else queryset

		return queryset

	def get_serializer_class(self):
		if self.request.user.is_authenticated:
			if self.request.user.role == Account.Role.STUDENT:
				return activities_serializers.StudentAuthenticatedActivitySerializer

			return activities_serializers.AuthenticatedActivitySerializer

		return self.serializer_class

	def get_permissions(self):
		if self.action in ["create", "update", "partial_update", "destroy", "attendace"]:
			return [perms.HasInAssistantGroup()]

		if self.action in ["register_activity", "report_activity"]:
			return [perms.HasInStudentGroup()]

		if self.action in ["comments", "like_activity"] and self.request.method.__eq__("POST"):
			return [permissions.IsAuthenticated()]

		return [permissions.AllowAny()]

	@action(methods=["get", "post"], detail=True, url_path="comments")
	def comments(self, request, pk=None):
		if request.method.__eq__("POST"):
			content = request.data.get("content")
			if not content:
				return Response(data={"detail": "Nội dung bình luận không được trống"}, status=status.HTTP_400_BAD_REQUEST)

			comment = self.get_object().comments.create(content=content, account=request.user)
			serializer = interacts_serializers.CommentSerializer(comment)

			return Response(data=serializer.data, status=status.HTTP_201_CREATED)

		comments = self.get_object().comments.select_related("account").order_by("-created_date")

		paginator = paginators.CommentPaginators()
		page = paginator.paginate_queryset(queryset=comments, request=request)
		if page is not None:
			serializer = interacts_serializers.CommentSerializer(page, many=True)
			return paginator.get_paginated_response(serializer.data)

		serializer = interacts_serializers.CommentSerializer(comments, many=True)
		return Response(data=serializer.data, status=status.HTTP_200_OK)

	@action(methods=["post"], detail=True, url_path="like")
	def like_activity(self, request, pk=None):
		like, created = self.get_object().likes.get_or_create(account=request.user)
		if not created:
			like.is_active = not like.is_active
			like.save()

		serializer = self.get_serializer_class()(self.get_object(), context={"request": request})
		return Response(data=serializer.data, status=status.HTTP_200_OK)

	@action(methods=["post"], detail=True, url_path="register")
	def register_activity(self, request, pk=None):
		registration, created = self.get_object().registrations.get_or_create(student=request.user.student)
		if not created:
			registration.delete()
			return Response(status=status.HTTP_204_NO_CONTENT)

		serializer = activities_serializers.ActivityRegistrationSerializer(registration)
		return Response(data=serializer.data, status=status.HTTP_201_CREATED)

	@action(methods=["post"], detail=True, url_path="report")
	def report_activity(self, request, pk=None):
		activity = self.get_object()

		try:
			registration = activity.registrations.get(student=request.user.student)

			if registration.is_point_added:
				return Response(data={"detail": "Không thể báo thiếu hoạt động đã được cộng điểm"}, status=status.HTTP_400_BAD_REQUEST)
		except ActivityRegistration.DoesNotExist:
			pass

		content = request.data.get("content", "")
		evidence = request.data.get("evidence", None)

		try:
			missing_report = activity.reports.get(student=request.user.student)
			missing_report.delete()
			return Response(status=status.HTTP_204_NO_CONTENT)
		except MissingActivityReport.DoesNotExist:
			missing_report = activity.reports.create(student=request.user.student, content=content, evidence=evidence)

		serializer = activities_serializers.MissingActivityReportSerializer(missing_report)
		return Response(data=serializer.data, status=status.HTTP_201_CREATED)

	def partial_update(self, request, pk=None):
		serializer = self.get_serializer_class()(self.get_object(), data=request.data, context={"request": request}, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		return Response(data=serializer.data, status=status.HTTP_200_OK)

	@action(methods=["post"], detail=False, url_path="attendance/upload/csv")
	def attendace(self, request):
		file = request.FILES.get("file", None)
		if not file or not file.name.endswith(".csv"):
			return Response(data={"detail": "Vui lòng upload file có định dạng là csv"}, status=status.HTTP_400_BAD_REQUEST)

		csv_data = csv.reader(file.read().decode("utf-8").splitlines())
		next(csv_data)
		for row in csv_data:
			student_code, activity_id = row

			try:
				registration = ActivityRegistration.objects.select_related("student", "activity") \
					.get(student__code=student_code, activity_id=activity_id)
			except (Student.DoesNotExist, Activity.DoesNotExist, ActivityRegistration.DoesNotExist):
				continue
			if registration.is_point_added:
				continue

			dao.update_point_for_student(registration)

		return Response(data={"detail": "Upload file điểm danh thành công"}, status=status.HTTP_200_OK)


class MissingActivityReportViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
	queryset = MissingActivityReport.objects.select_related("student", "activity").filter(is_active=True).order_by("-updated_date")
	serializer_class = activities_serializers.MissingActivityReportSerializer
	pagination_class = paginators.MissingActivityReportPagination
	permission_classes = [perms.HasInAssistantGroup]

	filter_params = ["student_id", "activity_id", "activity__faculty_id"]

	def get_queryset(self):
		queryset = self.queryset

		if self.action.__eq__("list"):
			for param in self.filter_params:
				value = self.request.query_params.get(param)
				queryset = queryset.filter(**{param: value}) if value else queryset

			resolved = self.request.query_params.get("resolved")
			if resolved and resolved.capitalize() in ["True", "False"]:
				queryset = queryset.filter(is_resolved=resolved.capitalize())

		return queryset

	@action(methods=["post"], detail=True, url_path="confirm")
	def confirm_missing_report(self, request, pk=None):
		missing_report = self.get_object()
		if missing_report.is_resolved:
			return Response(data={"detail": "Báo thiếu đã được giải quyết"}, status=status.HTTP_400_BAD_REQUEST)

		registration, _ = ActivityRegistration.objects.get_or_create(student=missing_report.student, activity=missing_report.activity)
		dao.update_point_for_student(registration)

		missing_report.is_resolved = True
		missing_report.save()

		serializer = self.serializer_class(missing_report)
		return Response(data=serializer.data, status=status.HTTP_200_OK)

	@action(methods=["delete"], detail=True, url_path="reject")
	def reject_missing_report(self, request, pk=None):
		missing_report = self.get_object()
		if missing_report.is_resolved is True:
			return Response(data={"detail": "Không thể xóa báo thiếu đã được giải quyết"}, status=status.HTTP_400_BAD_REQUEST)

		missing_report.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)
