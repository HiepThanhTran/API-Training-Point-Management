from django.db import models
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field

from core.base.models import BaseModel
from schools import apps


class EducationalSystem(BaseModel):
	class Meta:
		db_table = "{}_educational_system".format(apps.SchoolsConfig.name)
		verbose_name = _("Educational System")
		verbose_name_plural = _("Educational Systems")

	name = models.CharField(max_length=30)

	def __str__(self):
		return self.name


class Faculty(BaseModel):
	class Meta:
		verbose_name = _("Faculty")
		verbose_name_plural = _("Faculties")

	name = models.CharField(max_length=50)

	educational_system = models.ForeignKey(to=EducationalSystem, on_delete=models.CASCADE, related_name="faculties")

	def __str__(self):
		return self.name


class Major(BaseModel):
	class Meta:
		verbose_name = _("Major")
		verbose_name_plural = _("Majors")

	name = models.CharField(max_length=50)

	faculty = models.ForeignKey(to=Faculty, on_delete=models.CASCADE, related_name="majors")

	def __str__(self):
		return self.name


class AcademicYear(BaseModel):
	class Meta:
		db_table = "{}_academic_year".format(apps.SchoolsConfig.name)
		verbose_name = _("Academic Year")
		verbose_name_plural = _("Academic Years")

	name = models.CharField(max_length=20)
	start_date = models.DateField()
	end_date = models.DateField()

	def __str__(self):
		return f"{self.start_date.year}-{self.end_date.year}"


class Class(BaseModel):
	class Meta:
		verbose_name = _("Class")
		verbose_name_plural = _("Classes")

	name = models.CharField(max_length=50)

	major = models.ForeignKey(to=Major, on_delete=models.CASCADE, related_name="classes")
	academic_year = models.ForeignKey(to=AcademicYear, on_delete=models.CASCADE, related_name="classes")

	def __str__(self):
		return self.name


class Semester(BaseModel):
	class Meta:
		verbose_name = _("Semester")
		verbose_name_plural = _("Semesters")

	class Semesters(models.IntegerChoices):
		SEMESTER_FIRST = 1, _("Học kỳ 1")
		SEMESTER_SECOND = 2, _("Học kỳ 2")
		SEMESTER_THIRD = 3, _("Học kỳ 3")

	start_date = models.DateField()
	end_date = models.DateField()
	short_name = models.PositiveSmallIntegerField(choices=Semesters.choices)
	code = models.CharField(max_length=3, null=True, blank=True, unique=True, db_index=True, editable=False)

	academic_year = models.ForeignKey(to=AcademicYear, on_delete=models.CASCADE, related_name="semesters")
	students = models.ManyToManyField("users.Student", related_name="semesters", through="SemesterOfStudent")

	def __str__(self):
		return f"{self.original_name} - {self.academic_year}"

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)

		if self.code is None:
			self.code = self.generate_code()
			self.save()

	@property
	def original_name(self):
		return self.Semesters.labels[self.Semesters.values.index(self.short_name)]

	def generate_code(self):
		return f"{str(self.academic_year.start_date.year)[-2:]}{self.short_name}"


class SemesterOfStudent(BaseModel):
	class Meta:
		db_table = "{}_semester_of_student".format(apps.SchoolsConfig.name)
		verbose_name = _("Semester Of Student")
		verbose_name_plural = _("Semester Of Student")
		unique_together = ("semester", "student")

	semester = models.ForeignKey(to=Semester, on_delete=models.CASCADE)
	student = models.ForeignKey(to="users.Student", on_delete=models.CASCADE)

	def __str__(self):
		return f"{self.student} - {self.semester}"


class Criterion(BaseModel):
	class Meta:
		verbose_name = _("Criterion")
		verbose_name_plural = _("Criterions")

	name = models.CharField(max_length=20)
	max_point = models.PositiveSmallIntegerField()
	description = CKEditor5Field("Text", config_name="extends")

	def __str__(self):
		return self.name


class TrainingPoint(BaseModel):
	class Meta:
		db_table = "{}_training_point".format(apps.SchoolsConfig.name)
		verbose_name = _("Training Point")
		verbose_name_plural = _("Training Points")
		unique_together = ["semester", "criterion", "student"]
		permissions = [
			("view_faculty_statistics", "Can view faculty statistics"),
			("export_faculty_statistics", "Can export faculty statistics"),
			("view_class_statistics", "Can view class statistics"),
			("export_class_statistics", "Can export class statistics")
		]

	point = models.PositiveSmallIntegerField(default=0)

	semester = models.ForeignKey(to=Semester, on_delete=models.CASCADE, related_name="points")
	criterion = models.ForeignKey(to=Criterion, on_delete=models.CASCADE, related_name="points")
	student = models.ForeignKey(to="users.Student", on_delete=models.CASCADE, related_name="points")

	def __str__(self):
		return f"{self.student} - {self.criterion} - {self.semester}"
