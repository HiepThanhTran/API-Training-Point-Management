from django.core.management.base import BaseCommand

from activities.models import Activity, ActivityRegistration
from commands.models import CollectData
from users.models import Student


class Command(BaseCommand):
	def handle(self, *args, **kwargs):
		if self.is_collected_data(app_labels=[ActivityRegistration._meta.app_label], model_names=["activityregistration"]):
			self.stdout.write(f"Data for ActivityRegistration already exists {self.style.ERROR('SKIP')}")
		else:
			activities = Activity.objects.all()
			self.create_activity_registrations(activities)

			CollectData.objects.create(app_label=ActivityRegistration._meta.app_label, model_name="activityregistration", applied=True)
			self.stdout.write(f"Created data for ActivityRegistration successfully... {self.style.SUCCESS(f'OK')}")

	@staticmethod
	def create_activity_registrations(activities):
		activity_registrations = []
		for activity in activities:
			students = Student.objects.filter(account__isnull=False).order_by("?")[:10]
			for student in students:
				activity_registrations.append(ActivityRegistration(activity=activity, student=student))

		return ActivityRegistration.objects.bulk_create(activity_registrations)

	@staticmethod
	def is_collected_data(app_labels, model_names):
		return CollectData.objects.filter(app_label__in=app_labels, model_name__in=model_names, applied=True).exists()
