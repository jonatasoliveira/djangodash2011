from django.conf.urls.defaults import *

urlpatterns = patterns('control.views',
    # Example:
    url(r'^$', 'dashboard', name='dashboard'),
    url(r'^domain/create/?$', 'domain_create', name='domain_create'),
    url(r'^domain/list/?$', 'domain_list', name='domain_list'),
)