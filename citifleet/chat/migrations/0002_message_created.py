# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-06 14:15
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 4, 6, 14, 15, 24, 88050, tzinfo=utc), verbose_name='Created'),
            preserve_default=False,
        ),
    ]
