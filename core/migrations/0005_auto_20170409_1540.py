# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-04-09 12:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_meeting_meeting_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='birth_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.SmallIntegerField(null=True),
        ),
    ]
