from django.conf.urls import url
from . import views

app_name = 'deklination'
urlpatterns = [
    #url(r'gender_quiz/', views.GenderQuizView.as_view(), name='gender_quiz'),
    url(r'gender_quiz/', views.gender_quiz, name='gender_quiz'),
    url(r'', views.index, name='index'),
    #url(r'^(?P<question_id>[0-9]+)/$', views.detail, name='detail'),
    #url(r'^(?P<question_id>[0-9]+)/results/$', views.results, name='results'),
    #url(r'^$', views.IndexView.as_view(), name='index'),
    #url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    #url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
    #url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
    ]

