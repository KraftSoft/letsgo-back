from core.models import User
from django.db import models


class Chat(models.Model):
    title = models.CharField(max_length=32)
    users = models.ManyToManyField(User)


class Message(models.Model):
    chat = models.ForeignKey(Chat)
    author = models.ForeignKey(User)
    text = models.TextField()
    date_create = models.DateTimeField(auto_now=True)

