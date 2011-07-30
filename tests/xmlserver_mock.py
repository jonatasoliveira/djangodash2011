# -*- coding: utf-8 -*-

from SimpleXMLRPCServer import SimpleXMLRPCServer
from datetime import datetime
import random


def create_random_domain_name():
    letters = 'abcdefghijklmnopqrstuvwxyz'
    return ''.join([random.choice(letters) for _ in range(random.randint(5, 15))])


class Domain(object):
    soa_ttl = 1
    soa_serial = ''
    soa_refresh_seconds = 1000
    soa_retry = 5
    soa_expire = 1000
    soa_minimun = 10
    domain = ''
    domain_active = True
    group_id = None
    domain_linked_id = None

    def __init__(self):
        self.domain = create_random_domain_name()
        self.soa_serial = datetime.now().strftime('%Y%m%d') + '00'

    def serialize(self):
        attrs = ['soa_ttl', 'soa_serial', 'soa_refresh_seconds', 'soa_retry',
                 'soa_expire', 'soa_minimun', 'domain', 'domain_active',
                 'group_id', 'domain_linked_id']
        return dict([(k, self.__getattribute__(k)) for k in attrs])


class DomainDNSConfig:
    domains = [Domain() for _ in range(10)]

    def list(self):
        return self.domains

server = SimpleXMLRPCServer(("localhost", 3333))
#server.register_introspection_functions()
server.register_instance(DomainDNSConfig())
server.serve_forever()

