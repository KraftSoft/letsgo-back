# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-04-02 13:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20170402_1633'),
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='users',
            field=models.ManyToManyField(to='core.User'),
        ),
        migrations.AddField(
            model_name='confirm',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='confirm',
            name='meeting',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='confirms', to='core.Meeting'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='confirm',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='confirms', to='core.User'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='message',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.User'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='message',
            name='chat',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='chat.Chat'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='confirm',
            unique_together=set([('meeting', 'user')]),
        ),
    ]