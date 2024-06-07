import os

from django.contrib.auth.models import Permission

from core import settings

MODEL_DATA_PATH = {
	'EducationalSystem': os.path.join(settings.BASE_DIR, 'static/data/schools/educational_system_data.json'),
	'Faculty': os.path.join(settings.BASE_DIR, 'static/data/schools/faculty_data.json'),
	'Major': os.path.join(settings.BASE_DIR, 'static/data/schools/major_data.json'),
	'AcademicYear': os.path.join(settings.BASE_DIR, 'static/data/schools/academic_year_data.json'),
	'Class': os.path.join(settings.BASE_DIR, 'static/data/schools/class_data.json'),
	'Semester': os.path.join(settings.BASE_DIR, 'static/data/schools/semester_data.json'),
	'Criterion': os.path.join(settings.BASE_DIR, 'static/data/schools/criterion_data.json'),

	'Student': os.path.join(settings.BASE_DIR, 'static/data/users/student_data.json'),
	'Assistant': os.path.join(settings.BASE_DIR, 'static/data/users/assistant_data.json'),
	'Specialist': os.path.join(settings.BASE_DIR, 'static/data/users/specialist_data.json'),

	'Bulletin': os.path.join(settings.BASE_DIR, 'static/data/activities/bulletin_data.json'),
	'Activity': os.path.join(settings.BASE_DIR, 'static/data/activities/activity_data.json'),

	'Comment': os.path.join(settings.BASE_DIR, 'static/data/interacts/comment_data.json'),
	'Like': os.path.join(settings.BASE_DIR, 'static/data/interacts/like_data.json'),
}

SPECIALIST_PERMISSIONS = [
	"create_assistant_account",
	"view_faculty_statistics",
	"export_faculty_statistics",
]

ASSISTANT_PERMISSIONS = [
	"view_class_statistics",
	"export_class_statistics",
	"upload_attendance_csv",
	"view_reported_list",
	"view_deficiency_list",
	"resolve_deficiency",
	"add_activity",
	"add_bulletin",
]

STUDENT_PERMISSIONS = [
	"register_activity",
	"report_activity",
	"view_participated_list",
	"view_registered_list",
	"view_trainingpoint",
]

PERMISSIONS = {
	"specialist": Permission.objects.filter(codename__in=SPECIALIST_PERMISSIONS),
	"assistant": Permission.objects.filter(codename__in=ASSISTANT_PERMISSIONS),
	"student": Permission.objects.filter(codename__in=STUDENT_PERMISSIONS),
}

DEFAULT_PUBLIC_ID = {
	"avatar": "default-avatar",
	"bulletin": "bulletin-cover",
	"activity": "activity-image",
}

CONTENT_TYPE_BY_FILE_FORMAT = {
	"csv": "text/csv",
	"pdf": "application/pdf",
}

ACHIEVEMENTS = ["Xuất sắc", "Giỏi", "Khá", "Trung bình", "Yếu", "Kém"]
