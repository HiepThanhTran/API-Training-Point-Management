from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe

from activities.forms import ActivityAdminForm
from activities.models import (
	Activity,
	ActivityRegistration,
	Bulletin,
	MissingActivityReport,
)
from base.admin import BaseAdmin, my_admin_site


class BulletinAdmin(BaseAdmin):
	list_display = ["name", "created_date", "updated_date"]
	list_filter = ["created_date", "updated_date"]
	search_fields = ("name", "description")
	readonly_fields = ["bulletin_image"]

	def bulletin_image(self, instance):
		if instance:
			return mark_safe(f"<img width='512' src='{instance.image.url}' />")


class ActivityAdmin(BaseAdmin):
	form = ActivityAdminForm

	list_display = ["name", "criterion", "point", "faculty", "semester", "created_date", "updated_date"]
	list_filter = ["created_date", "updated_date"]
	search_fields = ("name", "criterion__name", "bulletin__name", "faculty__name", "description", "location")
	readonly_fields = ["activity_image"]

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "organizer_type":
			kwargs["queryset"] = ContentType.objects.filter(app_label="users", model__in=["administrator", "assistant", "specialist"])

		return super().formfield_for_foreignkey(db_field, request, **kwargs)

	def activity_image(self, instance):
		if instance:
			return mark_safe(f"<img width='512' src='{instance.image.url}' />")


class ActivityRegistrationAdmin(BaseAdmin):
	list_display = ["student", "activity", "is_attendance", "is_point_added"]
	list_filter = ["is_attendance", "is_point_added"]
	search_fields = ("student", "activity")


class MissingActivityReportAdmin(BaseAdmin):
	list_display = ["student", "activity", "is_resolved"]
	list_filter = ["is_resolved"]
	search_fields = ("student", "activity")


my_admin_site.register(Bulletin, BulletinAdmin)
my_admin_site.register(Activity, ActivityAdmin)
my_admin_site.register(ActivityRegistration, ActivityRegistrationAdmin)
my_admin_site.register(MissingActivityReport, MissingActivityReportAdmin)
