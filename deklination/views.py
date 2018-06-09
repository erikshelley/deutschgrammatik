# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Noun, GenderQuizScore
import random, math
from datetime import timedelta
from django.utils import timezone
from operator import itemgetter

def index(request):
    context = {}
    context['page_subtitle'] = "Deklination - "
    card1 = {
        'disabled': False, 
        'title': 'Identify Gender',  
        'text': 'The first step in correct declination is to know the gender of the noun in question. If you need practice on noun genders then start here.',
        'button_id': 'begin_gender',
        'button_text': 'Begin Practicing &raquo;',
        'url': 'deklination:gender_quiz'
        #'url': '/deklination/gender_quiz/'
        }
    card2 = {
        'disabled': True,  
        'title': 'Identify Case',  
        'text': 'The second step in correct declination is to know the case of the noun in question. If you need practice on case identification then start here.',
        'button_id': 'begin_case',
        'button_text': 'Coming Soon',
        'url': 'deklination:index'
        }
    card3 = {
        'disabled': True,  
        'title': 'Identify Declension', 
        'text': 'The final step in correct declination is to know what ending to use on the articles, adjectives, pronouns, and nouns.',
        'button_id': 'begin_declension',
        'button_text': 'Coming Soon',
        'url': 'deklination:index'
        }
    context['card_deck'] = [card1, card2, card3]
    return render(request, 'deklination/index.html', context)
    

def gender_quiz_record_response(request):
    noun_key = request.POST['noun'].replace(" | ", "|")
    noun = Noun.objects.get(noun = noun_key, english = request.POST['english'])
    gender_srs, created = GenderQuizScore.objects.get_or_create(
        noun        = noun,
        user        = request.user,
        defaults    = {'easiness_factor': 2.5, 'consecutive_correct': 0, 'interval': 0})
    quality = int(request.POST['quality'])
    if quality < 3:
        gender_srs.consecutive_correct = 0
        gender_srs.interval = 0
    else:
        if gender_srs.interval == 0:
            gender_srs.interval = 1
        elif gender_srs.interval == 1:
            gender_srs.interval = 6
        else:
            gender_srs.interval = math.ceil(gender_srs.interval * gender_srs.easiness_factor)
        gender_srs.consecutive_correct = gender_srs.consecutive_correct + 1
    gender_srs.easiness_factor = gender_srs.easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if gender_srs.easiness_factor < 1.3:
        gender_srs.easiness_factor = 1.3
    quality_count = [0, 0, 0, 0, 0, 0]
    quality_count[quality] = 1
    gender_srs.quality_0 += quality_count[0]
    gender_srs.quality_1 += quality_count[1]
    gender_srs.quality_2 += quality_count[2]
    gender_srs.quality_3 += quality_count[3]
    gender_srs.quality_4 += quality_count[4]
    gender_srs.quality_5 += quality_count[5]
    gender_srs.save()


def gender_quiz_select_question(request, context, nouns):
    if request.user.is_authenticated():
        """ 
        if there are nouns due for review 
          if interval is zero then select noun with longest time since last review (at least five minutes ago)
          if there are no nouns selected yet select noun with the largest ratio of overdue / interval
        if there are no nouns due for review
          select most popular noun not yet reviewed
        """
        reviews = GenderQuizScore.objects.filter(user = request.user).select_related('noun')
        context['review'] = 'Review'
        if len(reviews) > 0:
            unlearned_nouns = []
            overdue_nouns = []
            current_time = timezone.now()
            for review in reviews:
                overdue_amount = current_time - (review.review_date + timedelta(days = review.interval))
                if review.interval == 0:
                    if review.review_date + timedelta(minutes = 5) < current_time:
                        unlearned_nouns.append((review.review_date, review.noun))
                elif overdue_amount.total_seconds() > 0:
                    overdue_nouns.append((overdue_amount.total_seconds() / (review.interval * 24 * 60 * 60), review.noun))
            if len(unlearned_nouns) > 0:
                unlearned_nouns.sort(key=itemgetter(0), reverse=True)
                context['noun'] = unlearned_nouns[0][1]
            elif len(overdue_nouns) > 0:
                overdue_nouns.sort(key=itemgetter(0), reverse=True)
                context['noun'] = overdue_nouns[0][1]
        if 'noun' not in context:
            context['review'] = 'New'
            for noun in nouns:
                review = GenderQuizScore.objects.filter(user = request.user, noun = noun)
                if len(review) == 0:
                    context['noun'] = noun
                    break
    elif len(nouns) > 0:
        context['noun'] = random.choice(nouns)


def gender_quiz(request):
    context = {}
    context['page_subtitle'] = "Gender Quiz - Deklination - "

    if request.method == 'POST':
        gender_quiz_record_response(request)

    nouns = Noun.objects.all().order_by('rank')
    gender_quiz_select_question(request, context, nouns)

    context['count'] = nouns.count()
    if len(nouns) > 0:
        if context['noun'].gender == 'M':
            context['article'] = "Der"
            context['gender'] = "masculine"
        elif context['noun'].gender == 'N':
            context['article'] = "Das"
            context['gender'] = "neuter"
        else:
            context['article'] = "Die"
            context['gender'] = "feminine"
        context['noun'].noun = context['noun'].noun.replace("|", " | ")

    return render(request, 'deklination/gender_quiz.html', context)


