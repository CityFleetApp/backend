# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-28 07:46
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('marketplace', '0005_goodphoto'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobOffer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pickup_datetime', models.DateTimeField(verbose_name='Pickup datetime')),
                ('pickup_address', models.CharField(max_length=255, verbose_name='Pickup address')),
                ('destination', models.CharField(max_length=255, verbose_name='Destination')),
                ('fare', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Fare')),
                ('gratuity', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Gratuity')),
                ('vehicle_type', models.PositiveSmallIntegerField(choices=[(1, 'Regular'), (2, 'Black'), (3, 'SUV'), (4, 'LUX')], verbose_name='Vehicle Type')),
                ('suite', models.BooleanField(default=False, verbose_name='Suite/Tie')),
                ('job_type', models.PositiveSmallIntegerField(choices=[(1, 'Drop off'), (2, 'Wait & Return'), (3, 'Hourly')], verbose_name='Job Type')),
                ('instructions', models.CharField(max_length=255, verbose_name='Instructions')),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='offers', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_postings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
