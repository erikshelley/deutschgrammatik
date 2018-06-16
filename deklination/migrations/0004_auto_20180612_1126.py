# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deklination', '0003_auto_20180612_1123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genderquizscore',
            name='first_review',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
