# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-09-07 17:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_auto_20160905_2040'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='datetime_location_changed',
            field=models.DateTimeField(blank=True, null=True, verbose_name='time location changed'),
        ),
    ]