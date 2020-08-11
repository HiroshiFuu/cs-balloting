# -*- encoding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from .models import AuthUser

from .forms import CustomCompanyCreationForm
from .forms import CustomUserCreationForm

from .constants import USER_TYPE_USER

import copy


@admin.register(AuthUser)
class AuthUserAdmin(UserAdmin):
    list_display = ['company_user', 'username', 'email',
                    'weight', 'is_company', 'is_active']
    ordering = ('username',)
    list_display_links = ('username', 'email')
    fieldsets = (
        (None, {'fields': ['username', 'email', 'weight', 'company_user']}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ['groups', 'is_active']}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ['username', 'email', 'weight', 'user_type', 'company_user', 'password1', 'password2', 'is_staff']}
         ),
    )

    def is_company(self, obj):
        return not obj.is_superuser and obj.is_staff
    is_company.short_description = _('Is Company User')
    is_company.boolean = True

    def get_list_display(self, request):
        list_display = copy.deepcopy(self.list_display)
        if not request.user.is_superuser:
            list_display.pop(0) 
        return list_display

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(Q(username=request.user.username) | Q(company_user=request.user))

    def get_fieldsets(self, request, obj=None):
        if obj:
            fieldsets = copy.deepcopy(self.fieldsets)
            if not request.user.is_superuser:
                fieldsets[0][1]['fields'].pop(-1)
                fieldsets[2][1]['fields'].pop(0)
        else:
            fieldsets = copy.deepcopy(self.add_fieldsets)
            if request.user.is_superuser:
                self.add_form = CustomCompanyCreationForm
            elif request.user.is_staff:
                self.add_form = CustomUserCreationForm
                # fieldsets[0][1]['fields'].pop(-1)
                fieldsets[0][1]['fields'] = ['username',
                                             'email', 'weight', 'password1', 'password2']
        # print('get_fieldsets', self.add_form)
        return fieldsets

    def save_model(self, request, obj, form, change):
        # print('save_model', obj, change)
        if not change and not request.user.is_superuser and request.user.is_staff:
            obj.company_user = request.user
            obj.user_type = USER_TYPE_USER
        super().save_model(request, obj, form, change)

    # def get_changeform_initial_data(self, request):
    #     return {'company_user': request.user}


# @admin.register(CompanyUser)
# class CompanyUserAdmin(admin.ModelAdmin):
#     add_form = CustomUserCreationForm
#     list_display = ('company', 'username', 'email', 'weight', 'is_active')
#     list_filter = ('company', 'weight', 'is_active')
#     fieldsets = (
#         (None, {'fields': ['company', 'username', 'email', 'weight']}),
#         ('Personal info', {'fields': ('first_name', 'last_name')}),
#         ('Permissions', {'fields': ('is_active',)}),
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ['company', 'username', 'email', 'weight', 'is_active', 'password1', 'password2']}
#          ),
#     )
#     search_fields = ('email', 'username')
#     ordering = ('email',)
#     list_display_links = ('username', 'email')

#     # def get_fieldsets(self, request, obj=None):
#     #     if not obj:
#     #         return self.add_fieldsets
#     #     return super().get_fieldsets(request, obj)

#     def get_form(self, request, obj=None, **kwargs):
#         """
#         Use special form during user creation
#         """
#         defaults = {}
#         if obj is None:
#             defaults['form'] = self.add_form
#         defaults.update(kwargs)
#         return super().get_form(request, obj, **defaults)

#     def get_fieldsets(self, request, obj=None):
#         if obj:
#             fieldsets = copy.deepcopy(self.fieldsets)
#         else:
#             fieldsets = copy.deepcopy(self.add_fieldsets)
#         if not request.user.is_superuser:
#             fieldsets[0][1]['fields'].pop(0)
#         return fieldsets

#     def save_model(self, request, obj, form, change):
#         if not change:
#             obj.company = request.user
#         print(obj, change)
#         super().save_model(request, obj, form, change)
