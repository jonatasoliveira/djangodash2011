from django.conf.urls.defaults import *

urlpatterns = patterns('control.views',
    # Example:
    url(r'^$', 'index', name='index'),
    url(r'^domain/create/?$', 'domain_create', name='domain_create'),
    url(r'^domain/list/?$', 'domain_list', name='domain_list'),
    url(r'^domain/edit/(?P<domain_name>.+)/?$', 'domain_edit', name='domain_edit'),
    url(r'^domain/delete/(?P<domain_name>.+)/?$', 'domain_delete', name='domain_delete'),
)
