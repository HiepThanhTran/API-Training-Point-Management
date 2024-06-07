from django.db import models


class BaseModel(models.Model):
    class Meta:
        abstract = True

    is_active = models.BooleanField(default=True)
    updated_date = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)
