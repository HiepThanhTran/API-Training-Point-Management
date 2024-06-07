import datetime
import json
import random
import re
import time

import unidecode
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction

from activities.models import Activity, ActivityRegistration, Bulletin
from commands.models import CollectData
from core.utils import factory
from core.utils.configs import MODEL_DATA_PATH
from interacts.models import Comment, Like
from schools.models import (
    AcademicYear,
    Class,
    Criterion,
    EducationalSystem,
    Faculty,
    Major,
    Semester,
    SemesterOfStudent,
    TrainingPoint,
)
from users.models import Account, Administrator, Assistant, Specialist, Student


class Command(BaseCommand):
	bulletin_cover = factory.get_or_upload_image(ftype="bulletin")
	activity_image = factory.get_or_upload_image(ftype="activity")
	default_avatar = factory.get_or_upload_image(ftype="avatar")
	default_password = make_password("user@123")

	def handle(self, *args, **kwargs):
		date_fields = ["start_date", "end_date", "date_of_birth"]
		collect_data_list = []
		total_time = time.time()
		models_list = {
			"EducationalSystem": EducationalSystem,
			"Faculty": Faculty,
			"Major": Major,
			"AcademicYear": AcademicYear,
			"Class": Class,
			"Criterion": Criterion,
			"Semester": Semester,

			"Student": Student,
			"Assistant": Assistant,
			"Specialist": Specialist,

			"Bulletin": Bulletin,
			"Activity": Activity,
		}
		if self.is_collected_data(app_labels=[Administrator._meta.app_label], model_names=["administrator"]):
			self.stdout.write(f"Data for Administrator already exists {self.style.ERROR('SKIP')}")
		else:
			Account.objects.create_superuser(email="admin@gmail.com", password="admin@123")
			collect_data_list.append(CollectData(app_label=Administrator._meta.app_label, model_name="administrator", applied=True))
			self.stdout.write(f"Created account for Administrator successfully... {self.style.SUCCESS(f'OK')}")

		for model_name, model_instance in models_list.items():
			if self.is_collected_data(app_labels=[model_instance._meta.app_label], model_names=[model_name.lower()]):
				self.stdout.write(f"Data for {model_name} already exists {self.style.ERROR('SKIP')}")
				continue

			f = open(MODEL_DATA_PATH[model_name])
			model_data = json.load(f)
			for data in model_data:
				for date_field in date_fields:
					if date_field in data:
						data[date_field] = datetime.datetime.strptime(data[date_field], "%Y-%m-%d").date()

				if model_name.__eq__("Bulletin"):
					poster = Assistant.objects.order_by("?").first()
					data["poster"] = poster
					data["image"] = self.bulletin_cover

				if model_name.__eq__("Activity"):
					organizer = Assistant.objects.order_by("?").first()
					data["organizer"] = organizer
					data["image"] = self.activity_image

				obj = model_instance.objects.create(**data)

			collect_data_list.append(CollectData(app_label=model_instance._meta.app_label, model_name=model_name.lower(), applied=True))
			self.stdout.write(f"Created data for {model_name} successfully... {self.style.SUCCESS(f'OK')}")

		# SemesterOfStudent && TrainingPoint
		if self.is_collected_data(app_labels=[SemesterOfStudent._meta.app_label, TrainingPoint._meta.app_label], model_names=["semesterofstudent", "trainingpoint"]):
			self.stdout.write(f"Data for SemesterOfStudent already exists {self.style.ERROR('SKIP')}")
		else:
			semesters = Semester.objects.prefetch_related("students").all()
			students = Student.objects.all()
			self.create_semester_of_student(semesters=semesters, students=students)
			self.create_training_point_for_students(students=students, semesters=semesters, criterions=Criterion.objects.all())

			collect_data_list.append(CollectData(app_label=SemesterOfStudent._meta.app_label, model_name="semesterofstudent", applied=True))
			collect_data_list.append(CollectData(app_label=TrainingPoint._meta.app_label, model_name="trainingpoint", applied=True))
			self.stdout.write(f"Created data for SemesterOfStudent successfully... {self.style.SUCCESS(f'OK')}")
			self.stdout.write(f"Created data for TrainingPoint successfully... {self.style.SUCCESS(f'OK')}")

		# Account
		if self.is_collected_data(app_labels=[Account._meta.app_label], model_names=["account"]):
			self.stdout.write(f"Data for Account already exists {self.style.ERROR('SKIP')}")
		else:
			faculties = Faculty.objects.prefetch_related("students", "assistants", "specialists").all()
			for faculty in faculties:
				classes = Class.objects.filter(major__faculty=faculty)
				for sclass in classes:
					students = sclass.students.select_related("account").order_by("?")[:15]
					self.create_accounts_for_users(users=students, password=self.default_password, role=Account.Role.STUDENT)

				assistants = faculty.assistants.select_related("account").order_by("?")[:2]
				specialists = faculty.specialists.select_related("account").all()
				self.create_accounts_for_users(users=assistants, password=self.default_password, role=Account.Role.ASSISTANT)
				self.create_accounts_for_users(users=specialists, password=self.default_password, role=Account.Role.SPECIALIST)

			collect_data_list.append(CollectData(app_label=Account._meta.app_label, model_name="account", applied=True))
			self.stdout.write(f"Created account for Student successfully... {self.style.SUCCESS(f'OK')}")
			self.stdout.write(f"Created account for Assistant of successfully... {self.style.SUCCESS(f'OK')}")
			self.stdout.write(f"Created account for Specialist of successfully... {self.style.SUCCESS(f'OK')}")

		# ActivityRegistration
		if self.is_collected_data(app_labels=[ActivityRegistration._meta.app_label], model_names=["activityregistration"]):
			self.stdout.write(f"Data for ActivityRegistration already exists {self.style.ERROR('SKIP')}")
		else:
			activities = Activity.objects.prefetch_related("participants").all()
			classes = Class.objects.prefetch_related("students").all()
			self.create_activity_registrations(activities=activities, classes=classes)

			collect_data_list.append(CollectData(app_label=ActivityRegistration._meta.app_label, model_name="activityregistration", applied=True))
			self.stdout.write(f"Created data for ActivityRegistration successfully... {self.style.SUCCESS(f'OK')}")

		models_list = {
			"Comment": Comment,
			"Like": Like,
		}
		for model_name, model_instance in models_list.items():
			if self.is_collected_data(app_labels=[model_instance._meta.app_label], model_names=[model_name.lower()]):
				self.stdout.write(f"Data for {model_name} already exists {self.style.ERROR('SKIP')}")
				continue

			f = open(MODEL_DATA_PATH[model_name])
			model_data = json.load(f)
			for data in model_data:
				obj = model_instance.objects.create(**data)

			collect_data_list.append(CollectData(app_label=model_instance._meta.app_label, model_name=model_name.lower(), applied=True))
			self.stdout.write(f"Created data for {model_name} successfully... {self.style.SUCCESS(f'OK')}")

		CollectData.objects.bulk_create(collect_data_list)
		self.stdout.write(f"- Total time: {self.style.SUCCESS(self.convert_seconds(time.time() - total_time))}")

	@staticmethod
	def is_collected_data(app_labels, model_names):
		return CollectData.objects.filter(app_label__in=app_labels, model_name__in=model_names, applied=True).exists()

	@staticmethod
	def create_semester_of_student(semesters, students):
		semester_of_student = [
			SemesterOfStudent(semester=semester, student=student)
			for semester in semesters
			for student in students
		]
		SemesterOfStudent.objects.bulk_create(semester_of_student)

	@staticmethod
	def create_training_point_for_students(students, semesters, criterions):
		training_points = [
			TrainingPoint(student=student, semester=semester, criterion=criterion, point=random.randint(a=0, b=80))
			for criterion in criterions
			for semester in semesters
			for student in students
		]
		TrainingPoint.objects.bulk_create(training_points)

	def create_accounts_for_users(self, users, password, role):
		for user in users:
			first_name = re.escape(unidecode.unidecode(user.first_name).lower().replace(" ", ""))
			account_data = {"email": f"{user.code}{first_name}@ou.edu.vn", "password": password, "role": role, "avatar": self.default_avatar}

			account = Account.objects.create(**account_data)
			user.account = account
			user.save()

			factory.set_permissions_for_account(account)

	@staticmethod
	def create_activity_registrations(activities, classes):
		activity_registrations = []
		for activity in activities:
			for sclass in classes:
				students = sclass.students.filter(account__isnull=False).order_by("?")[:10]
				for student in students:
					activity_registrations.append(ActivityRegistration(activity=activity, student=student))

		return ActivityRegistration.objects.bulk_create(activity_registrations)

	@staticmethod
	def convert_seconds(seconds=0):
		if seconds >= 3600:
			hours = seconds // 3600
			minutes = (seconds % 3600) // 60
			remaining_seconds = round(seconds % 60, 2)
			return f"{hours}h {minutes}m {remaining_seconds}s"

		if seconds >= 60:
			minutes = seconds // 60
			remaining_seconds = round(seconds % 60, 2)
			return f"{minutes}m {remaining_seconds}s"

		return f"{round(seconds, 2)}s"
