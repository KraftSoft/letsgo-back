# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-04-09 19:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20170409_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='meeting_date',
            field=models.DateField(),
        ),
    ]
