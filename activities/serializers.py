from rest_framework import serializers

from activities.models import (
	Activity,
	ActivityRegistration,
	Bulletin,
	MissingActivityReport,
)
from base.serializers import BaseSerializer
from interacts.models import Like
from utils import factory, validations


class BulletinSerializer(BaseSerializer):
	created_by = serializers.SerializerMethodField()

	class Meta:
		model = Bulletin
		fields = ["id", "name", "image", "created_date", "updated_date", "description", "created_by"]

	def to_representation(self, bulletin):
		data = super().to_representation(bulletin)
		image = data.get("image")

		if "image" in self.fields and image:
			data["image"] = bulletin.image.url

		return data

	def create(self, validated_data):
		request = self.context.get("request")
		image = validated_data.pop("image", None)

		instance_name = validations.check_account_role(request.user)[1]
		validated_data["poster"] = getattr(request.user, instance_name, None)
		bulletin = Bulletin.objects.create(**validated_data)

		bulletin.image = factory.get_or_upload_image(file=image, public_id=f"bulletin-{bulletin.id}" if image else None, ftype="bulletin")
		bulletin.save()

		return bulletin

	def update(self, bulletin, validated_data):
		image = validated_data.get("image", None)
		if image:
			validated_data["image"] = factory.get_or_upload_image(file=image, public_id=f"bulletin-{bulletin.id}")

		for key, value in validated_data.items():
			setattr(bulletin, key, value)
		bulletin.save()

		return bulletin

	def get_created_by(self, bulletin):
		serializer_class, role = validations.check_user_instance(bulletin.poster)
		serializer = serializer_class(bulletin.poster, excludes=["code"])

		data = serializer.data
		data["role"] = role
		data["avatar"] = bulletin.poster.account.avatar.url if bulletin.poster.account else None

		return data


class ActivitySerializer(BaseSerializer):
	total_likes = serializers.SerializerMethodField()
	created_by = serializers.SerializerMethodField()

	class Meta:
		model = Activity
		fields = [
			"id", "name", "participant", "start_date", "end_date",
			"location", "point", "updated_date", "created_date",
			"bulletin", "faculty", "semester", "criterion",
			"image", "organizational_form", "total_likes", "description", "created_by"
		]

	def to_representation(self, activity):
		data = super().to_representation(activity)
		image = data.get("image", None)

		if "image" in self.fields and image:
			data["image"] = activity.image.url
		if "bulletin" in self.fields and activity.bulletin:
			data["bulletin"] = {"id": activity.bulletin.id, "name": f"{activity.bulletin.name}"}
		if "faculty" in self.fields and activity.faculty:
			data["faculty"] = {"id": activity.faculty.id, "name": f"{activity.faculty.name}"}
		if "criterion" in self.fields and activity.criterion:
			data["criterion"] = {"id": activity.criterion.id, "name": f"{activity.criterion.name}"}
		if "semester" in self.fields and activity.semester:
			data["semester"] = {"id": activity.semester.id, "name": f"{activity.semester.original_name} - {activity.semester.academic_year}"}

		return data

	def create(self, validated_data):
		request = self.context.get("request")
		image = validated_data.pop("image", None)

		instance_name = validations.check_account_role(request.user)[1]
		validated_data["organizer"] = getattr(request.user, instance_name, None)
		activity = Activity.objects.create(**validated_data)

		activity.image = factory.get_or_upload_image(file=image, public_id=f"activity-{activity.id}" if image else image, ftype="activity")
		activity.save()

		return activity

	def update(self, activity, validated_data):
		image = validated_data.get("image", None)
		if image:
			validated_data["image"] = factory.get_or_upload_image(file=image, public_id=f"activity-{activity.id}", ftype="activity")

		for key, value in validated_data.items():
			setattr(activity, key, value)
		activity.save()

		return activity

	def get_created_by(self, activity):
		serializer_class, role = validations.check_user_instance(activity.organizer)
		serializer = serializer_class(activity.organizer, excludes=["code"])

		data = serializer.data
		data["role"] = role
		data["avatar"] = activity.organizer.account.avatar.url if activity.organizer.account else None

		return data

	def get_total_likes(self, activity):
		return activity.likes.filter(is_active=True).count()


class AuthenticatedActivitySerializer(ActivitySerializer):
	liked = serializers.SerializerMethodField()

	class Meta:
		model = ActivitySerializer.Meta.model
		fields = ActivitySerializer.Meta.fields + ["liked"]

	def get_liked(self, activity):
		request = self.context.get("request")

		try:
			like = Like.objects.get(account=request.user, activity=activity)
		except Like.DoesNotExist:
			return False

		return like.is_active


class StudentAuthenticatedActivitySerializer(AuthenticatedActivitySerializer):
	registered = serializers.SerializerMethodField()
	reported = serializers.SerializerMethodField()

	class Meta:
		model = AuthenticatedActivitySerializer.Meta.model
		fields = AuthenticatedActivitySerializer.Meta.fields + ["registered", "reported"]

	def get_registered(self, activity):
		request = self.context.get("request")

		instance_name = validations.check_account_role(request.user)[1]
		user = getattr(request.user, instance_name, None)

		return activity.participants.filter(pk=user.id).exists()

	def get_reported(self, activity):
		request = self.context.get("request")

		try:
			report = MissingActivityReport.objects.get(student=request.user.student, activity=activity)
		except MissingActivityReport.DoesNotExist:
			return {"reported": False, "is_resolved": None}

		return {"reported": True, "is_resolved": report.is_resolved}


class ActivityRegistrationSerializer(BaseSerializer):
	from users import serializers as user_serializers
	student = user_serializers.StudentSerializer()
	activity = ActivitySerializer()

	class Meta:
		model = ActivityRegistration
		fields = ["id", "is_attendance", "is_point_added", "created_date", "updated_date", "student", "activity", ]


class MissingActivityReportSerializer(BaseSerializer):
	from users import serializers as user_serializers
	student = user_serializers.StudentSerializer()
	activity = ActivitySerializer()

	class Meta:
		model = MissingActivityReport
		fields = ["id", "is_resolved", "evidence", "created_date", "updated_date", "content", "student", "activity", ]

	def to_representation(self, instance):
		data = super().to_representation(instance)

		evidence = data.get("evidence", None)
		if "evidence" in self.fields and evidence:
			data["evidence"] = instance.evidence.url

		return data
