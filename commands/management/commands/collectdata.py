import time

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
	def handle(self, *args, **kwargs):
		total_time = time.time()

		call_command("create_basic")
		call_command("create_student")
		call_command("create_account")
		call_command("create_activity_bulletin")
		call_command("create_training_points")
		call_command("create_activity_registration")
		call_command("create_comment_like")

		self.stdout.write(f"- Total time: {self.style.SUCCESS(self.convert_seconds(time.time() - total_time))}")

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
