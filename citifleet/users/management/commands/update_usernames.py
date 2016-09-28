# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from citifleet.common.utils import generate_username

User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        users = User.objects.filter(username__icontains='@')
        for user in users:
            user.username = generate_username(user.full_name)
            user.save()
