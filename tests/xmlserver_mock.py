# -*- coding: utf-8 -*-

from SimpleXMLRPCServer import SimpleXMLRPCServer
from datetime import datetime
import random


def create_random_domain_name():
    letters = 'abcdefghijklmnopqrstuvwxyz'
    domain_ends = '.com .net .com.br .org .org.br .net.br .ws .me'.split()
    return ''.join([random.choice(letters) for _ in range(random.randint(5, 15))]) + random.choice(domain_ends)


class Domain(object):
    """
    Domain Mockup to test the XML-RPC server.
    """
    soa_ttl = 1
    soa_serial = ''
    soa_refresh_seconds = 1000
    soa_retry = 5
    soa_expire = 1000
    soa_minimum = 10
    domain = ''
    domain_active = True
    group_id = None
    domain_linked_id = None

    def __init__(self, domain=None, domain_active=None, soa_ttl=None,
                 soa_serial=None, soa_refresh_seconds=None,
                 soa_retry=None, soa_expire=None, soa_minimum=None,
                 group_id=None, domain_linked_id=None):
        self.domain = domain
        self.domain_active = domain_active
        self.soa_ttl = soa_ttl
        self.soa_serial = soa_serial
        self.soa_refresh_seconds = soa_refresh_seconds
        self.soa_retry = soa_retry
        self.soa_expire = soa_expire
        self.soa_minimum = soa_minimum
        self.group_id = group_id
        self.domain_linked_id = domain_linked_id

    def serialize(self):
        attrs = ['domain', 'domain_active', 'soa_ttl', 'soa_serial',
                 'soa_refresh_seconds', 'soa_retry', 'soa_expire', 'soa_minimum', 
                 'group_id', 'domain_linked_id']
        return dict([(k, self.__getattribute__(k)) for k in attrs])


class DomainWrapper(object):
    """
    This class is used to separate the entities namespaces in the XML-RPC server.

    Usage in the server (example):
    >>> import xmlrpclib
    >>> client = xmlrpclib.ServerProxy('http://localhost:3000')
    >>> client.domain.list()
    """
    domains = [Domain(create_random_domain_name()).serialize() for _ in range(10)]

    def list(self):
        return self.domains

    def create(self, domain, domain_active=True, soa_ttl=None, soa_serial=None,
               soa_refresh_seconds=None, soa_retry=None, soa_expire=None,
               soa_minimum=None, group_id=None, domain_linked_id=None):
        new_domain = Domain(domain, domain_active, soa_ttl, soa_serial,
            soa_refresh_seconds, soa_retry, soa_expire, soa_minimum,
            group_id, domain_linked_id)
        self.domains.append(new_domain)
        return True

    def delete(self, domain):
        for d in self.domains:
            if d['domain'] == domain:
                break
        else:
            return [('message', 'The domain was not founded.'), ('type', 'error')]

        self.domains.remove(d)
        return True


class ServerDNSConfig:
    """
    Encasulate the main entities to the XML-RPC server.
    """
    domain = DomainWrapper()
    # group = GroupWrapper()


server = SimpleXMLRPCServer(("localhost", 3333), allow_none=True)
server.register_instance(ServerDNSConfig(), True)
server.serve_forever()

