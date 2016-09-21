# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-09-21 17:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_user_datetime_location_changed'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_type',
            field=models.SmallIntegerField(choices=[(0, 'Just a User'), (1, 'Any staff user (admin/superuser/staff)')], default=0, verbose_name='user type'),
        ),
    ]
