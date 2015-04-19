from django.conf.urls import patterns, url

from workday import views


urlpatterns = patterns('',
	# ex: /linchpin/message
    url(r'^message$', views.message, name='message'),
    # ex: /linchpin/register
    url(r'^register$', views.register, name='register'),
    # ex: /linchpin/login
    url(r'^login$', views.login, name='login'),
    # ex: /linchpin/gcm
    url(r'^gcm$', views.gcm, name='gcm'),
    # ex: /linchpin/contacts
    url(r'^contacts$', views.contacts, name='contacts'),
)