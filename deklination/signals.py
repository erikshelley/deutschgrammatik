# -*- coding: utf-8 -*-
from .models import Noun
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=Noun)
@receiver(post_save, sender=Noun)
def update_verbose_name(sender, **kwargs):
    Noun._meta.verbose_name_plural = 'nouns (%s)' % Noun.objects.count()

