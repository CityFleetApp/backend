# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-16 11:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20160315_0906'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='chat_privacy',
            field=models.BooleanField(default=True, verbose_name='chat privacy'),
        ),
        migrations.AddField(
            model_name='user',
            name='notifications_enabled',
            field=models.BooleanField(default=True, verbose_name='notifications enabled'),
        ),
        migrations.AddField(
            model_name='user',
            name='visible',
            field=models.BooleanField(default=True, verbose_name='visible'),
        ),
    ]
