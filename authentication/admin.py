# -*- encoding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from .models import Company
from .models import AuthUser
from .models import AuthGroup
from .models import Lot

from .forms import CustomCompanyCreationForm
from .forms import CustomUserCreationForm

from .constants import USER_TYPE_USER
from .constants import USER_TYPE_COMPANY

import copy


admin.site.unregister(Group)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'address',
        'postal_code',
        'valid_date',
    ]


@admin.register(AuthGroup)
class AuthGroupAdmin(GroupAdmin):
    list_display = ['name', 'list_permissions']

    def list_permissions(self, obj):
        return ' | '.join([o.name for o in obj.permissions.all()])

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        form_field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name in [*self.filter_horizontal]:
            form_field.widget.attrs = {'size': '10'}
        return form_field


class LotDetailsInline(admin.TabularInline):
    model = Lot
    fk_name = 'user'
    extra = 0
    per_page = 3
    exclude = ('created_by', 'modified_by')


@admin.register(AuthUser)
class AuthUserAdmin(UserAdmin):
    list_display = ['company', 'username', 'weight', 'phone_no',
                    '_has_lot', 'lots_details', 'is_company_user', 'is_active']
    ordering = ('company', 'user_type', 'username')
    list_display_links = ('company', 'username')
    fieldsets = (
        (None, {'fields': ['username', 'weight', 'user_type', 'company']}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_no')}),
        ('Permissions', {'fields': [
         'groups', 'is_staff', 'is_active', 'password']}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ['username', 'phone_no', 'weight', 'user_type', 'company', 'password1', 'password2', 'is_staff']}
         ),
    )
    inlines = [
        LotDetailsInline
    ]

    def is_company_user(self, obj):
        return obj.user_type == USER_TYPE_COMPANY
    is_company_user.short_description = _('Is Company User')
    is_company_user.boolean = True

    def get_list_display(self, request):
        list_display = copy.deepcopy(self.list_display)
        if not request.user.is_superuser:
            list_display.remove('company')
        return list_display

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(company=request.user.company)

    def get_fieldsets(self, request, obj=None):
        if obj:
            if request.user.is_superuser:
                fieldsets = copy.deepcopy(self.fieldsets)
            else:
                fieldsets = (
                    (None, {'fields': ['username',
                                       'weight', 'user_type', 'company']}),
                    ('Personal info', {
                     'fields': ('first_name', 'last_name', 'phone_no')}),
                    ('Permissions', {'fields': [
                     'groups', 'is_staff', 'is_active', 'password']}),
                )
        else:
            if request.user.is_superuser:
                fieldsets = copy.deepcopy(self.add_fieldsets)
                # self.add_form = CustomCompanyCreationForm
            else:
                # self.add_form = CustomUserCreationForm
                fieldsets = (
                    (None, {
                        'classes': ('wide',),
                        'fields': ['username', 'phone_no', 'weight', 'user_type', 'company', 'password1', 'password2', 'is_staff']}
                     ),
                )
        # print('get_fieldsets', fieldsets)
        return fieldsets

    def save_model(self, request, obj, form, change):
        # print('save_model', obj, change)
        if not change and request.user.user_type == USER_TYPE_COMPANY:
            obj.company = request.user.company
            obj.user_type = USER_TYPE_USER
            obj.email = obj.username
        super().save_model(request, obj, form, change)

    # def get_changeform_initial_data(self, request):
    #     return {'company_user': request.user}


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = ['user', 'block_no', 'unit_no']
    ordering = ('user',)
    list_display_links = ('user',)
    exclude = ('created_by', 'modified_by')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(user__company=request.user.company)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'user':
            if not request.user.is_superuser:
                kwargs['queryset'] = get_user_model().objects.filter(company=request.user.company, is_staff=False)
        return super(LotAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


# @admin.register(CompanyUser)
# class CompanyUserAdmin(admin.ModelAdmin):
#     add_form = CustomUserCreationForm
#     list_display = ('company', 'username', 'weight', 'is_active')
#     list_filter = ('company', 'weight', 'is_active')
#     fieldsets = (
#         (None, {'fields': ['company', 'username', 'weight']}),
#         ('Personal info', {'fields': ('first_name', 'last_name')}),
#         ('Permissions', {'fields': ('is_active',)}),
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ['company', 'username', 'weight', 'is_active', 'password1', 'password2']}
#          ),
#     )
#     search_fields = ('username')
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
