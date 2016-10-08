# -*- coding: utf-8 -*-

from django.dispatch import Signal

user_location_changed = Signal(providing_args=['user', ])
