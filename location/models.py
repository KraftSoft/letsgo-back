from django.db import models
from core.mixins import LocationMixin


class Subway(LocationMixin, models.Model):
    name = models.CharField(max_length=64)
