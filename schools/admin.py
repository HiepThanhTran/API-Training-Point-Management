from base.admin import BaseAdmin, my_admin_site
from schools.models import (
	AcademicYear,
	Class,
	Criterion,
	EducationalSystem,
	Faculty,
	Major,
	Semester,
	TrainingPoint,
)


class EducationalSystemAdmin(BaseAdmin):
	list_display = ["name", "created_date", "updated_date"]
	list_filter = ["created_date", "updated_date"]
	search_fields = ("name",)


class FacultyAdmin(BaseAdmin):
	list_display = ["name", "educational_system", "created_date", "updated_date"]
	list_filter = ["created_date", "updated_date"]
	search_fields = ("name", "educational_system__name")


class MajorAdmin(BaseAdmin):
	list_display = ["name", "faculty", "created_date", "updated_date"]
	list_filter = ["created_date", "updated_date"]
	search_fields = ("name", "faculty__name")


class AcademicYearAdmin(BaseAdmin):
	list_display = ["name", "start_date", "end_date", "created_date", "updated_date"]
	list_filter = ["created_date", "updated_date"]
	search_fields = ("name", "start_date", "end_date")


class ClassAdmin(BaseAdmin):
	list_display = ["name", "major", "academic_year", "created_date", "updated_date"]
	list_filter = ["created_date", "updated_date"]
	search_fields = ("name", "major__name", "academic_year__name")


class SemesterAdmin(BaseAdmin):
	list_display = ["original_name", "code", "academic_year", "start_date", "end_date", "created_date", "updated_date"]
	list_filter = ["created_date", "updated_date"]
	search_fields = ("original_name", "code", "academic_year__name")


class CriterionAdmin(BaseAdmin):
	list_display = ["name", "max_point", "created_date", "updated_date"]
	list_filter = ["max_point", "created_date", "updated_date"]
	search_fields = ("name",)


class TrainingPointAdmin(BaseAdmin):
	list_display = ["student", "criterion", "semester", "point", "created_date", "updated_date"]
	list_filter = ["created_date", "updated_date"]


my_admin_site.register(EducationalSystem, EducationalSystemAdmin)
my_admin_site.register(Faculty, FacultyAdmin)
my_admin_site.register(Major, MajorAdmin)
my_admin_site.register(AcademicYear, AcademicYearAdmin)
my_admin_site.register(Class, ClassAdmin)
my_admin_site.register(Semester, SemesterAdmin)
my_admin_site.register(Criterion, CriterionAdmin)
my_admin_site.register(TrainingPoint, TrainingPointAdmin)
