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
            name='GenderReviewScore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('easiness_factor', models.FloatField(help_text='From 1.3 (hard) to 2.5 (easy)')),
                ('consecutive_correct', models.IntegerField(help_text='Zero or greater')),
                ('interval', models.IntegerField(help_text='One or greater')),
                ('review_date', models.DateTimeField(auto_now=True)),
                ('first_review', models.DateTimeField(auto_now_add=True)),
                ('review_count', models.IntegerField(default=0)),
                ('reviews_missed', models.IntegerField(default=0)),
                ('status', models.CharField(default='N', max_length=1, choices=[('N', 'New'), ('S', 'Short'), ('L', 'Long')])),
            ],
            options={
                'ordering': ['-review_date'],
                'verbose_name_plural': 'Gender Review Scores',
            },
        ),
        migrations.CreateModel(
            name='Noun',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('frequency', models.IntegerField(default=0, help_text='Enter word frequency (higher = more popular)')),
                ('noun', models.CharField(help_text='Enter noun', max_length=32)),
                ('gender', models.CharField(max_length=2, choices=[('M', 'Masculine'), ('N', 'Neuter'), ('F', 'Feminine'), ('PL', 'Plural')])),
                ('english', models.TextField(help_text='Enter English translation(s)', max_length=420)),
                ('nom_plural', models.CharField(help_text='Enter nominative plural form', max_length=32, blank=True)),
                ('dat_plural', models.CharField(help_text='Enter dative plural form', max_length=32, blank=True)),
                ('genitive', models.CharField(help_text='Enter genitive form', max_length=32, blank=True)),
                ('matches_rule', models.BooleanField(default=False, help_text='Does noun+gender match any rule')),
            ],
            options={
                'ordering': ['-frequency'],
            },
        ),
        migrations.CreateModel(
            name='NounRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_match', models.BooleanField(default=False, help_text='Does noun+gender match the rule')),
                ('noun', models.ForeignKey(blank=True, to='deklination.Noun', null=True)),
            ],
            options={
                'ordering': ['rule'],
                'verbose_name_plural': 'Noun Rules',
            },
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('frequency', models.IntegerField(help_text='Enter word frequency (higher = more popular)')),
                ('short_name', models.CharField(help_text='Enter short name for rule', max_length=16, db_index=True)),
                ('long_name', models.CharField(help_text='Enter long name for rule', max_length=64)),
                ('gender', models.CharField(max_length=2, choices=[('M', 'Masculine'), ('N', 'Neuter'), ('F', 'Feminine'), ('PL', 'Plural')])),
                ('percent_right', models.FloatField(help_text='How often is this rule correct')),
            ],
            options={
                'ordering': ['-frequency'],
            },
        ),
        migrations.AddField(
            model_name='nounrule',
            name='rule',
            field=models.ForeignKey(blank=True, to='deklination.Rule', null=True),
        ),
        migrations.AlterIndexTogether(
            name='noun',
            index_together=set([('noun', 'gender')]),
        ),
        migrations.AddField(
            model_name='genderreviewscore',
            name='noun',
            field=models.ForeignKey(blank=True, to='deklination.Noun', null=True),
        ),
        migrations.AddField(
            model_name='genderreviewscore',
            name='rule',
            field=models.ForeignKey(blank=True, to='deklination.Rule', null=True),
        ),
        migrations.AddField(
            model_name='genderreviewscore',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterIndexTogether(
            name='genderreviewscore',
            index_together=set([('user', 'noun', 'rule')]),
        ),
    ]
