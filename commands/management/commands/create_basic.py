import datetime
import json

from django.core.management.base import BaseCommand

from commands.models import CollectData
from schools.models import AcademicYear, Class, Criterion, EducationalSystem, Faculty, Major, Semester
from users.models import Account, Administrator, Assistant, Specialist
from utils.configs import MODEL_DATA_PATH


class Command(BaseCommand):
	date_fields = ["start_date", "end_date", "date_of_birth"]

	def handle(self, *args, **kwargs):
		if self.is_collected_data(app_labels=[Administrator._meta.app_label], model_names=["administrator"]):
			self.stdout.write(f"Data for Administrator already exists {self.style.ERROR('SKIP')}")
		else:
			Account.objects.create_superuser(email="admin@gmail.com", password="admin@123")
			CollectData.objects.create(app_label=Administrator._meta.app_label, model_name="administrator", applied=True)
			self.stdout.write(f"Created account for Administrator successfully... {self.style.SUCCESS(f'OK')}")

		models_list = {
			"EducationalSystem": EducationalSystem,
			"Faculty": Faculty,
			"Major": Major,
			"AcademicYear": AcademicYear,
			"Class": Class,
			"Criterion": Criterion,
			"Semester": Semester,

			"Assistant": Assistant,
			"Specialist": Specialist,
		}
		for model_name, model_instance in models_list.items():
			if self.is_collected_data(app_labels=[model_instance._meta.app_label], model_names=[model_name.lower()]):
				self.stdout.write(f"Data for {model_name} already exists {self.style.ERROR('SKIP')}")
				continue

			f = open(MODEL_DATA_PATH[model_name])
			model_data = json.load(f)
			for data in model_data:
				for date_field in self.date_fields:
					if date_field in data:
						data[date_field] = datetime.datetime.strptime(data[date_field], "%Y-%m-%d").date()

				obj = model_instance.objects.create(**data)

			CollectData.objects.create(app_label=model_instance._meta.app_label, model_name=model_name.lower(), applied=True)
			self.stdout.write(f"Created data for {model_name} successfully... {self.style.SUCCESS(f'OK')}")

	@staticmethod
	def is_collected_data(app_labels, model_names):
		return CollectData.objects.filter(app_label__in=app_labels, model_name__in=model_names, applied=True).exists()
