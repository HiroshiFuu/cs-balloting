# -*- encoding: utf-8 -*-

from django.contrib import admin

from import_export.admin import ImportExportModelAdmin
from adminsortable2.admin import SortableAdminMixin

from .models import Survey
from .models import SurveyOption
from .models import SurveyVote
from .models import SurveyResult
from .models import LivePoll
from .models import LivePollItem
from .models import LivePollItemVote

from django.conf.locale.en import formats as en_formats
en_formats.DATE_FORMAT = "Y-m-d"

# Register your models here.
class SurveyOptionInline(admin.StackedInline):
    model = SurveyOption
    extra = 0
    exclude = ('created_by', 'modified_by')


@admin.register(Survey)
class SurveyAdmin(ImportExportModelAdmin):
    list_display = [
        'title',
        'end_date',
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


@admin.register(SurveyOption)
class SurveyOptionAdmin(ImportExportModelAdmin):
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
class SurveyVoteAdmin(ImportExportModelAdmin):
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
class SurveyResultAdmin(ImportExportModelAdmin):
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


@admin.register(LivePollItem)
class LivePollItemAdmin(SortableAdminMixin, ImportExportModelAdmin):
    list_display = [
        'order',
        'poll',
        'text',
        'is_open',
        'opened_at',
        'opening_duration_minustes',
    ]
    list_display_links = ('text', )
    search_fields = ['text', 'poll']
    exclude = ('created_by', 'modified_by')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(poll__company=request.user.company)


@admin.register(LivePollItemVote)
class LivePollItemVoteAdmin(ImportExportModelAdmin):
    list_display = [
        'user',
        'poll_item',
        'vote_option',
        'created_at',
    ]
    search_fields = ['user__username', 'poll_item__text', 'poll_item__poll_title']
    ordering = ['created_at']
    exclude = ('created_by', 'modified_by')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(poll_item__poll__company=request.user.company)
