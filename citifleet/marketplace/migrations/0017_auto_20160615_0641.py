# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-06-15 06:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0016_auto_20160513_0735'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='created',
            field=models.DateTimeField(auto_now=True, verbose_name='Created'),
        ),
        migrations.AlterField(
            model_name='generalgood',
            name='created',
            field=models.DateTimeField(auto_now=True, verbose_name='Created'),
        ),
    ]