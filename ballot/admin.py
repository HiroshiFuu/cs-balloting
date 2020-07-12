# -*- encoding: utf-8 -*-

from django.contrib import admin

from .models import Poll, PollOption

from django.conf.locale.en import formats as en_formats
en_formats.DATE_FORMAT = "Y-m-d"

# Register your models here.
class PollOptionInline(admin.StackedInline):
    model = PollOption
    extra = 0


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = [
        'title',
    ]
    search_fields = ['title', ]
    ordering = ['created_at']
    inlines = [
        PollOptionInline
    ]


@admin.register(PollOption)
class PollOptionAdmin(admin.ModelAdmin):
    list_display = [
        'text',
    ]
    search_fields = ['text', ]
    ordering = ['created_at']
