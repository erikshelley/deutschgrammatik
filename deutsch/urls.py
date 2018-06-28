from django.conf.urls import url, include, handler404, handler500, handler403, handler400
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^admin/',              admin.site.urls),
    url(r'^accounts/',           include('django.contrib.auth.urls')),
    url(r'^accounts/profile/$',  views.change_profile,  name='change_profile'),
    url(r'^accounts/password/$', views.change_password, name='change_password'),
    url(r'^accounts/signup/$',   views.signup, name='signup'),
    url(r'^deklination/',        include('deklination.urls', namespace='deklination', app_name='deklination')),
    url(r'^progress/',           include('progress.urls',    namespace='progress',    app_name='progress')),
    url(r'^$',                   views.index,  name='index'),
    ]

handler400 = views.error_400
handler403 = views.error_403
handler404 = views.error_404
handler500 = views.error_500
