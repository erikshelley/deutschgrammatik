# -*- coding: utf-8 -*-
from __future__                 import unicode_literals
from datetime                   import timedelta
from operator                   import itemgetter
from django.contrib.auth.models import User
from django.shortcuts           import render
from django.utils               import timezone

import random, math, datetime, pytz

from .models                    import Noun, Rule, NounRule, GenderReviewScore
from progress.models            import Progress
from progress.views             import ProgressTracker

def index(request):
    context = {}
    context['page_subtitle'] = "Deklination - "
    card1 = {
        'disabled': False, 
        'title': 'Identify Gender',  
        'text': 'The first step in correct declination is to know the gender of the noun in question. If you need practice on noun genders then start here.',
        'icon': 'list-ul',
        'button_id': 'begin_gender',
        'button_text': 'Practice &raquo;',
        'url': 'deklination:gender_quiz'
        }
    card2 = {
        'disabled': True,  
        'title': 'Identify Case',  
        'text': 'The second step in correct declination is to know the case of the noun in question. If you need practice on case identification then start here.',
        'icon': 'list-ul',
        'button_id': 'begin_case',
        'button_text': 'Coming Soon',
        'url': 'deklination:index'
        }
    card3 = {
        'disabled': True,  
        'title': 'Identify Declension', 
        'text': 'The final step in correct declination is to know what ending to use on the articles, adjectives, pronouns, and nouns.',
        'icon': 'list-ul',
        'button_id': 'begin_declension',
        'button_text': 'Coming Soon',
        'url': 'deklination:index'
        }
    if request.user.is_authenticated():
        progress = ProgressTracker()
        context['next_review'] = progress.get_next_review(request.user)
        context['dek_reviews'] = progress.get_review_count(request.user, 'DG')
        card1['reviews_due'] = progress.get_review_count(request.user, 'DG')
    context['card_deck'] = [card1, card2, card3]
    rules = Rule.objects.all()
    context['rules'] = rules
    return render(request, 'deklination/index.html', context)
    

def gender_quiz(request):
    context = {}
    context['page_subtitle'] = "Gender Quiz - Deklination - "

    if request.method == 'POST':
        gender_quiz_record_response(request)

    # this needs to be after the response is recorded
    if request.user.is_authenticated():
        progress = ProgressTracker()
        context['next_review'] = progress.get_next_review(request.user)
        context['dek_reviews'] = progress.get_review_count(request.user, 'DG')

    nouns = Noun.objects.all()
    gender_quiz_select_question(request, context, nouns)

    context['count'] = nouns.count()
    if len(nouns) > 0:
        context['dict'] = context['noun'].noun
        if context['noun'].gender == 'M':
            context['article'] = "Der"
            context['gender'] = "masculine"
        elif context['noun'].gender == 'N':
            context['article'] = "Das"
            context['gender'] = "neuter"
        else:
            context['article'] = "Die"
            context['gender'] = "feminine"
        context['noun'].noun = context['noun'].noun

    return render(request, 'deklination/gender_quiz.html', context)


