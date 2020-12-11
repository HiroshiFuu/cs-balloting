from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse

from import_export.admin import ExportMixin

from .models import LivePollMultiple
from .models import LivePollMultipleItem
from .models import LivePollMultipleItemVote
from .models import LivePollMultipleProxy
from .models import LivePollMultipleResult

from authentication.constants import USER_TYPE_COMPANY

from django.conf.locale.en import formats as en_formats
en_formats.DATE_FORMAT = "Y-m-d"

# Register your models here.
class LivePollMultipleItemInline(admin.StackedInline):
    model = LivePollMultipleItem
    extra = 0
    exclude = ('created_by', 'modified_by')


@admin.register(LivePollMultiple)
class LivePollMultipleAdmin(ExportMixin, admin.ModelAdmin):
    list_display = [
        'batch_no',
        'text',
        'is_open',
        'threshold',
        'allocation',
        'opened_at',
        'opening_duration_minustes',
        'agm_audit_report_actions',
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
            return ('is_open', 'opened_at', 'company')

    def save_model(self, request, obj, form, change):
        # print('save_model', obj, change)
        if not change and request.user.user_type == USER_TYPE_COMPANY:
            obj.company = request.user.company
        super().save_model(request, obj, form, change)

    def agm_audit_report_actions(self, obj):
            return format_html('<a href="{preview_url}" target="_blank" class="btn">{preview_text}</a>&nbsp;<a href="{download_url}" target="_blank" class="btn">{download_text}</a>', preview_url=reverse('ballot:preview_pdf', kwargs={'app': 'LPM', 'id': obj.id}), preview_text=_("Preview AGM Audit Report"), download_url=reverse('ballot:download_pdf', kwargs={'app': 'LPM', 'id': obj.id}), download_text=_("Download AGM Audit Report"))
    agm_audit_report_actions.short_description = _("AGM Audit Report Actions")



@admin.register(LivePollMultipleItem)
class LivePollMultipleItemAdmin(ExportMixin, admin.ModelAdmin):
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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'live_poll':
            kwargs['queryset'] = LivePollMultiple.objects.filter(company=request.user.company)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CompanyLivePollMultipleListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Poll')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'poll'

    default_value = None

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        list_of_polls = []
        queryset = LivePollMultiple.objects.filter(company=request.user.company)
        for poll in queryset:
            list_of_polls.append(
                (str(poll.id), str(poll.batch_no) + ' ' + str(poll.text))
            )
        # print('CompanyLivePollMultipleListFilter', list_of_polls, sorted(list_of_polls, key=lambda tp: tp[0]))
        return sorted(list_of_polls, key=lambda tp: tp[0])

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value to decide how to filter the queryset.
        if self.value():
            return queryset.filter(live_poll_item__live_poll=self.value())
        return queryset


@admin.register(LivePollMultipleItemVote)
class LivePollMultipleItemVoteAdmin(ExportMixin, admin.ModelAdmin):
    list_display = [
        'user',
        'live_poll_item',
        'ip_address',
        'user_agent',
        'created_at',
        'proxy_user',
        'is_proxy_vote',
    ]
    list_filter = [CompanyLivePollMultipleListFilter]
    search_fields = ['user__username', 'live_poll_item__text', 'live_poll_item__poll_title']
    ordering = ['created_at']
    exclude = ('created_by', 'modified_by')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(live_poll_item__live_poll__company=request.user.company)

    def is_proxy_vote(self, obj):
        return obj.proxy_user is not None
    is_proxy_vote.boolean = True
    is_proxy_vote.short_description = 'Is Proxy Vote'


@admin.register(LivePollMultipleProxy)
class LivePollMultipleProxyAdmin(ExportMixin, admin.ModelAdmin):
    list_display = [
        'live_poll',
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
        if db_field.name == 'live_poll':
            kwargs['queryset'] = LivePollMultiple.objects.filter(company=request.user.company)
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
class LivePollMultipleResultAdmin(ExportMixin, admin.ModelAdmin):
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
