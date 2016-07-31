from django.db import models


class User(models.Model):
    name = models.CharField(max_length=64)
    avatar = models.ImageField()
    about = models.CharField(256)
    date_join = models.DateTimeField(auto_now=True)


class Meeting(models.Model):
    title = models.CharField(max_length=32)
    description = models.TextField()
    users = models.ManyToManyField(User)
    # TODO
    #location =
    #subway =