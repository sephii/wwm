from django.conf.urls import patterns, include, url
from django.contrib import admin
import socketio.sdjango

admin.autodiscover()
socketio.sdjango.autodiscover()

urlpatterns = patterns(
    '',
    url("^socket\.io", include(socketio.sdjango.urls)),
    url(r'^$', 'apps.quizz.views.home', name='home'),
    url(r'^games/new/$', 'apps.quizz.views.game_create', name='game_create'),
    #url(r'^games/(?P<id>\d+)/$', 'apps.quizz.views.game_detail',
    #    name='game_detail'),
    # url(r'^wwm/', include('wwm.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
