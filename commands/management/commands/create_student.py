import random
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from commands.models import CollectData
from schools.models import Class, AcademicYear
from users.models import Student


class Command(BaseCommand):
	last_names = [
		"Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan",
		"Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"
	]
	middle_names = [
		"Thị", "Văn", "Đình", "Minh", "Xuân", "Hữu", "Thanh", "Ngọc",
		"Kim", "Đức", "Quốc", "Phương", "Quang", "Việt", "Bá", "Tuấn"
	]
	first_names = [
		"Anh", "Bình", "Cường", "Dũng", "Hạnh", "Hải", "Hùng", "Khoa",
		"Lan", "Linh", "Minh", "Nga", "Nghĩa", "Phong", "Phúc", "Quang",
		"Sơn", "Trang", "Tuấn", "Vân", "Việt", "Yến", "Tú", "Thủy"
	]

	date_of_birth_start = datetime(year=2003, month=1, day=1)
	date_of_birth_end = datetime(year=2007, month=12, day=31)

	mobile_prefixes = ["03", "07", "08", "09"]
	landline_prefixes = ["020", "021", "022", "023", "024", "025", "026", "027", "028", "029"]

	def handle(self, *args, **kwargs):
		if self.is_collected_data(app_labels=[Student._meta.app_label], model_names=["student"]):
			self.stdout.write(f"Data for Student already exists {self.style.ERROR('SKIP')}")
		else:
			classes = Class.objects.all()
			for sclass in classes:
				for i in range(1, 11):
					date_of_birth = self.random_date(start=self.date_of_birth_start, end=self.date_of_birth_end)
					major = sclass.major
					faculty = major.faculty
					educational_system = faculty.educational_system
					academic_year = AcademicYear.objects.get(start_date__year=date_of_birth.year + 18)
					data = {
						"sclass": sclass,
						"major": major,
						"faculty": faculty,
						"academic_year": academic_year,
						"date_of_birth": date_of_birth,
						"address": self.random_address(),
						"gender": random.choice(["M", "F"]),
						"phone_number": self.random_phone(),
						"educational_system": educational_system,
						"last_name": random.choice(self.last_names),
						"first_name": random.choice(self.first_names),
						"middle_name": random.choice(self.middle_names),
					}
					student = Student.objects.create(**data)

			CollectData.objects.create(app_label=Student._meta.app_label, model_name="student", applied=True)
			self.stdout.write(f"Created data for Student successfully... {self.style.SUCCESS(f'OK')}")

	def random_phone(self):
		if random.choice([True, False]):
			prefix = random.choice(self.mobile_prefixes)
			phone_number = prefix + "".join(random.choices("0123456789", k=8))
		else:
			prefix = random.choice(self.landline_prefixes)
			phone_number = prefix + "".join(random.choices("0123456789", k=(10 - len(prefix))))
		return phone_number

	@staticmethod
	def random_address():
		streets = ["Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Huế", "Nha Trang", "Vũng Tàu"]
		districts = ["Quận 1", "Quận 2", "Quận 3", "Quận 4", "Quận 5", "Quận 6", "Quận 7", "Quận 8", "Quận 9"]
		random_street = random.choice(streets)
		random_district = random.choice(districts)
		address = f"Số {random.randint(1, 999)}, {random_street}, {random_district}"
		return address

	@staticmethod
	def random_date(start, end):
		return start + timedelta(days=random.randint(0, (end - start).days))

	@staticmethod
	def is_collected_data(app_labels, model_names):
		return CollectData.objects.filter(app_label__in=app_labels, model_name__in=model_names, applied=True).exists()
