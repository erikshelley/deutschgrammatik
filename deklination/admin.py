# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Noun, GenderQuizScore

class NounAdmin(admin.ModelAdmin):
    list_display = ('noun', 'english', 'gender', 'plural', 'genitive', 'rank')
    list_filter = ['gender']
    search_fields = ['noun']
    ordering = ['rank']

class GenderQuizScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'noun', 'first_review', 'review_date', 'easiness_factor', 'interval', 'review_count', 'reviews_missed', 'consecutive_correct')
    list_filter = ['user']
    search_fields = ['noun__noun']
    ordering = ['review_date']

admin.site.register(Noun, NounAdmin)
admin.site.register(GenderQuizScore, GenderQuizScoreAdmin)
