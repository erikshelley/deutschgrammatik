from django.conf.urls   import url
from jchart.views       import ChartView
from .                  import views

app_name = 'progress'
urlpatterns = [
    url(r'reviewed/$', views.reviewed, name='reviewed'),
    url(r'learned/$', views.learned, name='learned'),
    #url(r'charts/review_chart/(?P<username>\w+)/$', ChartView.from_chart(views.review_chart), name='review_chart'),
    #url(r'charts/learned_chart/(?P<username>\w+)/$', ChartView.from_chart(views.learned_chart), name='learned_chart'),
    url(r'charts/review_chart/(?P<username>\w+)/(?P<delta>\w+)/$', ChartView.from_chart(views.review_chart), name='review_chart'),
    url(r'charts/learned_chart/(?P<username>\w+)/(?P<delta>\w+)/$', ChartView.from_chart(views.learned_chart), name='learned_chart'),
    url(r'', views.index, name='index'),
    ]

