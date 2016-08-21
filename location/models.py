from django.db import models


class Subway(models.Model):
    name = models.CharField(max_length=64)
