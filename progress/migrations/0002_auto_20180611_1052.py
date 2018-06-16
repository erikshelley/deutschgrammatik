# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('progress', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='progress',
            name='quiz',
            field=models.CharField(default=b'DG', max_length=2, choices=[(b'DG', b'Deklination Gender'), (b'DC', b'Deklination Case'), (b'DD', b'Deklination Declension')]),
        ),
        migrations.AlterField(
            model_name='progress',
            name='review_date',
            field=models.DateField(auto_now=True),
        ),
    ]
