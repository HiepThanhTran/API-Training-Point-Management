from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

from core.base.models import BaseModel


class Interaction(BaseModel):
    class Meta:
        abstract = True

    account = models.ForeignKey(to="users.Account", on_delete=models.CASCADE, related_name="%(class)ss")
    activity = models.ForeignKey(to="activities.Activity", on_delete=models.CASCADE, related_name="%(class)ss")


class Comment(Interaction):
    content = CKEditor5Field("Text", config_name="extends")


class Like(Interaction):
    class Meta:
        unique_together = ("account", "activity")
