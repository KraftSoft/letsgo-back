from django.db import models
from core.mixins import LocationMixin
from location.models import Subway


class User(models.Model):
    name = models.CharField(max_length=64)
    avatar = models.ImageField()
    about = models.CharField(max_length=256)
    date_join = models.DateTimeField(auto_now=True)


class Meeting(LocationMixin, models.Model):
    title = models.CharField(max_length=32)
    description = models.TextField()
    users = models.ManyToManyField(User)
    subway = models.ForeignKey(Subway, null=True, blank=False)
