# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.apps import AppConfig


class ProgressConfig(AppConfig):
    name = 'progress'

    def ready(self):
        import progress

