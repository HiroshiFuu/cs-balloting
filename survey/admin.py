# -*- encoding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse

from import_export.admin import ExportMixin

from .models import Survey
from .models import SurveyOption
from .models import SurveyVote
from .models import SurveyResult

from authentication.constants import USER_TYPE_COMPANY

from django.conf.locale.en import formats as en_formats
en_formats.DATE_FORMAT = "Y-m-d"

# Register your models here.
class SurveyOptionInline(admin.StackedInline):
    model = SurveyOption
    extra = 0
    exclude = ('created_by', 'modified_by')


@admin.register(Survey)
class SurveyAdmin(ExportMixin, admin.ModelAdmin):
    list_display = [
        'title',
        'end_date',
        'agm_audit_report_actions',
    ]
    search_fields = ['title', ]
    ordering = ['-created_at']
    inlines = [
        SurveyOptionInline
    ]
    exclude = ('created_by', 'modified_by')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(company=request.user.company)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return super(SurveyAdmin, self).get_readonly_fields(request, obj)
        else:
            return ('company', )

    def save_model(self, request, obj, form, change):
        # print('save_model', obj, change)
        if not change and request.user.user_type == USER_TYPE_COMPANY:
            obj.company = request.user.company
        super().save_model(request, obj, form, change)

    def agm_audit_report_actions(self, obj):
        return format_html('<a href="{preview_url}" target="_blank" class="btn">{preview_text}</a>&nbsp;<a href="{download_url}" target="_blank" class="btn">{download_text}</a>', preview_url=reverse('ballot:preview_pdf', kwargs={'app': 'SV', 'id': obj.id}), preview_text=_("Preview AGM Audit Report"), download_url=reverse('ballot:download_pdf', kwargs={'app': 'SV', 'id': obj.id}), download_text=_("Download AGM Audit Report"))
    agm_audit_report_actions.short_description = _("AGM Audit Report Actions")


@admin.register(SurveyOption)
class SurveyOptionAdmin(ExportMixin, admin.ModelAdmin):
    list_display = [
        'get_survey_title',
        'text',
    ]
    search_fields = ['get_survey_title', 'text']
    ordering = ['created_at']
    list_display_links = ('get_survey_title', 'text')
    exclude = ('created_by', 'modified_by')

    def get_survey_title(self, obj):
        return obj.survey.title
    get_survey_title.short_description = 'Title'
    get_survey_title.admin_order_field = 'survey__title'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(survey__company=request.user.company)


@admin.register(SurveyVote)
class SurveyVoteAdmin(ExportMixin, admin.ModelAdmin):
    list_display = [
        'user',
        'survey_option',
        'created_at',
    ]
    search_fields = ['user__username', 'survey_option__text', 'survey_option__survey_title']
    ordering = ['created_at']
    exclude = ('created_by', 'modified_by')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(survey_option__survey__company=request.user.company)


@admin.register(SurveyResult)
class SurveyResultAdmin(ExportMixin, admin.ModelAdmin):
    list_display = [
        'survey',
        'result',
    ]
    search_fields = ['survey_title', ]
    ordering = ['created_at']
    exclude = ('created_by', 'modified_by')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(survey__company=request.user.company)