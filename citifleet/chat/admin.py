# -*- coding: utf-8 -*-
from django.contrib import admin

from citifleet.chat.models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    pass
