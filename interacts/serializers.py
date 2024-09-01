from rest_framework import serializers

from interacts.models import Comment
from users import serializers as users_serializer
from utils import validations


class CommentSerializer(serializers.ModelSerializer):
	account = serializers.SerializerMethodField()

	class Meta:
		model = Comment
		fields = ["id", "created_date", "updated_date", "content", "account"]

	def get_account(self, comment):
		instance_name = validations.check_account_role(comment.account)[1]
		user = getattr(comment.account, instance_name, None)

		serializer = users_serializer.AccountSerializer(comment.account, excludes=["user"])
		data = serializer.data
		data['full_name'] = user.full_name

		return data
