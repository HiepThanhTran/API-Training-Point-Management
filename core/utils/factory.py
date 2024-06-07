import cloudinary
from cloudinary import CloudinaryResource, api, uploader
from django.contrib.auth.models import Group
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from core.utils import validations
from core.utils.configs import DEFAULT_PUBLIC_ID, PERMISSIONS
from schools.models import Class, Faculty, Semester
from users.models import User


def set_permissions_for_account(account):
	group_name = validations.check_account_role(account)[1]

	if not group_name:
		raise ValidationError({"detail": "Tài khoản chưa được gán vai trò"})

	if group_name.__eq__("administrator"):
		specialist_group = Group.objects.get_or_create(name="specialist")[0]
		assistant_group = Group.objects.get_or_create(name="assistant")[0]
		student_group = Group.objects.get_or_create(name="student")[0]
		groups = [specialist_group, assistant_group, student_group]
		account.groups.set(groups)
		return account

	group = Group.objects.get_or_create(name=group_name)[0]
	group.permissions.set(PERMISSIONS[group_name])
	groups = [group]

	if group_name.__eq__("specialist"):
		assistant_group = Group.objects.get_or_create(name="assistant")[0]
		groups.append(assistant_group)

	account.groups.set(groups)
	return account


def set_role_for_account(user, account):
	role = validations.check_user_instance(user)[1]

	if not role:
		raise ValidationError({"detail": "Người dùng không hợp lệ"})

	account.role = role
	account.save()

	return user, account


def find_sfc_by_id(semester_code=None, faculty_id=None, class_id=None):
	semester = get_object_or_404(queryset=Semester, code=semester_code)

	if not faculty_id and not class_id:
		raise ValidationError({"detail": "Vui lòng cung cấp mã khoa hoặc mã lớp hoặc cả 2"})

	faculty, sclass = None, None

	if faculty_id and class_id:
		faculty = get_object_or_404(queryset=Faculty, pk=faculty_id)
		sclass = get_object_or_404(queryset=Class, pk=class_id, major__faculty=faculty)

	if faculty_id and not class_id:
		faculty = get_object_or_404(queryset=Faculty, pk=faculty_id)

	if not faculty_id and class_id:
		sclass = get_object_or_404(queryset=Class, pk=class_id)

	return semester, faculty, sclass


def find_user_by_code(code=None):
	users = get_all_subclasses(User)
	for user in users:
		try:
			return user.objects.get(code=code)
		except user.DoesNotExist:
			continue

	raise ValidationError({"detail": "Không tìm thấy người dùng"})


def get_or_upload_image(file=None, public_id=None, ftype=None):
	if not file and not public_id and not ftype:
		return None

	if file:
		return uploader.upload_resource(file=file, public_id=public_id, unique_filename=False, overwrite=True)

	if not public_id and ftype:
		public_id = DEFAULT_PUBLIC_ID[ftype]

	try:
		response = api.resource(public_id)
	except (cloudinary.exceptions.NotFound, TypeError):
		return None

	return CloudinaryResource(**{key: response.get(key) for key in ["public_id", "format", "version", "type", "resource_type"]})


def get_all_subclasses(cls):
	all_subclasses = []

	for subclass in cls.__subclasses__():
		if not subclass._meta.abstract:
			all_subclasses.append(subclass)
		all_subclasses.extend(get_all_subclasses(subclass))

	return all_subclasses
