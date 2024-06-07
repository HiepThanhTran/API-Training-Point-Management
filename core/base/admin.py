from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.template.response import TemplateResponse
from django.urls import path

from core.utils import dao
from schools.models import Faculty, Semester


class MyAdminSite(admin.AdminSite):
    site_header = "TPM Administator"
    site_title = "TPM site admin"
    index_title = "Quản lý điểm rèn luyện"

    def get_urls(self):
        return [
            path("statistics/", self.admin_view(view=self.statistics_view, cacheable=True), name='statistics')
        ] + super().get_urls()

    def statistics_view(self, request):
        semesters = Semester.objects.select_related('academic_year').order_by("-start_date")
        faculties = Faculty.objects.order_by("name")
        classes = []
        if faculties:
            for major in faculties[0].majors.all():
                for sclass in major.classes.order_by("name"):
                    classes.append(sclass)

        statistics_faculty, _ = dao.get_statistics(semester=semesters[0], faculty=faculties[0])
        statistics_class, _ = dao.get_statistics(semester=semesters[0], sclass=classes[0])

        return TemplateResponse(
            request=request, template="admin/statistics.html",
            context={
                "faculties": faculties,
                "classes": classes,
                "semesters": semesters,
                "statistics_faculty": statistics_faculty,
                "statistics_class": statistics_class,
                "site_header": "Quản lý điểm rèn luyện",
                "title": "Thống kê điểm rèn luyện theo khoa và lớp",
            },
        )


my_admin_site = MyAdminSite(name="Training Point Management")

my_admin_site.register(Group)
my_admin_site.register(Permission)
