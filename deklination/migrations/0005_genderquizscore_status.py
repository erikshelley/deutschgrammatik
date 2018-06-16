# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deklination', '0004_auto_20180612_1126'),
    ]

    operations = [
        migrations.AddField(
            model_name='genderquizscore',
            name='status',
            field=models.CharField(default='N', max_length=1, choices=[('N', 'New'), ('S', 'Short'), ('L', 'Long')]),
        ),
    ]
