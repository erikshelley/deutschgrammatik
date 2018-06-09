# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Noun, GenderQuizScore

class NounAdmin(admin.ModelAdmin):
    list_display = ('noun', 'english', 'gender', 'plural', 'genitive', 'rank')
    list_filter = ['gender']
    search_fields = ['noun']

class GenderQuizScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'noun', 'review_date', 'easiness_factor', 'interval', 'consecutive_correct', 'quality_0', 'quality_1', 'quality_2', 'quality_3', 'quality_4', 'quality_5')
    list_filter = ['user']
    search_fields = ['noun__noun']

admin.site.register(Noun, NounAdmin)
admin.site.register(GenderQuizScore, GenderQuizScoreAdmin)
