# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Noun, Rule, NounRule, GenderReviewScore

class NounAdmin(admin.ModelAdmin):
    list_display = ('frequency', 'noun', 'gender', 'english', 'nom_plural', 'dat_plural', 'genitive', 'matches_rule')
    list_filter = ['gender']
    search_fields = ['noun']
    ordering = ['-frequency']


class RuleAdmin(admin.ModelAdmin):
    list_display = ('frequency', 'short_name', 'long_name', 'gender', 'percent_right')
    list_filter = ['gender']
    search_fields = ['long_name']
    ordering = ['-frequency']


class NounRuleAdmin(admin.ModelAdmin):
    list_display = ('noun', 'rule', 'is_match')
    list_filter = ['rule']
    search_fields = ['noun__noun']
    ordering = ['rule']


class GenderReviewScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'noun', 'rule', 'first_review', 'review_date', 'easiness_factor', 'interval', 'review_count', 'reviews_missed', 'consecutive_correct')
    list_filter = ['user']
    search_fields = ['noun__noun', 'rule__short_name']
    ordering = ['-review_date']


admin.site.register(Noun, NounAdmin)
admin.site.register(Rule, RuleAdmin)
admin.site.register(NounRule, NounRuleAdmin)
admin.site.register(GenderReviewScore, GenderReviewScoreAdmin)
