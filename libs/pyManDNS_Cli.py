# -*- coding: utf-8 -*-

import xmlrpclib
import socket


class ConnectXMLRPC(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._connect()

    def _connect(self):
        try:
            self.client = xmlrpclib.ServerProxy('http://%s:%s' % (self.host, self.port), allow_none=True)
        except Exception, msg:
            return dict(type='error', message=msg)


class pyManDNS_Cli_Domain(ConnectXMLRPC):
    def _kwargs_to_args_ordenated(self, **kwargs):
        # The XML-RPC doesn't accept named params. The keys are
        # to ordenate the params and use as **params.
        keys = ['domain', 'domain_active', 'soa_ttl', 'soa_serial',
                'soa_refresh_seconds', 'soa_retry', 'soa_expire',
                'soa_minimum', 'group_id', 'domain_linked', 'domain_copy']

        return [kwargs[k] for k in keys if k in kwargs]

    def show(self, **kwargs):
        """
        Show db file

        @param domain
        """

        try:
            result = self.client.domain.show(kwargs["domain"])
            return dict(type='success', message='', result=result)
        except socket.error, msg:
            return dict(type='error', message=msg)

    def delete(self, **kwargs):
        """
        Delete domain

        @param domain
        """

        try:
            result = self.client.domain.delete(kwargs["domain"])
            return dict(type='success', message='', result=result)
        except socket.error, msg:
            return dict(type='error', message=msg)

    def list(self, limit=False):
        """
        List all domains,
        """
        try:
            domains = self.client.domain.list()
        except socket.error, msg:
            return dict(type='error', message=msg)

        if limit:
            domains = domains[:limit]

        return dict(type='success', message='', result=domains)

    def get(self, domain):
        """
        Get one domain, with all details,
        """
        try:
            result = self.client.domain.get(domain=domain)
        except socket.error, msg:
            return dict(type='error', message=msg)

        return dict(type='success', message='', result=domain)

    def create(self, *args, **kwargs):
        """
        Create a new domain.

        @param domain
        @param domain_active
        @param soa_ttl
        @param soa_serial
        @param soa_refresh_seconds
        @param soa_retry
        @param soa_expire
        @param soa_minimum
        @param group_id
        @param domain_linked
        @param domain_copy
        """
        try:
            params = self._kwargs_to_args_ordenated(**kwargs)
            result = self.client.domain.create(*params)
            return dict(type='success', message='', result=result)
        except socket.error, msg:
            return dict(type='error', message=msg)

    def update(self, *args, **kwargs):
        """
        Update a domain.

        @param domain
        @param domain_active
        @param soa_ttl
        @param soa_serial
        @param soa_refresh_seconds
        @param soa_retry
        @param soa_expire
        @param soa_minimum
        @param group_id
        @param domain_linked
        """

        try:
            params = self._kwargs_to_args_ordenated(**kwargs)
            result = self.client.domain.update(*params)
            return dict(type='success', message='', result=result)
        except socket.error, msg:
            return dict(type='error', message=msg)


