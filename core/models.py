from django.contrib.auth.models import AbstractUser
from django.db import models

from core.utils import build_absolute_url
from location.models import Subway
from django.contrib.gis.db import models as gis_models


class User(AbstractUser):
    about = models.CharField(max_length=256, blank=True)

    USERNAME_FIELD = 'first_name'
    REQUIRED_FIELDS = tuple()

    def get_avatar(self):

        obj = self.photos.filter(is_avatar=True).first()

        if not obj:
            obj = self.photos.filter().first()

        if not obj or not obj.photo:
            return ''

        return build_absolute_url(obj.photo)


class Meeting(models.Model):
    title = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, related_name='created_meetings')
    subway = models.ForeignKey(Subway, null=True, blank=True, related_name='meetings')
    coordinates = gis_models.PointField(null=True, blank=False)
    date_create = models.DateTimeField(auto_now=True)
    meeting_date = models.DateTimeField()
    last_modify = models.DateTimeField(auto_now_add=True)
    group_type = models.SmallIntegerField()


class UserPhotos(models.Model):
    owner = models.ForeignKey(User, related_name='photos')
    photo = models.URLField(null=True, blank=True)
    is_avatar = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_avatar']


class SocialData(models.Model):
    user = models.OneToOneField(User)
    social_slug = models.CharField(max_length=16)
    external_id = models.PositiveIntegerField()
    token = models.CharField(max_length=255, unique=True)

    class Meta:
        unique_together = ('social_slug', 'external_id')
