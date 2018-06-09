from django.shortcuts import render

def index(request):
    context = {}
    card1 = {
        'disabled': False, 'title': 'Deklination', 
        'text': 'Practice <strong>declension</strong>. Identify the correct case and apply the correct endings to nouns, pronouns, articles, and adjectives.', 
        'button_id': 'begin_deklination',
        'button_text': 'Begin Practicing &raquo;',
        'url': 'deklination:index'
        }
    card2 = {
        'disabled': True,  
        'title': 'Konjugation',  
        'text': 'Practice verb <strong>conjugation</strong>. Identify the correct tense and apply the correct form of the verb.',
        'button_id': 'begin_konjugation',
        'button_text': 'Coming Soon',
        'url': 'index'
        }
    card3 = {
        'disabled': True,  
        'title': 'Wortstellung', 
        'text': 'Practice <strong>word order</strong>. Identify clauses and apply the correct word order.',
        'button_id': 'begin_wortstellung',
        'button_text': 'Coming Soon',
        'url': 'index'
        }
    context['card_deck'] = [card1, card2, card3]
    return render(request, 'index.html', context)


