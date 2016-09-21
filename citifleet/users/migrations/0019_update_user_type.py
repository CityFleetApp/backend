# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-09-21 17:25
from __future__ import unicode_literals

from django.db import migrations, models


def update_user_type(apps, schema_editor):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    User.objects.filter(models.Q(is_staff=True) | models.Q(is_superuser=True)).update(user_type=User.USER_TYPES.staff)


def reverse_method(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_user_user_type'),
    ]

    operations = [
        migrations.RunPython(update_user_type, reverse_method),
    ]