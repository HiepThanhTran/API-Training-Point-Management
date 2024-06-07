from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from activities.forms import ActivityAdminForm
from activities.models import Activity, ActivityRegistration, MissingActivityReport, Bulletin
from core.base.admin import my_admin_site


class ActivityAdmin(admin.ModelAdmin):
    form = ActivityAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organizer_type":
            kwargs["queryset"] = ContentType.objects.filter(app_label="users", model__in=["administrator", "assistant", "specialist"])

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


my_admin_site.register(Activity, ActivityAdmin)
my_admin_site.register(Bulletin)
my_admin_site.register(ActivityRegistration)
my_admin_site.register(MissingActivityReport)
