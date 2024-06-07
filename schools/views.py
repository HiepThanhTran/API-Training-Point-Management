from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.base import paginators, perms
from core.utils import dao, exporter, factory
from schools import serializers as schools_serializers
from schools.models import Class, Criterion, Semester


class ClassViewSet(viewsets.ViewSet, generics.ListAPIView):
	queryset = Class.objects.filter(is_active=True)
	serializer_class = schools_serializers.ClassSerializer
	permission_classes = [perms.HasInAssistantGroup]

	def get_queryset(self):
		queryset = self.queryset

		if self.action.__eq__("list"):
			faculty_id = self.request.query_params.get("faculty_id")
			if faculty_id:
				queryset = queryset.filter(major__faculty_id=faculty_id)

		return queryset


class CriterionViewSet(viewsets.ViewSet, generics.ListAPIView):
	queryset = Criterion.objects.filter(is_active=True)
	serializer_class = schools_serializers.CriterionSerializer


class SemesterViewSet(viewsets.ViewSet, generics.ListAPIView):
	queryset = Semester.objects.filter(is_active=True)
	serializer_class = schools_serializers.SemesterSerializer
	pagination_class = paginators.SemesterPagination


class StatisticsViewSet(viewsets.ViewSet):
	permission_classes = [perms.HasInAssistantGroup]

	@action(methods=["get"], detail=False, url_path="points")
	def get_statistics(self, request, semester_code=None):
		faculty_id, class_id = request.query_params.get("faculty_id"), request.query_params.get("class_id")
		semester, faculty, sclass = factory.find_sfc_by_id(
			semester_code=semester_code,
			faculty_id=faculty_id,
			class_id=class_id
		)

		statistics_data = dao.get_statistics(semester=semester, faculty=faculty, sclass=sclass)[0]
		return Response(data=statistics_data, status=status.HTTP_200_OK)

	@action(methods=["get"], detail=False, url_path="export")
	def export_statistics(self, request, semester_code=None):
		file_format = request.query_params.get("type", "csv")

		if file_format not in ["pdf", "csv"]:
			return Response(status=status.HTTP_400_BAD_REQUEST)

		faculty_id, class_id = request.query_params.get("faculty_id"), request.query_params.get("class_id")
		semester, faculty, sclass = factory.find_sfc_by_id(
			semester_code=semester_code,
			faculty_id=faculty_id,
			class_id=class_id
		)

		return exporter.export_statistics(semester=semester, faculty=faculty, sclass=sclass, file_format=file_format)
