import datetime
import json

from django.core.management.base import BaseCommand

from activities.models import Activity, Bulletin
from commands.models import CollectData
from users.models import Assistant
from utils import factory
from utils.configs import MODEL_DATA_PATH


class Command(BaseCommand):
	bulletin_cover = factory.get_or_upload_image(ftype="bulletin")
	activity_image = factory.get_or_upload_image(ftype="activity")
	date_fields = ["start_date", "end_date"]

	def handle(self, *args, **kwargs):
		models_list = {
			"Bulletin": Bulletin,
			"Activity": Activity
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

				if model_name.__eq__("Bulletin"):
					data["poster"] = Assistant.objects.filter(account__isnull=False).order_by("?").first()
					data["image"] = self.bulletin_cover

				if model_name.__eq__("Activity"):
					data["organizer"] = Assistant.objects.filter(account__isnull=False).order_by("?").first()
					data["image"] = self.activity_image

				obj = model_instance.objects.create(**data)

			CollectData.objects.create(app_label=model_instance._meta.app_label, model_name=model_name.lower(), applied=True)
			self.stdout.write(f"Created data for {model_name} successfully... {self.style.SUCCESS(f'OK')}")

	@staticmethod
	def is_collected_data(app_labels, model_names):
		return CollectData.objects.filter(app_label__in=app_labels, model_name__in=model_names, applied=True).exists()
