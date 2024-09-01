import json

from django.core.management.base import BaseCommand

from commands.models import CollectData
from interacts.models import Comment, Like
from utils.configs import MODEL_DATA_PATH


class Command(BaseCommand):
	def handle(self, *args, **kwargs):
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

			CollectData.objects.create(app_label=model_instance._meta.app_label, model_name=model_name.lower(), applied=True)
			self.stdout.write(f"Created data for {model_name} successfully... {self.style.SUCCESS(f'OK')}")

	@staticmethod
	def is_collected_data(app_labels, model_names):
		return CollectData.objects.filter(app_label__in=app_labels, model_name__in=model_names, applied=True).exists()
