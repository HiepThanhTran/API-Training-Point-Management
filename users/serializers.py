from rest_framework import serializers

from base.serializers import BaseSerializer
from users.models import Account, Administrator, Assistant, Specialist, Student, User
from utils import factory, validations


class AccountSerializer(BaseSerializer):
	code = serializers.CharField(write_only=True, required=True, allow_blank=False, allow_null=False)
	user = serializers.SerializerMethodField(read_only=True)

	class Meta:
		model = Account
		fields = ["id", "role", "original_role", "code", "email", "password", "avatar", "date_joined", "last_login", "user"]
		extra_kwargs = {
			"password": {"write_only": True},
			"original_role": {"read_only": True},
			"date_joined": {"read_only": True},
			"last_login": {"read_only": True},
		}

	def to_representation(self, account):
		data = super().to_representation(account)
		avatar = data.get("avatar")

		if "avatar" in self.fields and avatar:
			data["avatar"] = account.avatar.url

		return data

	def create(self, validated_data):
		user = factory.find_user_by_code(code=validated_data.pop("code"))
		validations.validate_email(code=user.code, first_name=user.first_name, email=validated_data["email"])

		avatar = validated_data.get("avatar", None)
		validated_data["avatar"] = factory.get_or_upload_image(file=avatar, public_id=f"user-{user.code}" if avatar else avatar, ftype="avatar")

		account = Account.objects.create_account(email=validated_data.pop("email"), password=validated_data.pop("password"), **validated_data)
		user.account = account
		user.save()
		factory.set_role_for_account(user=user, account=account)

		return account

	def get_user(self, account):
		serializer_class, instance_name = validations.check_account_role(account)
		user = getattr(account, instance_name, None)
		return serializer_class(user).data


class AccountUpdateSerializer(serializers.Serializer):
	old_password = serializers.CharField(write_only=True, required=False)
	new_password = serializers.CharField(write_only=True, required=False)
	avatar = serializers.ImageField(required=False)
	first_name = serializers.CharField(required=False, max_length=50)
	middle_name = serializers.CharField(required=False, max_length=50)
	last_name = serializers.CharField(required=False, max_length=50)
	date_of_birth = serializers.DateField(required=False)
	address = serializers.CharField(required=False, max_length=255)
	phone_number = serializers.CharField(required=False, max_length=15)
	gender = serializers.CharField(required=False, max_length=1)

	def update(self, account, validated_data):
		instance_name = validations.check_account_role(account)[1]
		user = getattr(account, instance_name, None)

		if "old_password" in validated_data and "new_password" in validated_data:
			account.set_password(validated_data.pop("new_password"))
		if "avatar" in validated_data:
			account.avatar = factory.get_or_upload_image(file=validated_data.pop("avatar"), public_id=f"user-{user.code}")
		account.save()

		for attr, value in validated_data.items():
			if attr != 'code':
				setattr(user, attr, value)
		user.save()

		return account


class UserSerializer(BaseSerializer):
	class Meta:
		model = User
		fields = [
			"id", "code", "full_name", "first_name", "middle_name", "last_name",
			"gender", "date_of_birth", "address", "phone_number", "faculty"
		]

	def to_representation(self, user):
		data = super().to_representation(user)

		if "faculty" in self.fields and user.faculty:
			data["faculty"] = f"{user.faculty}"

		return data


class AdministratorSerializer(UserSerializer):
	class Meta:
		model = Administrator
		fields = UserSerializer.Meta.fields


class SpecialistSerializer(UserSerializer):
	class Meta:
		model = Specialist
		fields = UserSerializer.Meta.fields + ["job_title", "academic_degree"]


class AssistantSerializer(UserSerializer):
	class Meta:
		model = Assistant
		fields = UserSerializer.Meta.fields


class StudentSerializer(UserSerializer):
	class Meta:
		model = Student
		fields = UserSerializer.Meta.fields + ["major", "sclass", "academic_year", "educational_system"]

	def to_representation(self, student):
		data = super().to_representation(student)

		if "major" in self.fields and student.major:
			data["major"] = f"{student.major}"
		if "sclass" in self.fields and student.sclass:
			data["sclass"] = f"{student.sclass}"
		if "academic_year" in self.fields and student.academic_year:
			data["academic_year"] = f"{student.academic_year}"
		if "educational_system" in self.fields and student.educational_system:
			data["educational_system"] = f"{student.educational_system}"

		return data
