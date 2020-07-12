# -*- encoding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.models import Group

from .models import User
from .forms import CustomUserCreationForm

# Register your models here.
admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    add_form = CustomUserCreationForm
    list_display = ('username', 'email', 'is_staff', 'is_active', 'weight')
    list_filter = ('weight', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'weight', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'weight', 'is_active')}
        ),
    )
    search_fields = ('email', 'username')
    ordering = ('email',)
    list_display_links = ('username', 'email')

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)