# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-02 13:26
from __future__ import unicode_literals

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InsuranceBroker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('years_of_experience', models.IntegerField(verbose_name='years of experience')),
                ('rating', models.PositiveSmallIntegerField(verbose_name='rating')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, verbose_name='phone')),
                ('address', models.CharField(max_length=250, verbose_name='address')),
            ],
            options={
                'verbose_name': 'Insurance Broker',
                'verbose_name_plural': 'Insurance Brokers',
            },
        ),
    ]
