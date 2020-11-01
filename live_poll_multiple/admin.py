from django.contrib import admin
from django.contrib.auth import get_user_model

from import_export.admin import ImportExportModelAdmin

from .models import LivePollMultiple
from .models import LivePollMultipleItem
from .models import LivePollMultipleItemVote
from .models import LivePollMultipleProxy
from .models import LivePollMultipleResult

from django.conf.locale.en import formats as en_formats
en_formats.DATE_FORMAT = "Y-m-d"

# Register your models here.
class LivePollMultipleItemInline(admin.StackedInline):
    model = LivePollMultipleItem
    extra = 0
    exclude = ('created_by', 'modified_by')


@admin.register(LivePollMultiple)
class LivePollMultipleAdmin(ImportExportModelAdmin):
    list_display = [
        'batch_no',
        'is_open',
        'opened_at',
        'opening_duration_minustes',
    ]
    inlines = [
        LivePollMultipleItemInline
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
            return super(LivePollMultipleAdmin, self).get_readonly_fields(request, obj)
        else:
            return ('batch_no', 'is_open', 'opened_at')



@admin.register(LivePollMultipleItem)
class LivePollMultipleItemAdmin(ImportExportModelAdmin):
    list_display = [
        'live_poll',
        'text',
    ]
    list_display_links = ('text', )
    search_fields = ['live_poll', 'text']
    exclude = ('created_by', 'modified_by')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(live_poll__company=request.user.company)


@admin.register(LivePollMultipleItemVote)
class LivePollMultipleItemVoteAdmin(ImportExportModelAdmin):
    list_display = [
        'user',
        'live_poll_item',
        'vote_option',
        'ip_address',
        'user_agent',
        'created_at',
    ]
    search_fields = ['user__username', 'live_poll_item__text', 'live_poll_item__poll_title', 'poll_batch__batch_no']
    ordering = ['created_at']
    exclude = ('created_by', 'modified_by')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(live_poll_item__live_poll__company=request.user.company)


@admin.register(LivePollMultipleProxy)
class LivePollMultipleProxyAdmin(ImportExportModelAdmin):
    list_display = [
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
        return super(LivePollMultipleProxyAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_dbfield(self, db_field, request=None, **kwargs):
        if db_field.name == 'proxy_users':
            if not request.user.is_superuser:
                kwargs['queryset'] = get_user_model().objects.filter(company=request.user.company, is_staff=False)
        return super(LivePollMultipleProxyAdmin, self).formfield_for_dbfield(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(main_user__company=request.user.company)


@admin.register(LivePollMultipleResult)
class LivePollMultipleResultAdmin(ImportExportModelAdmin):
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
        return qs.filter(live_poll__company=request.user.company)
