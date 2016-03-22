# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-18 11:34
from __future__ import unicode_literals

import citifleet.users.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20160316_1129'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', citifleet.users.models.UserManager()),
                ('with_notifications', citifleet.users.models.AllowNotificationManager()),
            ],
        ),
    ]