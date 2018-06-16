# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Progress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('review_date', models.DateTimeField(auto_now=True)),
                ('quality_0', models.IntegerField(default=0)),
                ('quality_1', models.IntegerField(default=0)),
                ('quality_2', models.IntegerField(default=0)),
                ('quality_3', models.IntegerField(default=0)),
                ('quality_4', models.IntegerField(default=0)),
                ('quality_5', models.IntegerField(default=0)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['review_date'],
                'verbose_name_plural': 'Progress',
            },
        ),
    ]
