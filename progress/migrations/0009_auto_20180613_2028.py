# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('progress', '0008_auto_20180613_1859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='progress',
            name='review_date',
            field=models.DateField(),
        ),
    ]
