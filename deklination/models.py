# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User


#@python_2_unicode_compatible
class Noun(models.Model):
    MASCULINE = 'M'
    NEUTER = 'N'
    FEMININE = 'F'
    GENDER_CHOICES = (
        (MASCULINE, "Masculine"),
        (NEUTER, "Neuter"),
        (FEMININE, "Feminine"),
    )
    rank        = models.IntegerField(help_text="Enter popularity rank (1=most popular)", blank=True, null=True)
    noun        = models.CharField(unique=True, max_length=64, help_text="Enter noun")
    gender      = models.CharField(max_length=1, choices=GENDER_CHOICES)
    genitive    = models.CharField(max_length=64, help_text="Enter genitive form", blank=True)
    plural      = models.CharField(max_length=64, help_text="Enter plural form", blank=True)
    english     = models.TextField(help_text="Enter English translation(s)", blank=True)

    class Meta:
        ordering = ["noun"]

    def english_list(self):
        return self.english.split('|')

    #def __str__(self):
    #    return self.noun

    def __unicode__(self):
        return u'%s' % self.noun


class GenderQuizScore(models.Model):
    easiness_factor     = models.FloatField(help_text="From 1.3 (hard) to 2.5 (easy)")
    consecutive_correct = models.IntegerField(help_text="Zero or greater")
    interval            = models.IntegerField(help_text="One or greater")
    review_date         = models.DateTimeField(auto_now=True)
    quality_0           = models.IntegerField(default=0)
    quality_1           = models.IntegerField(default=0)
    quality_2           = models.IntegerField(default=0)
    quality_3           = models.IntegerField(default=0)
    quality_4           = models.IntegerField(default=0)
    quality_5           = models.IntegerField(default=0)
    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    noun                = models.ForeignKey("Noun", on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Gender Quiz Scores"

    #def save(self, *args, **kwargs):
    #    super(GenderQuizScore, self).save(*args, **kwargs)
    #    print('Save method executed!')

    #def __str__(self):
    #    return self.user.username + ":" + self.noun.noun

    def __unicode__(self):
        return self.user.username + ":" + u'%s' % self.noun.noun
        #return self.user.username + ":" + self.noun.noun.encode('utf-8')
        

