from core.models import User
from django.db import models


class Confirm(models.Model):
    meeting = models.ForeignKey('core.Meeting', related_name='confirms')
    user = models.ForeignKey('core.User', related_name='confirms')

    date_create = models.DateTimeField(auto_now_add=True)
    last_modify = models.DateTimeField(auto_now=True)

    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)

    class Meta:
        unique_together = ('meeting', 'user')


class Chat(models.Model):
    title = models.CharField(max_length=32)
    users = models.ManyToManyField(User)


class Message(models.Model):
    chat = models.ForeignKey(Chat)
    author = models.ForeignKey(User)
    text = models.TextField()
    date_create = models.DateTimeField(auto_now=True)
