# -*- encoding: utf-8 -*-

from django.contrib import admin

from .models import Survey
from .models import SurveyOption
from .models import SurveyVote
from .models import SurveyResult

from django.conf.locale.en import formats as en_formats
en_formats.DATE_FORMAT = "Y-m-d"

# Register your models here.
class SurveyOptionInline(admin.StackedInline):
    model = SurveyOption
    extra = 0


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'end_date',
    ]
    search_fields = ['title', ]
    ordering = ['-created_at']
    inlines = [
        SurveyOptionInline
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(company_user=request.user)


@admin.register(SurveyOption)
class SurveyOptionAdmin(admin.ModelAdmin):
    list_display = [
        'get_survey_title',
        'text',
    ]
    search_fields = ['get_survey_title', 'text']
    ordering = ['created_at']
    list_display_links = ('get_survey_title', 'text')

    def get_survey_title(self, obj):
        return obj.survey.title
    get_survey_title.short_description = 'Title'
    get_survey_title.admin_order_field = 'survey__title'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(survey__company_user=request.user)


@admin.register(SurveyVote)
class SurveyVoteAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'survey_option',
        'created_at',
    ]
    search_fields = ['user__username', 'survey_option__text', 'survey_option__survey_title']
    ordering = ['created_at']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(survey_option__survey__company_user=request.user)


@admin.register(SurveyResult)
class SurveyResultAdmin(admin.ModelAdmin):
    list_display = [
        'survey',
        'result',
    ]
    search_fields = ['survey_title', ]
    ordering = ['created_at']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(survey__company_user=request.user)
