# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-02-11 08:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_remove_meeting_members'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPhotos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='')),
                ('is_avatar', models.BooleanField(default=False)),
            ],
        ),
        migrations.RemoveField(
            model_name='user',
            name='avatar',
        ),
        migrations.AlterField(
            model_name='meeting',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_meetings', to='core.User'),
        ),
        migrations.AddField(
            model_name='userphotos',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='core.User'),
        ),
    ]