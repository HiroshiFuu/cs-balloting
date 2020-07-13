# -*- encoding: utf-8 -*-

from django.contrib import admin

from .models import Poll, PollOption
from .models import Voting
from .models import PollResult

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
        'end_date',
    ]
    search_fields = ['title', ]
    ordering = ['-created_at']
    inlines = [
        PollOptionInline
    ]


@admin.register(PollOption)
class PollOptionAdmin(admin.ModelAdmin):
    list_display = [
        'get_poll_title',
        'text',
    ]
    search_fields = ['get_poll_title', 'text']
    ordering = ['created_at']
    list_display_links = ('get_poll_title', 'text')

    def get_poll_title(self, obj):
        return obj.poll.title
    get_poll_title.short_description = 'Title'
    get_poll_title.admin_order_field = 'poll__title'


@admin.register(Voting)
class VotingAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'poll_option',
        'created_at',
    ]
    search_fields = ['user__username', 'poll_option__text', 'poll_option__poll_title']
    ordering = ['created_at']


@admin.register(PollResult)
class PollResultAdmin(admin.ModelAdmin):
    list_display = [
        'poll',
        'result',
    ]
    search_fields = ['poll_title', ]
    ordering = ['created_at']
