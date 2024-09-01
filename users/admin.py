from django.utils.safestring import mark_safe

from base.admin import BaseAdmin, my_admin_site
from users.models import Account, Administrator, Assistant, Specialist, Student


class AccountAdmin(BaseAdmin):
	list_display = ["email", "role", "is_staff", "is_superuser", "is_active", "last_login", "date_joined"]
	list_filter = ["role", "is_staff", "is_superuser", "is_active", "last_login", "date_joined"]
	search_fields = ["email"]
	readonly_fields = ["account_avatar"]

	def account_avatar(self, instance):
		if instance:
			return mark_safe(f"<img width='512' src='{instance.image.url}' />")


class UserAdmin(BaseAdmin):
	list_display = ["code", "last_name", "middle_name", "first_name", "gender", "account", "faculty"]
	list_filter = ["gender"]
	search_fields = ["code", "last_name", "middle_name", "first_name", "faculty__name"]


class AdministratorAdmin(UserAdmin):
	pass


class SpecialistAdmin(UserAdmin):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.list_display = UserAdmin.list_display + ["job_title", "academic_degree"]
		self.search_fields = UserAdmin.search_fields + ["job_title", "academic_degree"]


class AssistantAdmin(UserAdmin):
	pass


class StudentAdmin(UserAdmin):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.list_display = UserAdmin.list_display + ["major", "sclass", "academic_year", "educational_system"]
		self.search_fields = UserAdmin.search_fields + ["major__name", "sclass__name", "academic_year__name", "educational_system__name"]


my_admin_site.register(Account, AccountAdmin)
my_admin_site.register(Administrator, AdministratorAdmin)
my_admin_site.register(Specialist, SpecialistAdmin)
my_admin_site.register(Assistant, AssistantAdmin)
my_admin_site.register(Student, StudentAdmin)
