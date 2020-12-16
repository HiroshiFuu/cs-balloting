# -*- encoding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse

from import_export.admin import ExportMixin
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
class LivePollAdmin(ExportMixin, admin.ModelAdmin):
    list_display = [
        'title',
        'is_chosen',
        'agm_audit_report_actions',
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
        if change:
            LivePoll.objects.filter(company=obj.company).update(is_chosen=False)
        super().save_model(request, obj, form, change)

    def agm_audit_report_actions(self, obj):
        return format_html('<a href="{preview_url}" target="_blank" class="btn">{preview_text}</a>&nbsp;<a href="{download_url}" target="_blank" class="btn">{download_text}</a>', preview_url=reverse('ballot:preview_pdf', kwargs={'app': 'LP', 'id': obj.id}), preview_text=_("Preview AGM Audit Report"), download_url=reverse('ballot:download_pdf', kwargs={'app': 'LP', 'id': obj.id}), download_text=_("Download AGM Audit Report"))
    agm_audit_report_actions.short_description = _("AGM Audit Report Actions")


@admin.register(LivePollItem)
class LivePollItemAdmin(SortableAdminMixin, ExportMixin, admin.ModelAdmin):
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
            return super(LivePollItemAdmin, self).get_readonly_fields(request, obj)
        else:
            return ('is_open', 'opened_at')


class CompanyLivePollItemBatchListFilter(admin.SimpleListFilter):
    title = _('Poll Batch')
    parameter_name = 'poll_batch'
    default_value = None

    def lookups(self, request, model_admin):
        list_of_poll_batchs = []
        queryset = LivePollBatch.objects.filter(poll__company=request.user.company)
        for batch in queryset:
            list_of_poll_batchs.append(
                (str(batch.id), str(batch.batch_no))
            )
        # print('CompanyLivePollItemBatchListFilter', list_of_poll_batchs, sorted(list_of_poll_batchs, key=lambda tp: tp[0]))
        return sorted(list_of_poll_batchs, key=lambda tp: tp[0])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(poll_batch=self.value())
        return queryset


class CompanyLivePollItemListFilter(admin.SimpleListFilter):
    title = _('Poll Item')
    parameter_name = 'poll_item'
    default_value = None

    def lookups(self, request, model_admin):
        list_of_poll_items = []
        poll = LivePoll.objects.filter(company=request.user.company, is_chosen=True).first()
        queryset = LivePollItem.objects.filter(poll=poll).order_by('order')
        for item in queryset:
            list_of_poll_items.append(
                (str(item.id), str(item.text))
            )
        # print('CompanyLivePollItemListFilter', list_of_poll_items, sorted(list_of_poll_items, key=lambda tp: tp[0]))
        return sorted(list_of_poll_items, key=lambda tp: tp[0])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(poll_batch=self.value())
        return queryset


@admin.register(LivePollItemVote)
class LivePollItemVoteAdmin(ExportMixin, admin.ModelAdmin):
    list_display = [
        'user',
        'poll_item',
        'poll_batch',
        'vote_option',
        'ip_address',
        'user_agent',
        'created_at',
        'proxy_user',
    ]
    list_filter = [CompanyLivePollItemBatchListFilter, CompanyLivePollItemListFilter]
    search_fields = ['user__username', 'poll_item__text', 'poll_item__poll_title', 'poll_batch__batch_no']
    ordering = ['created_at']
    exclude = ('created_by', 'modified_by')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(poll_item__poll__company=request.user.company)


@admin.register(LivePollProxy)
class LivePollProxyAdmin(ExportMixin, admin.ModelAdmin):
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
        if db_field.name == 'poll_batch':
            kwargs['queryset'] = LivePollBatch.objects.filter(poll__company=request.user.company)
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
class LivePollResultAdmin(ExportMixin, admin.ModelAdmin):
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


@admin.register(LivePollBatch)
class LivePollBatchAdmin(ExportMixin, admin.ModelAdmin):
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
