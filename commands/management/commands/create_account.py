import re

import unidecode
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from commands.models import CollectData
from schools.models import Class, Faculty
from users.models import Account
from utils import factory


class Command(BaseCommand):
	default_avatar = factory.get_or_upload_image(ftype="avatar")
	default_password = make_password("user@123")

	def handle(self, *args, **kwargs):
		if self.is_collected_data(app_labels=[Account._meta.app_label], model_names=["account"]):
			self.stdout.write(f"Data for Account already exists {self.style.ERROR('SKIP')}")
		else:
			faculties = Faculty.objects.all()
			for faculty in faculties:
				classes = Class.objects.filter(major__faculty=faculty)
				for sclass in classes:
					students = sclass.students.order_by("?")[:5]
					self.create_accounts_for_users(users=students, password=self.default_password, role=Account.Role.STUDENT)

				assistants = faculty.assistants.order_by("?")[:3]
				specialists = faculty.specialists.all()
				self.create_accounts_for_users(users=assistants, password=self.default_password, role=Account.Role.ASSISTANT)
				self.create_accounts_for_users(users=specialists, password=self.default_password, role=Account.Role.SPECIALIST)

			CollectData.objects.create(app_label=Account._meta.app_label, model_name="account", applied=True)
			self.stdout.write(f"Created account for Student successfully... {self.style.SUCCESS(f'OK')}")
			self.stdout.write(f"Created account for Assistant of successfully... {self.style.SUCCESS(f'OK')}")
			self.stdout.write(f"Created account for Specialist of successfully... {self.style.SUCCESS(f'OK')}")

	def create_accounts_for_users(self, users, password, role):
		for user in users:
			first_name = re.escape(unidecode.unidecode(user.first_name).lower().replace(" ", ""))
			account_data = {"email": f"{user.code}{first_name}@ou.edu.vn", "password": password, "role": role, "avatar": self.default_avatar}

			account = Account.objects.create(**account_data)
			user.account = account
			user.save()

			factory.set_permissions_for_account(account)

	@staticmethod
	def is_collected_data(app_labels, model_names):
		return CollectData.objects.filter(app_label__in=app_labels, model_name__in=model_names, applied=True).exists()
