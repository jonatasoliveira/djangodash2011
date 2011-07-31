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


def index(request):
    return redirect('domain_list')


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
                    return redirect('domain_list')
                elif result['type'] == 'error':
                    messages.error(request, result['message'])

            except Exception, e:
                messages.error(request, u'>>> ERROR: %s' % e)
    else:
        domain_form = DomainForm()

    return render_to_response('domain_create.html', locals(),
        context_instance=RequestContext(request))


def domain_edit(request, domain_name):
    try:
        domain_client = _get_client()
        result = domain_client.get(domain_name)
        domain = result['result']

        result_zone = domain_client.show(domain=domain_name)
        zone = result_zone["message"]

    except Exception, e:
        messages.error(request, u'>>> ERROR: %s' % e)

    if request.method == 'POST':
        domain_form = DomainForm(request.POST)
        if domain_form.is_valid():
            try:
                result = domain_client.update(**domain_form.cleaned_data)

                if result['type'] == 'success':
                    messages.success(request,
                        u'The domain %s was updated.' % domain_form.cleaned_data['domain'])
                    return redirect('domain_list')
                elif result['type'] == 'error':
                    messages.error(request, result['message'])

            except Exception, e:
                messages.error(request, u'>>> ERROR: %s' % e)
    else:
        domain_form = DomainForm(initial=domain)

    return render_to_response('domain_edit.html', locals(),
        context_instance=RequestContext(request))


def domain_delete(request, domain_name):
    if request.method == 'POST':
        try:
            domain_client = _get_client()
            result = domain_client.delete(domain=domain_name)
            if result['type'] == 'success':
                messages.success(request, 'The domain %s was deleted.' % domain_name)
                return redirect('domain_list')
            elif result['type'] == 'error':
                messages.error(request, result['message'])
        except Exception, e:
            messages.error(request, u'>>> ERROR: %s' % e)


    return render_to_response('domain_delete.html', locals(),
        context_instance=RequestContext(request))
