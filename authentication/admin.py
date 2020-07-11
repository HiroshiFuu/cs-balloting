# -*- encoding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User

# Register your models here.
admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'weight')
    list_filter = ('username', 'email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'weight', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    list_display_links = ('username', 'email', )