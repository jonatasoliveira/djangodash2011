import argparse
import xmlrpclib
import socket

def show(msg, prefix='INFO: ', exit=False):
    print '%s%s' % (prefix, msg)
    if exit:
        import sys
        sys.exit()

def show_error(msg, exit=False):
    show(msg, 'ERROR: ', exit)

def show_message(msg, exit=False):
    show(msg, 'MESSAGE: ', exit)

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


class Domain(ConnectXMLRPC):
    def _kwargs_to_args_ordenated(self, **kwargs):
        # The XML-RPC doesn't accept named params. The keys are
        # to ordenate the params and use as **params.
        keys = ['domain', 'domain_active', 'soa_ttl', 'soa_serial',
                'soa_refresh_seconds', 'soa_retry', 'soa_expire',
                'soa_minimum', 'group_id', 'domain_linked_id']
        return [kwargs[k] for k in keys]

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
        @param domain_linked_id
        """
        try:
            params = self._kwargs_to_args_ordenated(**kwargs)
            result = self.client.domain.create(*params)
        except socket.error, msg:
            show_error(msg, exit=True)
        
        if result == True:
            msg = 'SUCCESS! The domain %s was created.' % kwargs['domain']
            show_message(msg, exit=True)
    
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
        @param domain_linked_id
        """
        try:
            params = self._kwargs_to_args_ordenated(**kwargs))
            result = self.client.domain.update(*params)
        except socket.error, msg:
            show_error(msg, exit=True)
    
        if result == True:
            msg = 'SUCCESS! The domain %s was updated.' % kwargs['domain']
            show_message(msg, exit=True)
    
    def delete(self, args):
        print '>>> DELETE: %s' % args


parser = argparse.ArgumentParser()

parser.add_argument('--host', default='localhost', help='Host where XML-RPC Server is running, default "localhost"')
parser.add_argument('--port', default='3333', help='Port of XML-RPC Server, default 3333')

subparsers = parser.add_subparsers(help='commands')

# Domain list parser
domain_list_parser = subparsers.add_parser('domainlist', help='List domains')
domain_list_parser.add_argument('--limit', default=False, help='Limit the output of domains')
domain_list_parser.set_defaults(cls='domain', method='list')

# Domain list parser
domain_create_parser = subparsers.add_parser('domaincreate', help='Create domain')
domain_create_parser.add_argument('domain', help='Domain name')
domain_create_parser.add_argument('--active', dest='domain_active', default=True, help='Active domain?')
domain_create_parser.add_argument('--soa-ttl', dest='soa_ttl', default=None, help='SOA TTL')
domain_create_parser.add_argument('--soa-serial', dest='soa_serial', default=None, help='SOA serial')
domain_create_parser.add_argument('--soa-refresh-time', dest='soa_refresh_seconds', default=None, help='SOA refresh time')
domain_create_parser.add_argument('--soa-retry-time', dest='soa_retry', default=None, help='SOA retry time')
domain_create_parser.add_argument('--soa-expire-time', dest='soa_expire', default=None, help='SOA expire time')
domain_create_parser.add_argument('--soa-minimum-ttl', dest='soa_minimum', default=None, help='SOA minimum TTL')
domain_create_parser.add_argument('--group', dest='group_id', default=None, help='Domain group')
domain_create_parser.add_argument('--linked-to', dest='domain_linked_id', default=None, help='Domain link')
domain_create_parser.set_defaults(cls='domain', method='create')

# Domain update parser
domain_create_parser = subparsers.add_parser('domainupdate', help='Update domain')
domain_create_parser.add_argument('domain', help='Domain name')
domain_create_parser.add_argument('--active', dest='domain_active', default=None, help='Active domain?')
domain_create_parser.add_argument('--soa-ttl', dest='soa_ttl', default=None, help='SOA TTL')
domain_create_parser.add_argument('--soa-serial', dest='soa_serial', default=None, help='SOA serial')
domain_create_parser.add_argument('--soa-refresh-time', dest='soa_refresh_seconds', default=None, help='SOA refresh time')
domain_create_parser.add_argument('--soa-retry-time', dest='soa_retry', default=None, help='SOA retry time')
domain_create_parser.add_argument('--soa-expire-time', dest='soa_expire', default=None, help='SOA expire time')
domain_create_parser.add_argument('--soa-minimum-ttl', dest='soa_minimum', default=None, help='SOA minimum TTL')
domain_create_parser.add_argument('--group', dest='group_id', default=None, help='Domain group')
domain_create_parser.add_argument('--linked-to', dest='domain_linked_id', default=None, help='Domain link')
domain_create_parser.set_defaults(cls='domain', method='update')

# Getting the args.
args = parser.parse_args()
# Removing the configuration args.
kwargs = dict([x for x in args._get_kwargs() if x[0] not in ('cls', 'method', 'host', 'port')])

if args.cls == 'domain':
    domain = Domain(args.host, args.port)
    method = getattr(domain, args.method)
    method(**kwargs)
else:
    print 'ERROR, the args: %s' % args

