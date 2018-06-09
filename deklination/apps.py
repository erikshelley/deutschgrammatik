# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.apps import AppConfig


class DeklinationConfig(AppConfig):
    name = 'deklination'

    def ready(self):
        import deklination.signals
