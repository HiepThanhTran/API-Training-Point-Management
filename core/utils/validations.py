import re
from datetime import datetime

import unidecode
from rest_framework.exceptions import ValidationError

from users.models import Account, Administrator, Assistant, Specialist, Student


def check_user_instance(user):
	if not isinstance(user, (Administrator, Specialist, Assistant, Student)):
		raise ValidationError({"detail": "Người dùng không hợp lệ"})

	from users import serializers
	instance_mapping = {
		Administrator: (serializers.AdministratorSerializer, Account.Role.ADMINISTRATOR),
		Specialist: (serializers.SpecialistSerializer, Account.Role.SPECIALIST),
		Assistant: (serializers.AssistantSerializer, Account.Role.ASSISTANT),
		Student: (serializers.StudentSerializer, Account.Role.STUDENT),
	}
	return instance_mapping.get(type(user))


def check_account_role(account):
	if not isinstance(account, Account):
		raise ValidationError({"detail": "Tài khoản không hợp lệ"})

	from users import serializers
	role_mapping = {
		Account.Role.ADMINISTRATOR: (serializers.AdministratorSerializer, "administrator"),
		Account.Role.SPECIALIST: (serializers.SpecialistSerializer, "specialist"),
		Account.Role.ASSISTANT: (serializers.AssistantSerializer, "assistant"),
		Account.Role.STUDENT: (serializers.StudentSerializer, "student"),
	}
	return role_mapping.get(account.role)


def validate_email(code, first_name, email):
	first_name = re.escape(unidecode.unidecode(first_name).lower().replace(" ", ""))
	pattern = f"^{code}{first_name}@ou.edu.vn$"

	if not email or not bool(re.match(pattern, email.strip())):
		raise ValidationError({"detail": "Vui lòng nhập email trường cấp"})

	return email


def validate_date_format(date):
	try:
		datetime.strptime(date, "%Y-%m-%d")
	except ValueError:
		return False

	return date