def gender_quiz_select_question(request, context, nouns):
    if request.user.is_authenticated():
        """ 
        if there are reviews
            if there are reviews with interval == 0 with review_date more than ten minutes ago
                select oldest by review_date
            if there are reviews with interval > 0 with review_date + interval > current_time
                select largest ratio of overdue_amount / interval
        if no review yet selected
            determine unreviewed rule with largest frequency
            determine unreviewed noun with largest frequency
            select whichever has largest frequency
        if selection is rule
            select noun that matches rule
        """
        local_time = timezone.now()
        # Look for reviews due with interval = 0
        utc_time = local_time.astimezone(pytz.UTC)
        utc_due = utc_time - timedelta(minutes = 10)
        selected_review = GenderReviewScore.objects.filter(user = request.user, interval = 0, review_date__lt = utc_due).order_by('-review_date').first()

        # Look for reviews due with interval > 0
        if selected_review is None:
            overdue_reviews = []
            reviews = GenderReviewScore.objects.filter(user = request.user, interval__gt = 0)
            for review in reviews:
                overdue_amount = local_time - (review.review_date + timedelta(days = review.interval))
                if overdue_amount.total_seconds() > 0:
                    overdue_reviews.append((overdue_amount.total_seconds() / (review.interval * 24 * 60 * 60), review))
            if len(overdue_reviews) > 0:
                overdue_reviews.sort(key=itemgetter(0), reverse=True)
                selected_review = overdue_reviews[0][1]

        # Look for new rule or noun to study
        if selected_review is None:
            reviewed_rules = list(GenderReviewScore.objects.filter(user = request.user).exclude(rule__isnull = True).values_list('rule', flat=True))
            unreviewed_rule = Rule.objects.exclude(id__in = reviewed_rules).order_by('-frequency').first()

            reviewed_nouns = list(GenderReviewScore.objects.filter(user = request.user).exclude(noun__isnull = True).values_list('noun', flat=True))
            nouns_with_rules = list(NounRule.objects.filter(is_match = True).values_list('noun', flat=True))
            unreviewed_noun = Noun.objects.exclude(id__in = reviewed_nouns).exclude(id__in = nouns_with_rules).order_by('-frequency').first()

            if unreviewed_rule.frequency >= unreviewed_noun.frequency:
                context['review'] = 'New'
                context['rule'] = unreviewed_rule
                noun_index = 0
            else:
                context['review'] = 'New'
                context['noun'] = unreviewed_noun
        else:
            if selected_review.rule is None:
                context['review'] = 'Review'
                context['noun'] = selected_review.noun
            else:
                #reviewed_nouns = list(GenderReviewScore.objects.filter(user = request.user).values_list('noun', flat=True))
                context['review'] = 'Review'
                context['rule'] = selected_review.rule
                noun_index = selected_review.review_count

        if 'rule' in context:
            """
            if there are unreviewed nouns matching the rule select the most popular
            if all nouns matching the rule have been reviewed select oldest
            """
            #nouns_matching_rule = list(NounRule.objects.filter(rule = context['rule'], is_match = True).values_list('noun', flat=True))
            #unreviewed_noun = Noun.objects.filter(id__in = nouns_matching_rule).exclude(id__in = reviewed_nouns).order_by('-frequency').first()
            #if unreviewed_noun is None:
            #    oldest_review = GenderReviewScore.objects.filter(user = request.user, rule = context['rule']).order_by('review_date').first()
            #    context['noun'] = oldest_review.noun;
            #else:
            #    context['noun'] = unreviewed_noun
            nouns_matching_rule = NounRule.objects.filter(rule = context['rule'], is_match = True).select_related('noun')
            #context['noun'] = random.choice(nouns_matching_rule).noun
            noun_index = noun_index % len(nouns_matching_rule)
            context['noun'] = nouns_matching_rule[noun_index].noun

            matches = NounRule.objects.filter(noun = context['noun'], is_match = True).exclude(rule = context['rule']).select_related('rule')
            exceptions = NounRule.objects.filter(noun = context['noun'], is_match = False).exclude(rule = context['rule']).select_related('rule')
        else:
            matches = NounRule.objects.filter(noun = context['noun'], is_match = True).select_related('rule')
            exceptions = NounRule.objects.filter(noun = context['noun'], is_match = False).select_related('rule')

        if len(matches) > 0:
            context['matches'] = matches

        if len(exceptions) > 0:
            context['exceptions'] = exceptions

    else:
        """
        for unauthenticated users select a random noun (if there are nouns to choose from)
        """
        if len(nouns) > 0:
            context['noun'] = random.choice(nouns)
            context['review'] = 'Random Selection'

            matches = NounRule.objects.filter(noun = context['noun'], is_match = True).select_related('rule')
            exceptions = NounRule.objects.filter(noun = context['noun'], is_match = False).select_related('rule')
            if len(matches) > 0:
                context['matches'] = matches
            if len(exceptions) > 0:
                context['exceptions'] = exceptions


