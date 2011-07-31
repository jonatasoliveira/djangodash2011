from django.conf.urls.defaults import *

urlpatterns = patterns('control.views',
    # Example:
    url(r'^$', 'dashboard', name='dashboard'),
    url(r'^domain/create/?$', 'domain_create', name='domain_create'),
    url(r'^domain/list/?$', 'domain_list', name='domain_list'),
    url(r'^domain/edit/(?P<domain_name>.+)/?$', 'domain_edit', name='domain_edit'),
)
