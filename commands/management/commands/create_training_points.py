import random

from django.core.management.base import BaseCommand

from commands.models import CollectData
from schools.models import Criterion, Semester, SemesterOfStudent, TrainingPoint
from users.models import Student


class Command(BaseCommand):
	def handle(self, *args, **kwargs):
		if self.is_collected_data(app_labels=[TrainingPoint._meta.app_label], model_names=["trainingpoint"]):
			self.stdout.write(f"Data for TrainingPoint already exists {self.style.ERROR('SKIP')}")
		else:
			students = Student.objects.all()
			semesters = Semester.objects.all()
			self.create_training_point_for_students(students=students, semesters=semesters, criterions=Criterion.objects.all())

			CollectData.objects.create(app_label=TrainingPoint._meta.app_label, model_name="trainingpoint", applied=True)
			self.stdout.write(f"Created data for TrainingPoint successfully... {self.style.SUCCESS(f'OK')}")

		if self.is_collected_data(app_labels=[SemesterOfStudent._meta.app_label], model_names=["semesterofstudent"]):
			self.stdout.write(f"Data for SemesterOfStudent already exists {self.style.ERROR('SKIP')}")
		else:
			students = Student.objects.all()
			semesters = Semester.objects.all()
			self.create_semester_of_student(semesters=semesters, students=students)

			CollectData.objects.create(app_label=SemesterOfStudent._meta.app_label, model_name="semesterofstudent", applied=True)
			self.stdout.write(f"Created data for SemesterOfStudent successfully... {self.style.SUCCESS(f'OK')}")

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
