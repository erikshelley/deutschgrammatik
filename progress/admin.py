# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Progress

class ProgressAdmin(admin.ModelAdmin):
    list_display = ('review_date', 'user', 'quiz', 'new_count', 'short_count', 'long_count', 'quality_0', 'quality_1', 'quality_2', 'quality_3', 'quality_4', 'quality_5')
    list_filter = ['review_date']
    search_fields = ['user']
    ordering = ['review_date']

admin.site.register(Progress, ProgressAdmin)

