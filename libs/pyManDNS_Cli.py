import xmlrpclib
import socket

class ConnectXMLRPC(object):

    def __init__(self, host=None, port=None):
        self.host = host if host else HOST
        self.port = port if port else PORT
        self._connect()

    def _connect(self):
        try:
            self.client = xmlrpclib.ServerProxy('http://%s:%s' % (self.host, self.port), allow_none=True)
        except Exception, msg:
            show_error(msg, exit=True)

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
            print result
        except socket.error, msg:
            show_error(msg, exit=True)

    def delete(self, **kwargs):
        """
        Delete domain

        @param domain
        """

        try:
            result = self.client.domain.delete(kwargs["domain"])
            print result
        except socket.error, msg:
            show_error(msg, exit=True)


    def list(self, limit=False):
        """
        List all domains,
        """
        try:
            domains = self.client.domain.list()
        except socket.error, msg:
            show_error(msg, exit=True)

        if limit:
            domains = domains[:limit]

        print 'Domain list (total: %d)' % len(domains)
        for domain in domains:
            print '- %s' % domain['domain']


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
            print result
        except socket.error, msg:
            show_error(msg, exit=True)

        #if result == True:
        #    msg = 'SUCCESS! The domain %s was created.' % kwargs['domain']
        #    show_message(msg, exit=True)

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
            print result
        except socket.error, msg:
            show_error(msg, exit=True)
