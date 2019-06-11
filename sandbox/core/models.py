from django.db import models


class DataModel(models.Model):
    some_value = models.IntegerField()
