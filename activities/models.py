from cloudinary.models import CloudinaryField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field

from activities import apps
from base.models import BaseModel


class Bulletin(BaseModel):
	class Meta:
		verbose_name = _("Bulletin")
		verbose_name_plural = _("Bulletins")
		indexes = [models.Index(fields=["poster_type", "poster_id"], )]

	name = models.CharField(max_length=100)
	image = CloudinaryField(null=True, blank=True)
	description = CKEditor5Field("Text", config_name="extends")

	poster_type = models.ForeignKey(to="contenttypes.ContentType", on_delete=models.CASCADE)
	poster_id = models.PositiveIntegerField()
	poster = GenericForeignKey(ct_field="poster_type", fk_field="poster_id")

	def __str__(self):
		return self.name


class Activity(BaseModel):
	class Meta:
		verbose_name = _("Activity")
		verbose_name_plural = _("Activities")
		indexes = [models.Index(fields=["organizer_type", "organizer_id"], )]
		permissions = [
			("upload_attendance_csv", "Can upload attendance csv"),
			("view_participated_list", "Can view participated list"),
			("view_registered_list", "Can view registered list"),
			("view_reported_list", "Can view reported list"),
			("register_activity", "Can register activity"),
			("report_activity", "Can report activity")
		]

	class Type(models.TextChoices):
		ONLINE = "Onl", _("Online")
		OFFLINE = "Off", _("Offline")

	name = models.CharField(max_length=100)
	participant = models.CharField(max_length=20)
	start_date = models.DateField()
	end_date = models.DateField()
	location = models.CharField(max_length=255)
	point = models.PositiveSmallIntegerField()
	image = CloudinaryField(null=True, blank=True)
	description = CKEditor5Field("Text", config_name="extends")
	organizational_form = models.CharField(max_length=3, choices=Type.choices, default=Type.OFFLINE)

	organizer_type = models.ForeignKey(to="contenttypes.ContentType", on_delete=models.CASCADE)
	organizer_id = models.PositiveIntegerField()
	organizer = GenericForeignKey(ct_field="organizer_type", fk_field="organizer_id")

	faculty = models.ForeignKey(to="schools.Faculty", on_delete=models.CASCADE, related_name="activities")
	semester = models.ForeignKey(to="schools.Semester", on_delete=models.CASCADE, related_name="activities")
	bulletin = models.ForeignKey(to=Bulletin, blank=True, null=True, on_delete=models.SET_NULL, related_name="activities")
	criterion = models.ForeignKey(to="schools.Criterion", blank=True, null=True, on_delete=models.SET_NULL, related_name="activities")
	participants = models.ManyToManyField("users.Student", related_name="activities", through="ActivityRegistration")

	def __str__(self):
		return self.name


class ActivityRegistration(BaseModel):
	class Meta:
		db_table = "{}_activity_registration".format(apps.ActivitiesConfig.name)
		verbose_name = _("Activity Registration")
		verbose_name_plural = _("Activity Registrations")
		unique_together = ("student", "activity",)

	is_attendance = models.BooleanField(default=False)
	is_point_added = models.BooleanField(default=False)

	activity = models.ForeignKey(to=Activity, on_delete=models.CASCADE, related_name="registrations")
	student = models.ForeignKey(to="users.Student", on_delete=models.CASCADE, related_name="registrations")

	def __str__(self):
		return f"{self.student} - {self.activity}"


class MissingActivityReport(BaseModel):
	class Meta:
		db_table = "{}_missing_activity_report".format(apps.ActivitiesConfig.name)
		verbose_name = _("Missing Activity Report")
		verbose_name_plural = _("Missing Activity Reports")
		unique_together = ("student", "activity",)
		permissions = [
			("resolve_deficiency", "Can resolve deficiency"),
			("view_deficiency_list", "Can view deficiency list")
		]

	is_resolved = models.BooleanField(default=False)
	evidence = CloudinaryField(null=True, blank=True)
	content = CKEditor5Field("Text", config_name="extends", null=True, blank=True)

	activity = models.ForeignKey(to=Activity, on_delete=models.CASCADE, related_name="reports")
	student = models.ForeignKey(to="users.Student", on_delete=models.CASCADE, related_name="reports")

	def __str__(self):
		return f"{self.student} - {self.activity}"
