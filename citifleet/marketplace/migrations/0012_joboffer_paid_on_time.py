# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-25 10:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0011_auto_20160421_1053'),
    ]

    operations = [
        migrations.AddField(
            model_name='joboffer',
            name='paid_on_time',
            field=models.BooleanField(default=False, verbose_name='Paid on time'),
        ),
    ]
