# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-26 14:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_auto_20160331_1122'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Balance'),
        ),
    ]