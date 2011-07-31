#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import xmlrpclib
import socket
import sys
sys.path.append('./libs')
from pyManDNS_Cli import *

def show(msg, prefix='INFO: ', exit=False):
    print '%s%s' % (prefix, msg)
    if exit:
        import sys
        sys.exit()

def show_error(msg, exit=False):
    show(msg, 'ERROR: ', exit)

def show_message(msg, exit=False):
    show(msg, 'MESSAGE: ', exit)

parser = argparse.ArgumentParser()

parser.add_argument('--host', default='localhost', help='Host where XML-RPC Server is running, default "localhost"')
parser.add_argument('--port', default='3333', help='Port of XML-RPC Server, default 3333')

subparsers = parser.add_subparsers(help='commands')

# Domain show db file
domain_show_parser = subparsers.add_parser('domainshow', help='Show db file')
domain_show_parser.add_argument('domain', help='Domain name')
domain_show_parser.set_defaults(cls='domain', method='show')

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
domain_create_parser.add_argument('--linked-to', dest='domain_linked', default=None, help='Domain link')
domain_create_parser.add_argument('--copy-from', dest='domain_copy', default=None, help='Domain copy')
domain_create_parser.set_defaults(cls='domain', method='create')

# Domain update parser
domain_update_parser = subparsers.add_parser('domainupdate', help='Update domain')
domain_update_parser.add_argument('domain', help='Domain name')
domain_update_parser.add_argument('--active', dest='domain_active', default=None, help='Active domain?')
domain_update_parser.add_argument('--soa-ttl', dest='soa_ttl', default=None, help='SOA TTL')
domain_update_parser.add_argument('--soa-serial', dest='soa_serial', default=None, help='SOA serial')
domain_update_parser.add_argument('--soa-refresh-time', dest='soa_refresh_seconds', default=None, help='SOA refresh time')
domain_update_parser.add_argument('--soa-retry-time', dest='soa_retry', default=None, help='SOA retry time')
domain_update_parser.add_argument('--soa-expire-time', dest='soa_expire', default=None, help='SOA expire time')
domain_update_parser.add_argument('--soa-minimum-ttl', dest='soa_minimum', default=None, help='SOA minimum TTL')
domain_update_parser.add_argument('--group', dest='group_id', default=None, help='Domain group')
domain_update_parser.add_argument('--linked-to', dest='domain_linked', default=None, help='Domain link')
domain_update_parser.set_defaults(cls='domain', method='update')

# Domain delete parser
domain_delete_parser = subparsers.add_parser('domaindelete', help='Delete domain')
domain_delete_parser.add_argument('domain', help='Domain name')
domain_delete_parser.set_defaults(cls='domain', method='delete')

# Getting the args.
args = parser.parse_args()
# Removing the configuration args.
kwargs = dict([x for x in args._get_kwargs() if x[0] not in ('cls', 'method', 'host', 'port')])

if args.cls == 'domain':
    domain = pyManDNS_Cli_Domain(args.host, args.port)
    method = getattr(domain, args.method)
    method(**kwargs)
else:
    print 'ERROR, the args: %s' % args
