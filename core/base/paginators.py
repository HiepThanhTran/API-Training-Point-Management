from rest_framework import pagination


class StudentPagination(pagination.PageNumberPagination):
    page_size = 5


class BulletinPagination(pagination.PageNumberPagination):
    page_size = 4


class ActivityPagination(pagination.PageNumberPagination):
    page_size = 4


class MissingActivityReportPagination(pagination.PageNumberPagination):
    page_size = 4
    

class SemesterPagination(pagination.PageNumberPagination):
    page_size = 3


class CommentPaginators(pagination.PageNumberPagination):
    page_size = 5
