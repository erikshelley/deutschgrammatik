# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('progress', '0004_auto_20180612_1123'),
    ]

    operations = [
        migrations.AddField(
            model_name='progress',
            name='long_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='progress',
            name='new_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='progress',
            name='short_count',
            field=models.IntegerField(default=0),
        ),
    ]
