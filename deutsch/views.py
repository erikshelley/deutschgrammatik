from django.conf                import settings
from django.contrib.auth        import login, authenticate
from django.contrib.auth.forms  import UserCreationForm
from django.shortcuts           import render, redirect, render_to_response
from django.template            import RequestContext
from forms                      import SignUpForm
from progress.views             import ProgressTracker

def index(request):
    context = {}
    card1 = {
        'disabled': False, 
        'title': 'Deklination', 
        'text': 'Practice case declension. Identify the correct case and apply the correct endings to nouns, pronouns, articles, and adjectives.', 
        'button_id': 'begin_deklination',
        'icon': 'chevron-right',
        'url': 'deklination:index'
        }
    card2 = {
        'disabled': True,  
        'title': 'Konjugation',  
        'text': 'Practice verb conjugation. Identify the correct tense and apply the correct form of the verb.',
        'button_id': 'begin_konjugation',
        'icon': 'chevron-right',
        'url': 'index'
        }
    card3 = {
        'disabled': True,  
        'title': 'Wortstellung', 
        'text': 'Practice sentence word order. Identify clauses and apply the correct word order.',
        'button_id': 'begin_wortstellung',
        'icon': 'chevron-right',
        'url': 'index'
        }
    if request.user.is_authenticated():
        progress = ProgressTracker()
        context['next_review'] = progress.get_next_review(request.user)
        context['dek_reviews'] = progress.get_review_count(request.user, 'DG')
        card1['reviews_due'] = progress.get_review_count(request.user, 'DG')
    context['card_deck'] = [card1, card2, card3]
    return render(request, 'index.html', context)

def signup(request):
    if request.method == 'POST':
        #form = UserCreationForm(request.POST)
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        #form = UserCreationForm()
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form, 'page_subtitle': 'Sign Up - '})

def error_400(request):
    response = render(request, '400.html', {})
    response.status_code = 400
    return response

def error_403(request):
    response = render(request, '403.html', {})
    response.status_code = 403
    return response

def error_404(request):
    response = render(request, '404.html', {})
    response.status_code = 404
    return response

def error_500(request):
    response = render(request, '500.html', {})
    response.status_code = 500
    return response

