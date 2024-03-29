# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-12 12:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0013_joboffer_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='joboffer',
            name='personal',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Personal'), (2, 'Company')], default=1, verbose_name='Personal/Company'),
        ),
        migrations.AddField(
            model_name='joboffer',
            name='tolls',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Tolls'),
        ),
    ]
