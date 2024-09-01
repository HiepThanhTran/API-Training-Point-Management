from rest_framework import serializers


class BaseSerializer(serializers.ModelSerializer):
	def __init__(self, *args, **kwargs):
		fields = kwargs.pop("fields", None)
		excludes = kwargs.pop("excludes", None)

		super().__init__(*args, **kwargs)

		if fields:
			allowed = set(fields)
			existing = set(self.fields)
			for field_name in existing - allowed:
				self.fields.pop(field_name)

		if excludes:
			for field_name in excludes:
				self.fields.pop(field_name)