def gender_quiz_record_response(request):
    new_delta = 0
    short_delta = 0
    long_delta = 0


    # Lookup rule, or noun if no rule
    if 'rule' in request.POST:
        rule_key = request.POST['rule']
        rule = Rule.objects.get(short_name = rule_key)
        noun = None
    else:
        noun_key = request.POST['noun'].replace(" | ", "|")
        noun = Noun.objects.get(noun = noun_key, english = request.POST['english'])
        rule = None

    # Lookup review score
    gender_srs, created = GenderReviewScore.objects.get_or_create(
        noun        = noun,
        rule        = rule,
        user        = request.user,
        defaults    = {'review_count': 0, 'easiness_factor': 2.5, 'consecutive_correct': 0, 'interval': 0})

    # Prevent re-submitting quality score
    if not created:
        current_time = timezone.now()
        if gender_srs.interval == 0:
            if gender_srs.review_date + timedelta(minutes = 10) > current_time:
                return
        else:
            if gender_srs.review_date + timedelta(days = gender_srs.interval) > current_time:
                return

    quality = int(request.POST['quality'])
    gender_srs.review_count += 1
    if created:
        gender_srs.status = 'N'
        new_delta = 1
    if quality < 3:
        gender_srs.consecutive_correct = 0
        gender_srs.interval = 0
        gender_srs.reviews_missed += 1
        if gender_srs.status == 'L':
            gender_srs.status = 'S'
            short_delta = 1
            long_delta = -1
    else:
        if gender_srs.interval == 0:
            gender_srs.interval = 1
        elif gender_srs.interval == 1:
            gender_srs.interval = 6
        else:
            gender_srs.interval = math.ceil(gender_srs.interval * gender_srs.easiness_factor)
        gender_srs.consecutive_correct = gender_srs.consecutive_correct + 1
    if gender_srs.interval >= 14:
        if gender_srs.status == 'N':
            gender_srs.status = 'S'
            new_delta = -1
            short_delta = 1
    if gender_srs.interval >= 21:
        gender_srs.status = 'L'
        short_delta = -1
        long_delta = 1
    gender_srs.easiness_factor = gender_srs.easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if gender_srs.easiness_factor < 1.3:
        gender_srs.easiness_factor = 1.3
    gender_srs.save()
    progress = ProgressTracker()
    progress.update_progress(request.user, 'DG', quality, new_delta, short_delta, long_delta)


