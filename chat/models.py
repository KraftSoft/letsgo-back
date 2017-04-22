from core.models import User, Meeting
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
    owner = models.ForeignKey(User, related_name='my_own_chats')
    users = models.ManyToManyField(User, related_name='chats_with_me')
    meeting = models.ForeignKey(Meeting, related_name='chats')
    channel_slug = models.CharField(max_length=128, unique=True, db_index=True)


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages')
    author = models.ForeignKey(User, related_name='messages')
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    date_create = models.DateTimeField(auto_now=True)
