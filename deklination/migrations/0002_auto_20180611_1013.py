# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deklination', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='genderquizscore',
            name='quality_0',
        ),
        migrations.RemoveField(
            model_name='genderquizscore',
            name='quality_1',
        ),
        migrations.RemoveField(
            model_name='genderquizscore',
            name='quality_2',
        ),
        migrations.RemoveField(
            model_name='genderquizscore',
            name='quality_3',
        ),
        migrations.RemoveField(
            model_name='genderquizscore',
            name='quality_4',
        ),
        migrations.RemoveField(
            model_name='genderquizscore',
            name='quality_5',
        ),
    ]
