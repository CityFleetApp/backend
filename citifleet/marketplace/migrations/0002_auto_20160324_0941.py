# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-24 09:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='color',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Black'), (2, 'White'), (3, 'Red')], verbose_name='Color'),
        ),
    ]
