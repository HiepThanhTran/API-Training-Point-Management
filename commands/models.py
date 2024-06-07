from django.db import models


class CollectData(models.Model):
    app_label = models.CharField(max_length=255)
    model_name = models.CharField(max_length=255)
    applied = models.BooleanField(default=False)
