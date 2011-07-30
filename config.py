#
# pyManDNS is a very easy script to Manage yout DNS
#
import sys
sys.path.append('./libs');
import ConfigParser
import os
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql.expression import select
from SimpleXMLRPCServer import SimpleXMLRPCServer
import pyManDNS_Tables
import pyManDNS_Zones

# Parse config file
config = ConfigParser.ConfigParser()
config.read('./config.cfg');

# Database connection
db_engine = config.get('Database','db.engine')
db_user = config.get('Database','db.user')
db_pass = config.get('Database','db.pass')
db_host = config.get('Database','db.host')
db_name = config.get('Database','db.name')

engine = create_engine('%s://%s:%s@%s/%s?charset=utf8&use_unicode=0' % (db_engine,db_user,db_pass,db_host,db_name), pool_recycle=3600, echo=False)

#
# Definicoes das tabelas
#

groupts_table = pyManDNS_Tables.groups_table()
domains_table = pyManDNS_Tables.domains_table()
records_table = pyManDNS_Tables.records_table()
records_default_table = pyManDNS_Tables.records_default_table()
soa_table = pyManDNS_Tables.soa_table()
queue_table = pyManDNS_Tables.queue_table()
pyManDNS_Tables.create(engine)

# 
# Geracao de zonas
#

dir_db_files = config.get('Bind','dir.db_files')

domains_result = engine.execute(domains_table.select())

for domain_row in domains_result:
    file = dir_db_files + "/db." + domain_row.domain;
    pyManDNS_Zones.create_db_file(engine,dir_db_files,domain_row.domain)

pyManDNS_Zones.create_zone_file(engine,dir_db_files,1);
pyManDNS_Zones.reload();

# 
# Funcoes do DNS
#
class DomainWrapper(object):
    """
    This class is used to separate the entities namespaces in the XML-RPC server.

    Usage in the server (example):
    >>> import xmlrpclib
    >>> client = xmlrpclib.ServerProxy('http://localhost:3000')
    >>> client.domain.list()
    """

    domains = []

    def list(self):
        domains_result = engine.execute(domains_table.select())

        for domain_row in domains_result:
            self.domains.append({ 'domain_id': domain_row.domain_id, 'domain': domain_row.domain }) 

        return self.domains

    def create(self, v_domain, v_domain_active=True, v_soa_ttl=None, v_soa_serial=None,
               v_soa_refresh=None, v_soa_retry=None, v_soa_expire=None,
               v_soa_minimum=None, v_group_id=None, v_domain_linked_id=None):

        insert = engine.execute(domains_table.insert().values(
            domain_linked_id=v_domain_linked_id,
            group_id=v_group_id,
            domain=v_domain,
            domain_active=v_domain_active,
            soa_ttl=v_soa_ttl,
            soa_serial=v_soa_serial,
            soa_refresh=v_soa_refresh,
            soa_retry=v_soa_retry,
            soa_expire=v_soa_expire,
            soa_minimum=v_soa_minimum
        ))

        last_insert_id = insert.inserted_primary_key

        records_default_result = engine.execute(records_default_table.select())

        for record_default_row in records_default_result:
            record_default_value = record_default_row.record_default_value;
            record_default_value = record_default_value.replace("DOMAIN",v_domain)

            engine.execute(records_table.insert().values(
                domain_id=last_insert_id[0],
                record_type=record_default_row.record_default_type,
                record_name=record_default_row.record_default_name,
                record_value=record_default_value,
                record_priority=record_default_row.record_default_priority
            ))

teste = DomainWrapper()
lista = teste.list()

#print lista

for i in lista:
   print i['domain']

#teste.create('teste.com.br',1,150,'111',2501,111,1111,1111,None,1)

#class ServerDNSConfig:
#    """
#    Encasulate the main entities to the XML-RPC server.
#    """
#    domain = DomainWrapper()
#
#server_host = config.get('Server','server.host')
#server_port = config.get('Server','server.port')
#
#server = SimpleXMLRPCServer((server_host, int(server_port)), allow_none=True)
#server.register_instance(ServerDNSConfig(), True)
#server.serve_forever()
