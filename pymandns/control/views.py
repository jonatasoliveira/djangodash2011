# Create your views here.
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib import messages

from forms import *
from models import *

def dashboard(request):
    return render_to_response('dashboard.html', locals(),
        context_instance=RequestContext(request))

def domain_create(request):

    if request.method == 'POST':
        domain_form = DomainForm(request.POST)
        if domain_form.is_valid():
            #import pdb; pdb.set_trace()
            messages.success(request, u'The domains %s was created.' % domain_form.cleaned_data['domain'])
            return redirect('dashboard')
        pass
    else:
        domain_form = DomainForm()

    return render_to_response('domain_create.html', locals(),
        context_instance=RequestContext(request))

