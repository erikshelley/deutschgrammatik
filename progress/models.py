# -*- coding: utf-8 -*-
from django.db                  import models
from django.contrib.auth.models import User
from django.utils               import timezone
from deklination.models         import GenderQuizScore


class Progress(models.Model):
    DEKLINATION_GENDER     = 'DG'
    DEKLINATION_CASE       = 'DC'
    DEKLINATION_DECLENSION = 'DD'
    QUIZ_CHOICES = (
        (DEKLINATION_GENDER,     'Deklination Gender'),
        (DEKLINATION_CASE,       'Deklination Case'),
        (DEKLINATION_DECLENSION, 'Deklination Declension'),
        )

    #review_date = models.DateField(auto_now_add=True, editable=True)
    review_date = models.DateField()
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz        = models.CharField(max_length=2, choices=QUIZ_CHOICES, default=DEKLINATION_GENDER)
    new_count   = models.IntegerField(default=0)
    short_count = models.IntegerField(default=0)
    long_count  = models.IntegerField(default=0)
    quality_0   = models.IntegerField(default=0)
    quality_1   = models.IntegerField(default=0)
    quality_2   = models.IntegerField(default=0)
    quality_3   = models.IntegerField(default=0)
    quality_4   = models.IntegerField(default=0)
    quality_5   = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.id:
            review_date = timezone.now()
        return super(Progress, self).save(*args, **kwargs)

    class Meta:
        ordering = ['review_date']
        verbose_name_plural = 'Progress'

    def __unicode__(self):
        return u'%s' % (self.user.username + ":" + self.quiz + ":" + str(self.review_date))

