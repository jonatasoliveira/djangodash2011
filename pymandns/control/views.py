# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib import messages

from pyManDNS_Cli import *
from forms import *
from models import *
import settings


def _get_client():
    domain_client = pyManDNS_Cli_Domain(settings.MANAGER_HOST, settings.MANAGER_PORT)
    return domain_client


def dashboard(request):
    return render_to_response('dashboard.html', locals(),
        context_instance=RequestContext(request))


def domain_list(request):
    try:
        domain_client = _get_client()
        result = domain_client.list()
        domains = result['result']
    except Exception, e:
        messages.error(request, u'>>> ERROR: %s' % e)

    return render_to_response('domain_list.html', locals(),
        context_instance=RequestContext(request))


def domain_create(request):
    if request.method == 'POST':
        domain_form = DomainForm(request.POST)
        if domain_form.is_valid():
            try:
                domain_client = _get_client()
                result = domain_client.create(**domain_form.cleaned_data)

                if result['type'] == 'success':
                    messages.success(request,
                        u'The domain %s was created.' % domain_form.cleaned_data['domain'])
                    return redirect('dashboard')
                elif result['type'] == 'error':
                    messages.error(request, result['message'])

            except Exception, e:
                messages.error(request, u'>>> ERROR: %s' % e)
    else:
        domain_form = DomainForm()

    return render_to_response('domain_create.html', locals(),
        context_instance=RequestContext(request))


#def domain_edit(request):
#    if request.method == 'POST':
#        domain_form = DomainForm(request.POST)
#        if domain_form.is_valid():
#            try:
#                domain_client = _get_client()
#                result = domain_client.create(**domain_form.cleaned_data)
#
#                if result['type'] == 'success':
#                    messages.success(request,
#                        u'The domain %s was created.' % domain_form.cleaned_data['domain'])
#                    return redirect('dashboard')
#                elif result['type'] == 'error':
#                    messages.error(request, result['message'])
#
#            except Exception, e:
#                messages.error(request, u'>>> ERROR: %s' % e)
#    else:
#        try:
#            domain_client = _get_client()
#            result = domain_client.show(**domain_form.cleaned_data)
#        except Exception, e:
#            messages.error(request, u'>>> ERROR: %s' % e)
#        domain_form = DomainForm(initial=)
#
#    return render_to_response('domain_create.html', locals(),
#        context_instance=RequestContext(request))

