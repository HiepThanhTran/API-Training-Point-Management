from base.admin import BaseAdmin, my_admin_site
from interacts.models import Comment, Like


class CommentAdmin(BaseAdmin):
	list_display = ["account", "activity", "created_date", "updated_date"]
	list_filter = ["created_date", "updated_date"]
	search_fields = ("content", "account__email", "activity__name",)


class LikeAdmin(BaseAdmin):
	list_display = ["account", "activity", "created_date", "updated_date"]
	list_filter = ["created_date", "updated_date"]
	search_fields = ("account__email", "activity__name",)


my_admin_site.register(Comment, CommentAdmin)
my_admin_site.register(Like, LikeAdmin)
