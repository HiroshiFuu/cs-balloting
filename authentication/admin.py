# -*- encoding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

# from .models import AdminUser
from .models import CompanyUser
from .forms import CustomUserCreationForm

import copy

# Register your models here.
# admin.site.unregister(Group)

# @admin.register(AdminUser)
# class AdminUserAdmin(UserAdmin):
#     ordering = ('username',)
#     list_display_links = ('username', 'email')


@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    add_form = CustomUserCreationForm
    list_display = ('company', 'username', 'email', 'weight', 'is_active')
    list_filter = ('company', 'weight', 'is_active')
    fieldsets = (
        (None, {'fields': ['company', 'username', 'email', 'weight']}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ['company', 'username', 'email', 'weight', 'is_active', 'password1', 'password2']}
        ),
    )
    search_fields = ('email', 'username')
    ordering = ('email',)
    list_display_links = ('username', 'email')

    # def get_fieldsets(self, request, obj=None):
    #     if not obj:
    #         return self.add_fieldsets
    #     return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def get_fieldsets(self, request, obj=None):
        if obj:
            fieldsets = copy.deepcopy(self.fieldsets)
        else:
            fieldsets = copy.deepcopy(self.add_fieldsets)
        if not request.user.is_superuser:
            fieldsets[0][1]['fields'].pop(0)
        return fieldsets

    def save_model(self, request, obj, form, change):
        if not change:
            obj.company = request.user
        print(obj, change)
        super().save_model(request, obj, form, change)
