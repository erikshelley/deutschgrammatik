# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('deklination', '0002_auto_20180611_1013'),
    ]

    operations = [
        migrations.AddField(
            model_name='genderquizscore',
            name='first_review',
            field=models.DateField(default=datetime.datetime(2018, 6, 12, 18, 23, 14, 597314, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='genderquizscore',
            name='review_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='genderquizscore',
            name='reviews_missed',
            field=models.IntegerField(default=0),
        ),
    ]
