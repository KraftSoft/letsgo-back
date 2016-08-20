from django.contrib.auth.models import AbstractUser
from django.db import models
from core.mixins import LocationMixin
from location.models import Subway


class User(AbstractUser):
    avatar = models.ImageField(null=True, blank=True)
    about = models.CharField(max_length=256, blank=True)


class Meeting(LocationMixin, models.Model):
    title = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, related_name='created_meetings', blank=True)
    members = models.ManyToManyField(User, related_name='favorite_meetings', blank=True)
    subway = models.ForeignKey(Subway, null=True, blank=True, related_name='meetings')

    date_create = models.DateTimeField(auto_now=True)
    last_modify = models.DateTimeField(auto_now_add=True)
