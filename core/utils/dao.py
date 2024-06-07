from django.db.models import Case, Count, F, IntegerField, Sum, When

from core.utils.configs import ACHIEVEMENTS
from schools.models import TrainingPoint


def get_statistics(semester=None, faculty=None, sclass=None):
	if faculty and not sclass:
		return statistics_by_entity(semester=semester, entity=faculty, entity_type="faculty")

	return statistics_by_entity(semester=semester, entity=sclass, entity_type="class")


def statistics_by_entity(semester=None, entity=None, entity_type="class"):
	achievements = {achievement: 0 for achievement in ACHIEVEMENTS}
	total_students, total_points = 0, 0
	students_summary_list = []

	students = entity.students.prefetch_related("points").all()
	for student in students:
		student_summary = statistics_by_student(semester=semester, student=student)[0]
		total_students += 1
		total_points += student_summary["total_points"]
		achievements[student_summary["achievement"]] += 1
		students_summary_list.append(student_summary)
	average_points = round(total_points / total_students if total_students > 0 else 0, 2)

	statistics_data = {
		"id": entity.id,
		"name": entity.name,
		"total_students": total_students,
		"total_points": total_points,
		"average_points": average_points,
		"achievements": achievements,
	}

	if entity_type == "faculty":
		statistics_data["total_classes"] = entity.majors.aggregate(total_classes=Count("classes"))["total_classes"]

	return statistics_data, students_summary_list


def statistics_by_student(semester=None, student=None):
	training_points = (
		student.points.filter(semester=semester)
		.select_related("criterion")
		.values("id", "point")
		.annotate(
			max_point=F("criterion__max_point"),
			criterion=F("criterion__name"),
			adjusted_point=Case(
				When(point__gt=F("max_point"), then=F("max_point")),
				default=F("point"),
				output_field=IntegerField(),
			),
		)
		.order_by("criterion__name")
	)
	total_points = training_points.aggregate(total_points=Sum("adjusted_point", default=0))["total_points"]

	statistics_data = {
		"id": student.id,
		"full_name": student.full_name,
		"code": student.code,
		"total_points": total_points,
		"achievement": get_achievement_by_points(total_points),
		"training_points": training_points,
	}

	return statistics_data, training_points


def get_achievement_by_points(total_points):
	if total_points >= 90:
		return "Xuất sắc"
	if total_points >= 80:
		return "Giỏi"
	if total_points >= 65:
		return "Khá"
	if total_points >= 50:
		return "Trung bình"
	if total_points >= 35:
		return "Yếu"

	return "Kém"


def update_point_for_student(registration):
	training_point = TrainingPoint.objects.get_or_create(
		student=registration.student,
		semester=registration.activity.semester,
		criterion=registration.activity.criterion,
	)[0]
	training_point.point = F("point") + registration.activity.point
	training_point.save()

	registration.is_point_added = True
	registration.is_attendance = True
	registration.save()

	return training_point
