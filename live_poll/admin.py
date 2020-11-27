# -*- encoding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth import get_user_model

from import_export.admin import ImportExportModelAdmin
from adminsortable2.admin import SortableAdminMixin

from .models import LivePoll
from .models import LivePollItem
from .models import LivePollItemVote
from .models import LivePollProxy
from .models import LivePollResult
from .models import LivePollBatch

from authentication.constants import USER_TYPE_COMPANY

from django.conf.locale.en import formats as en_formats
en_formats.DATE_FORMAT = "Y-m-d"

# Register your models here.
class LivePollItemInline(admin.StackedInline):
    model = LivePollItem
    extra = 0
    exclude = ('created_by', 'modified_by')


@admin.register(LivePoll)
class LivePollAdmin(ImportExportModelAdmin):
    list_display = [
        'title',
        'is_chosen',
    ]
    inlines = [
        LivePollItemInline
    ]
    search_fields = ['title', ]
    ordering = ['-created_at']
    exclude = ('created_by', 'modified_by')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(company=request.user.company)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return super(LivePollAdmin, self).get_readonly_fields(request, obj)
        else:
            return ('company', )

    def save_model(self, request, obj, form, change):
        # print('save_model', obj, change)
        if not change and request.user.user_type == USER_TYPE_COMPANY:
            obj.company = request.user.company
        super().save_model(request, obj, form, change)


@admin.register(LivePollItem)
class LivePollItemAdmin(SortableAdminMixin, ImportExportModelAdmin):
    list_display = [
        'order',
        'poll',
        'text',
        'is_open',
        'opened_at',
        'opening_duration_minustes',
        'poll_type',
    ]
    list_display_links = ('text', )
    search_fields = ['text', 'poll']
    exclude = ('created_by', 'modified_by')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(poll__company=request.user.company)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return super(LivePollMultipleAdmin, self).get_readonly_fields(request, obj)
        else:
            return ('is_open', 'opened_at')


@admin.register(LivePollItemVote)
class LivePollItemVoteAdmin(ImportExportModelAdmin):
    list_display = [
        'user',
        'poll_item',
        'poll_batch',
        'vote_option',
        'ip_address',
        'user_agent',
        'created_at',
    ]
    list_filter = ['poll_batch', 'poll_item']
    search_fields = ['user__username', 'poll_item__text', 'poll_item__poll_title', 'poll_batch__batch_no']
    ordering = ['created_at']
    exclude = ('created_by', 'modified_by')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(poll_item__poll__company=request.user.company)


@admin.register(LivePollProxy)
class LivePollProxyAdmin(ImportExportModelAdmin):
    list_display = [
        'poll_batch',
        'main_user',
    ]
    filter_horizontal = ('proxy_users',)
    search_fields = ['main_user__username']
    ordering = ['created_at']
    exclude = ('created_by', 'modified_by')

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'main_user':
            if not request.user.is_superuser:
                kwargs['queryset'] = get_user_model().objects.filter(company=request.user.company, is_staff=False)
        return super(LivePollProxyAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_dbfield(self, db_field, request=None, **kwargs):
        if db_field.name == 'proxy_users':
            if not request.user.is_superuser:
                kwargs['queryset'] = get_user_model().objects.filter(company=request.user.company, is_staff=False)
        return super(LivePollProxyAdmin, self).formfield_for_dbfield(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(main_user__company=request.user.company)


@admin.register(LivePollResult)
class LivePollResultAdmin(ImportExportModelAdmin):
    list_display = [
        'live_poll',
        'voting_date',
        'result',
    ]
    search_fields = ['live_poll__title', 'voting_date']
    ordering = ['created_at']
    exclude = ('created_by', 'modified_by')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(live_poll__poll__company=request.user.company)


@admin.register(LivePollBatch)
class LivePollBatchAdmin(ImportExportModelAdmin):
    list_display = [
        'poll',
        'batch_no',
    ]
    search_fields = ['poll__title', 'batch_no']
    ordering = ['created_at']
    exclude = ('created_by', 'modified_by')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(poll__company=request.user.company)
