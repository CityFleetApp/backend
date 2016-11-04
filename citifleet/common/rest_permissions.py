# -*- coding: utf-8 -*-

from __future__ import unicode_literals


from rest_framework.permissions import BasePermission


class UserWithoutSiteAccountOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated() and not request.user.has_usable_password()


class AnonymousOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_anonymous()
