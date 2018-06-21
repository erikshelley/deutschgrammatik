# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User


class Noun(models.Model):
    MASCULINE = 'M'
    NEUTER    = 'N'
    FEMININE  = 'F'
    PLURAL    = 'PL'
    GENDER_CHOICES = (
        (MASCULINE, 'Masculine'),
        (NEUTER,    'Neuter'),
        (FEMININE,  'Feminine'),
        (PLURAL,    'Plural'),
    )
    frequency    = models.IntegerField(help_text='Enter word frequency (higher = more popular)', default=0)
    noun         = models.CharField(max_length=32, help_text='Enter noun')
    gender       = models.CharField(max_length=2, choices=GENDER_CHOICES)
    english      = models.TextField(max_length=420, help_text='Enter English translation(s)')
    nom_plural   = models.CharField(max_length=32, help_text='Enter nominative plural form', blank=True)
    dat_plural   = models.CharField(max_length=32, help_text='Enter dative plural form', blank=True)
    genitive     = models.CharField(max_length=32, help_text='Enter genitive form', blank=True)
    matches_rule = models.BooleanField(help_text='Does noun+gender match any rule', default=False)

    class Meta:
        index_together = ['noun', 'gender']
        ordering = ['-frequency']

    def __unicode__(self):
        return u'%s' % self.noun + ':' + self.gender


class Rule(models.Model):
    MASCULINE = 'M'
    NEUTER    = 'N'
    FEMININE  = 'F'
    PLURAL    = 'PL'
    GENDER_CHOICES = (
        (MASCULINE, 'Masculine'),
        (NEUTER,    'Neuter'),
        (FEMININE,  'Feminine'),
        (PLURAL,    'Plural'),
    )
    frequency     = models.IntegerField(help_text='Enter word frequency (higher = more popular)')
    short_name    = models.CharField(max_length=16, help_text='Enter short name for rule', db_index=True)
    long_name     = models.CharField(max_length=64, help_text='Enter long name for rule')
    gender        = models.CharField(max_length=2, choices=GENDER_CHOICES)
    percent_right = models.FloatField(help_text='How often is this rule correct')

    class Meta:
        ordering = ['-frequency']

    def pretty_percent(self):
        return str(int(self.percent_right * 100)) + '%'

    def __unicode__(self):
        return u'%s' % self.short_name


class NounRule(models.Model):
    noun     = models.ForeignKey('Noun', on_delete=models.CASCADE, blank=True, null=True)
    rule     = models.ForeignKey('Rule', on_delete=models.CASCADE, blank=True, null=True)
    is_match = models.BooleanField(help_text='Does noun+gender match the rule', default=False)

    class Meta:
        ordering = ['rule']
        verbose_name_plural = 'Noun Rules'


class GenderReviewScore(models.Model):
    NEW_TERM = 'N'
    SHORT_TERM = 'S'
    LONG_TERM = 'L'
    STATUS_CHOICES = (
        (NEW_TERM, 'New'),
        (SHORT_TERM, 'Short'),
        (LONG_TERM, 'Long'),
    )
    easiness_factor     = models.FloatField(help_text='From 1.3 (hard) to 2.5 (easy)')
    consecutive_correct = models.IntegerField(help_text='Zero or greater')
    interval            = models.IntegerField(help_text='One or greater')
    review_date         = models.DateTimeField(auto_now=True)
    first_review        = models.DateTimeField(auto_now_add=True)
    review_count        = models.IntegerField(default=0)
    reviews_missed      = models.IntegerField(default=0)
    status              = models.CharField(max_length=1, choices=STATUS_CHOICES, default='N')
    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    noun                = models.ForeignKey('Noun', on_delete=models.CASCADE, blank=True, null=True)
    rule                = models.ForeignKey('Rule', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ['-review_date']
        index_together = ['user', 'noun', 'rule']
        verbose_name_plural = 'Gender Review Scores'

    def __unicode__(self):
        if self.noun is None:
            return self.user.username + ':' + u'%s' % self.rule.short_name
        else:
            return self.user.username + ':' + u'%s' % self.noun.noun

