# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-09-30 10:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customapnsdevice',
            name='user',
        ),
        migrations.DeleteModel(
            name='CustomAPNSDevice',
        ),
    ]
