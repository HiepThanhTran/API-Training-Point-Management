from rest_framework import pagination


class UserPagination(pagination.PageNumberPagination):
	page_size = 10


class AssistantPagination(pagination.PageNumberPagination):
	page_size = 5


class StudentPagination(pagination.PageNumberPagination):
	page_size = 5


class BulletinPagination(pagination.PageNumberPagination):
	page_size = 4


class ActivityPagination(pagination.PageNumberPagination):
	page_size = 4


class MissingActivityReportPagination(pagination.PageNumberPagination):
	page_size = 4


class FacultyPagination(pagination.PageNumberPagination):
	page_size = 5


class SemesterPagination(pagination.PageNumberPagination):
	page_size = 3


class CommentPaginators(pagination.PageNumberPagination):
	page_size = 5
