import random

from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext_lazy as _

from activities.models import Activity
from core.base.models import BaseModel


class Account(AbstractUser):
	class Meta:
		verbose_name = _("Account")
		verbose_name_plural = _("Accounts")
		permissions = [
			("create_student_account", "Can create student account"),
			("create_assistant_account", "Can create assistant account"),
			("create_specialist_account", "Can create specialist account")
		]

	class Role(models.TextChoices):
		ADMINISTRATOR = "AD", _("Administrator")
		STUDENT = "STU", _("Sinh viên")
		ASSISTANT = "ASST", _("Trợ lý sinh viên")
		SPECIALIST = "SPC", _("Chuyên viên cộng tác sinh viên")

	email = models.EmailField(unique=True)
	avatar = CloudinaryField(null=True, blank=True)
	role = models.CharField(max_length=4, choices=Role.choices, null=True, default=Role.STUDENT)

	username = None
	first_name = None
	last_name = None

	from users.managers import AccountManager

	objects = AccountManager()

	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = []

	def __str__(self):
		return self.email

	@property
	def original_role(self):
		return self.Role.labels[self.Role.values.index(self.role)]

	def has_in_group(self, name=None):
		return self.groups.filter(name=name).exists()


class User(BaseModel):
	class Meta:
		abstract = True

	class Gender(models.TextChoices):
		MALE = "M", _("Nam")
		FEMALE = "F", _("Nữ")
		UNKNOWN = "U", _("Khác")

	first_name = models.CharField(max_length=50)
	middle_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	date_of_birth = models.DateField()
	address = models.CharField(max_length=255)
	phone_number = models.CharField(max_length=15, null=True)
	gender = models.CharField(max_length=1, choices=Gender.choices, default=Gender.UNKNOWN)
	code = models.CharField(max_length=10, null=True, blank=True, unique=True, db_index=True, editable=False)

	account = models.OneToOneField(to=Account, null=True, blank=True, on_delete=models.SET_NULL, related_name="%(class)s", )
	faculty = models.ForeignKey(to="schools.Faculty", null=True, on_delete=models.SET_NULL, related_name="%(class)ss", )

	def __str__(self):
		return f"{self.code} - {self.full_name}"

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)

		if self.code is None:
			self.code = self.generate_code()
			self.save()

	@property
	def full_name(self):
		return f"{self.last_name} {self.middle_name} {self.first_name}"

	def generate_code(self):
		raise NotImplemented()


class Officer(User):
	class Meta:
		abstract = True

	bulletins = GenericRelation(
		to=Activity,
		related_name="officers",
		related_query_name="officers",
		content_type_field="poster_type",
		object_id_field="poster_id"
	)

	activities = GenericRelation(
		to=Activity,
		related_name="officers",
		related_query_name="officers",
		content_type_field="organizer_type",
		object_id_field="organizer_id"
	)

	def generate_code(self):
		return f"{self.faculty.id:02d}{random.randint(0, 99):02d}{self.id:06d}"


class Administrator(Officer):
	class Meta:
		verbose_name = _("Administrator")
		verbose_name_plural = _("Administrators")

	def generate_code(self):
		return f"AD{random.randint(0, 99):02d}{self.id:06d}"


class Specialist(Officer):
	class Meta:
		verbose_name = _("Specialist")
		verbose_name_plural = _("Specialists")

	job_title = models.CharField(max_length=50, null=True, blank=True)
	academic_degree = models.CharField(max_length=50, null=True, blank=True)


class Assistant(Officer):
	class Meta:
		verbose_name = _("Assistant")
		verbose_name_plural = _("Assistants")


class Student(User):
	class Meta:
		verbose_name = _("Student")
		verbose_name_plural = _("Students")

	major = models.ForeignKey(to="schools.Major", null=True, on_delete=models.SET_NULL, related_name="students")
	sclass = models.ForeignKey(to="schools.Class", null=True, on_delete=models.SET_NULL, related_name="students")
	academic_year = models.ForeignKey(to="schools.AcademicYear", null=True, on_delete=models.SET_NULL, related_name="students", )
	educational_system = models.ForeignKey(to="schools.EducationalSystem", null=True, on_delete=models.SET_NULL, related_name="students", )

	def generate_code(self):
		return f"{str(self.academic_year.start_date.year)[-2:]}{self.faculty.id:02d}{self.id:06d}"
