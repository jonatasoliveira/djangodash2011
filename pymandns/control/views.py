# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib import messages

from pyManDNS_Cli import *
from forms import *
from models import *
import settings


def dashboard(request):
    return render_to_response('dashboard.html', locals(),
        context_instance=RequestContext(request))


def domain_create(request):
    if request.method == 'POST':
        domain_form = DomainForm(request.POST)
        if domain_form.is_valid():
            #import pdb; pdb.set_trace()

            try:
                domain_client = pyManDNS_Cli_Domain(
                    settings.MANAGER_HOST, settings.MANAGER_PORT)
                result = domain_client.create(**domain_form.cleaned_data)

                messages.success(request,
                    'The domain %s was created.' % domain_form.cleaned_data['domain'])
                return redirect('dashboard')
            except Exception, e:
                messages.error(request, u'>>> ERROR: %s' % e)
    else:
        domain_form = DomainForm()

    return render_to_response('domain_create.html', locals(),
        context_instance=RequestContext(request))


