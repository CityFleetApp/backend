# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-25 14:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0004_auto_20160325_0917'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoodPhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.ImageField(upload_to='goods/', verbose_name='Photo')),
                ('goods', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='marketplace.GeneralGood', verbose_name='Good')),
            ],
            options={
                'verbose_name': 'General Goods Photo',
                'verbose_name_plural': 'General Goods Photos',
            },
        ),
    ]
