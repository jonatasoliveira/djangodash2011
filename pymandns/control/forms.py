# -*- coding: utf-8 -*-

from django import forms

class DomainForm(forms.Form):
    domain = forms.CharField(label=u'Domain name', max_length=200)
    domain_active = forms.BooleanField(label=u'Domain active?', initial=True, required=False)
    soa_ttl = forms.IntegerField(label=u'TTL')
    soa_serial = forms.IntegerField(label=u'Serial')
    soa_refresh = forms.IntegerField(label=u'Refresh time')
    soa_retry = forms.IntegerField(label=u'Retry time')
    soa_expire = forms.IntegerField(label=u'Expire time')
    soa_minimum = forms.IntegerField(label=u'Minimum time')

