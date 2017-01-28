from django.contrib.auth.models import AbstractUser
from django.db import models
from location.models import Subway
from django.contrib.gis.db import models as gis_models


class User(AbstractUser):
    avatar = models.ImageField(null=True, blank=True)
    about = models.CharField(max_length=256, blank=True)


class Meeting(models.Model):
    title = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, related_name='created_meetings', blank=True)
    subway = models.ForeignKey(Subway, null=True, blank=True, related_name='meetings')
    coordinates = gis_models.PointField(null=True, blank=False)
    date_create = models.DateTimeField(auto_now=True)
    last_modify = models.DateTimeField(auto_now_add=True)
