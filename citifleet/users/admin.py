# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from citifleet.marketplace.models import JobOffer, Car, GeneralGood
from .models import User, Photo


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'

    def save(self, commit=True):
        self.instance = super(MyUserChangeForm, self).save(commit=False)
        self.instance.user_type = User.USER_TYPES.user
        if self.cleaned_data['is_staff'] or self.cleaned_data['is_superuser']:
            self.instance.user_type = User.USER_TYPES.staff

        if commit:
            self.instance.save()
            self.save_m2m()
        return self.instance


class MyUserCreationForm(UserCreationForm):

    error_message = UserCreationForm.error_messages.update({
        'duplicate_username': 'This username has already been taken.'
    })

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'phone', 'email')

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


class GeneralGoodInline(admin.TabularInline):
    model = GeneralGood

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CarInline(admin.TabularInline):
    model = Car

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class JobOfferInline(admin.TabularInline):
    model = JobOffer
    fk_name = 'owner'
    exclude = ['driver_requests', 'driver_rating', 'owner_rating', 'driver', 'personal']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class UserAdmin(AuthUserAdmin):
    readonly_fields = ['drives']
    list_display = ['email', 'phone', 'drives', 'hack_license', 'date_joined', 'is_staff']
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    inlines = [CarInline, GeneralGoodInline, JobOfferInline]
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('full_name', 'email', 'phone', 'hack_license', 'bio')}),
        (_('Drives'), {'fields': ('car_make', 'car_model', 'car_color', 'car_type', 'car_year')}),
        (_('Created Posts'), {'fields': ('drives',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'password1', 'password2'),
        }),
    )

    change_list_template = 'users/change_list.html'


admin.site.register(User, UserAdmin)
admin.site.register(Photo)