"""
case_quiz
  record response or select question
  context : german sentence, english sentence, noun, case


select_question
  guest users see random sentence
  select rule (due for review if exists otherwise new)
  select sentence for rule based on score and rule review counter


record_response
  create or update casereviewscore
  update progress tracker


http://linguatools.org/tools/corpora/webcrawl-parallel-corpus-german-english-2015/#excluded
sentence_loader
  for each sentence
      count words
      for each noun
          determine noun frequency & gender
          determine if noun is nominative plural, dative plural, or genitive
              sort sentences by number of letters and words 
                  awk '{gsub(/^[^A-Za-z0-9]+/,"",$0); printf("%07d\t%d\t%d\t%s\n", NR, length($0), NF, $0);}' europarl-v7.de-en.de > europarl-v7.de-en.de.num
                  awk '{gsub(/^[^A-Za-z0-9]+/,"",$0); printf("%07d\t%d\t%d\n", NR, length($0), NF);}' europarl-v7.de-en.de > europarl-v7.de-en.de.nums
                  paste -d '\t' europarl-v7.de-en.de.nums  europarl-v7.de-en.en > europarl-v7.de-en.en.num
                  sort -n -k2,2 -k3,3r -k1,1 europarl-v7.de-en.de.num > europarl-v7.de-en.de.srt
              discard long sentences (and very short sentences)
                  discard <3 words
                      grep -vE $'^[0-9]{7}\t[0-9]+\t[0-2]\t' europarl-v7.de-en.de.srt > europarl-v7.de-en.de.nos
                      grep -vE $'^[0-9]{7}\t[0-9]+\t[0-2]\t' europarl-v7.de-en.en.srt > europarl-v7.de-en.en.nos
                  discard >80 characters
                      manual edit in vim
              build list of unique capitalized words
                  sed -r -e 's/^[0-9]{7}\t[0-9]+\t[0-9]+\t//' -e 's/[A-Z][a-z]+//' -e 's/[0-9.,!%?()":;\/]//g' -e 's/\+/ /g' -e "s/'|-|\[|\]//g" -e 's/\b[a-z]+\b//g' -e 's/[ ]{2,20}/ /g' -e 's/^ //' -e 's/ /\n/g' *.de.nos | 
                      sort -u > europarl-v7.de-en.de.cap
              combine list with unique list of nouns (comm --help)
                  noun list from Excel
                  sort -u europarl-v7.de-en.noun-list | sed 's/^$\n//' > europarl-v7.de-en.nouns
                  manual edit (first row)
                  comm -12 europarl-v7.de-en.de.cap_mod europarl-v7.de-en.nouns > europarl-v7.de-en.de.nouns
                  manual edits
              find lines that contain items from this combined list
                  sed -r -e 's/[A-Z][a-z]+\b//' europarl-v7.de-en.de.nos | sort -n > europarl-v7.de-en.de.nos.rest
                  grep -w -F -f europarl-v7.de-en.de.nouns europarl-v7.de-en.de.nos.rest | sed -r -e 's/^([0-9]{7}).*/\1/' > europarl-v7.de-en.de.row_nums
                  sort -n europarl-v7.de-en.de.nos > europarl-v7.de-en.de.nos.srt
                  sort -n europarl-v7.de-en.en.nos > europarl-v7.de-en.en.nos.srt
                  grep -w -F -f europarl-v7.de-en.de.row_nums europarl-v7.de-en.de.nos.srt > europarl-v7.de-en.de.final
                  grep -w -F -f europarl-v7.de-en.de.row_nums europarl-v7.de-en.en.nos.srt > europarl-v7.de-en.en.final
                      
          determine if form is adj:noun, dir:noun, ind:noun, dir:adj:noun, ind:adj:noun (dir & ind include pronouns)
              how? 
                  scan each word through columns of article and adjective tables?
          determine case
              nominative
                  ind    : adj-er : mas
                  dir-er : adj-e  : mas
                           adj-er : mas
              accusative
                  ind-en : adj-en : mas
                  dir-en : adj-en : mas
                           adj-en : mas
              dative
                  ind-em : adj-en : mas
                  dir-em : adj-en : mas
                           adj-em : mas
                  ind-em : adj-en : neu
                  dir-em : adj-en : neu
                           adj-em : neu
                  ind-en : adj-en : plu-dat
                  dir-en : adj-en : plu-dat
                           adj-en : plu-dat
                                    plu-dat
              genitive
                  ind-es : adj-en : mas-gen
                  dir-es : adj-en : mas-gen
                           adj-en : mas-gen
                                    mas-gen
                  ind-es : adj-en : neu-gen
                  dir-es : adj-en : neu-gen
                           adj-en : neu-gen
                                    neu-gen
                  ind-er : adj-en : plu-nom
                  dir-er : adj-en : plu-nom
                           adj-er : plu-nom
              nominative or accusative
                  ind    : adj-es : neu
                  dir-es : adj-e  : neu
                           adj-es : neu
                  ind-e  : adj-e  : fem
                  dir-e  : adj-e  : fem
                           adj-e  : fem
                  ind-e  : adj-en : plu-nom
                  dir-e  : adj-en : plu-nom
                           adj-e  : plu-nom
              dative or genitive
                  ind-er : adj-en : fem
                  dir-er : adj-en : fem
                           adj-er : fem
          determine rule(s)
              subject vs object vs direct object (sentence unlikely to have more than one of each?)
              nominative has no preposition?
              accusative preposition
              dative preposition
              genitive preposition
              two-way preposition (accusative:wohin or dative:wo)
              dative verb
          flag ambiguous cases for review
          flag ambiguous rules for review
      reject sentences
          no known noun
          too many words
          save to rejected sentence files (german & english)
      if not rejected
          save sentence-entry (german, english)
          calculate score (sentence length, noun-frequency)
          save case-entry with score, sentence id, noun id, case, rule, needs_review



"""




