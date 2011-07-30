#
# pyManDNS is a very easy script to Manage yout DNS
#
import ConfigParser
import os
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql.expression import select
from SimpleXMLRPCServer import SimpleXMLRPCServer

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

metadata = MetaData()

groups_table = Table('groups', metadata,
    Column('group_id', Integer, primary_key=True),
    Column('name', String(128), nullable=False),
    mysql_engine='InnoDB'
)

domains_table = Table('domains', metadata,
    Column('domain_id', Integer, primary_key=True),
    Column('domain_linked_id', Integer, ForeignKey('domains.domain_id')),
    Column('group_id', Integer, ForeignKey('groups.group_id')),
    Column('domain', String(64), nullable=False),
    Column('domain_active', String(1), nullable=False),
    Column('soa_ttl', String(10), nullable=True),
    Column('soa_serial', String(10), nullable=False),
    Column('soa_refresh', String(10), nullable=True),
    Column('soa_retry', String(10), nullable=True),
    Column('soa_expire', String(10), nullable=True),
    Column('soa_minimum', String(10), nullable=True),
    mysql_engine='InnoDB'
)

records_table = Table('records', metadata,
    Column('record_id', Integer, primary_key=True),
    Column('domain_id', Integer, ForeignKey('domains.domain_id')),
    Column('record_type', String(5), nullable=False),
    Column('record_name', String(64), nullable=False),
    Column('record_value', String(255), nullable=False),
    Column('record_priority', Integer, nullable=True),
    mysql_engine='InnoDB'
)

soa_table = Table('soa', metadata,
    Column('soa_ttl', String(10), nullable=False),
    Column('soa_refresh', String(10), nullable=False),
    Column('soa_retry', String(10), nullable=False),
    Column('soa_expire', String(10), nullable=False),
    Column('soa_minimum', String(10), nullable=False)
)

queue_table = Table('queue', metadata,
    Column('queue_id', Integer, primary_key=True),
    Column('queue_type', String(10), nullable=False),
    Column('domain', String(64), nullable=False),
    Column('completed', String(1), nullable=False)
)

metadata.create_all(engine)

dir_zone = config.get('Bind','dir.zone')

soa_result = engine.execute(soa_table.select())
soa_row = soa_result.first();

domains_result = engine.execute(domains_table.select())

zones = "";

for domain_row in domains_result:

    zone_type_NS = ""
    zone_type_MX = ""
    zone_type_A = ""
    zone_type_CNAME = ""
    zone_type_TXT = ""

    soa_ttl = soa_row.soa_ttl
    soa_refresh = soa_row.soa_refresh
    soa_retry = soa_row.soa_retry
    soa_expire = soa_row.soa_expire
    soa_minimum = soa_row.soa_minimum

    if domain_row.soa_ttl:
        soa_ttl = domain_row.soa_ttl

    if domain_row.soa_refresh:
        soa_refresh = domain_row.soa_refresh

    if domain_row.soa_retry:
        soa_retry = domain_row.soa_retry

    if domain_row.soa_expire:
        soa_expire = domain_row.soa_expire

    if domain_row.soa_minimum:
        soa_minimum = domain_row.soa_minimum

    zone  = ";\n";
    zone += "; BIND data file for " + domain_row.domain + "\n"
    zone += ";\n"
    zone += "$TTL\t" + soa_ttl + "\n"
    zone += "@\tIN\tSOA\t\tns1." + domain_row.domain + ". hostmaster." + domain_row.domain + ". (\n"
    zone += "\t\t\t\t\t" + domain_row.soa_serial + " ; Serial in YYYYMMDDXX (XX is increment)\n"
    zone += "\t\t\t\t\t" + soa_refresh + " ; Refresh\n"
    zone += "\t\t\t\t\t" + soa_retry + " ; Retry\n"
    zone += "\t\t\t\t\t" + soa_expire + " ; Expire\n"
    zone += "\t\t\t\t\t" + soa_minimum + ") ; Minimum\n"
    zone += ";\n"

    records_result = engine.execute(records_table.select().where("domain_id=:domain_id").order_by("record_type,record_name"),domain_id=domain_row.domain_id)

    for record_row in records_result:

        if record_row.record_type == "NS":
            zone_type_NS += "%s\tIN\tNS\t\t%s.\n" % (record_row.record_name,record_row.record_value)

        if record_row.record_type == "MX":
            zone_type_MX += "%s\tIN\tMX\t%s\t%s.\n" % (record_row.record_name,str(record_row.record_priority),record_row.record_value)

        if record_row.record_type == "A":
            zone_type_A += "%s\tIN\tA\t\t%s\n" % (record_row.record_name,record_row.record_value)

        if record_row.record_type == "CNAME":
            zone_type_CNAME += "%s\tIN\tCNAME\t\t%s\n" % (record_row.record_name,record_row.record_value)

        if record_row.record_type == "TXT":

            record_name = record_row.record_name;

            if record_name == "":
                record_name = "@"
            
            zone_type_CNAME += "%s\tIN\tTXT\t\t\"%s\"\n" % (record_name,record_row.record_value)

    zone += zone_type_NS
    zone += zone_type_MX
    zone += zone_type_A
    zone += zone_type_CNAME
    zone += zone_type_TXT

    file = open(dir_zone + "/db." + domain_row.domain, "w")
    file.write(zone)
    file.close()

    cmd = "/usr/sbin/named-checkzone -q " + domain_row.domain + " " + dir_zone + "/db." + domain_row.domain
    result = os.system(cmd)

    if result != 0:

        print "Bad domain " + domain_row.domain

    else:
        zones += "zone \"" + domain_row.domain + "\" {\n"
        zones += "\ttype master;\n"
        zones += "\tfile \"" + dir_zone + "/db." + domain_row.domain + "\";\n"
        zones += "};\n\n"

file = open("/var/named/chroot/etc/named.pyManDNS.zones", "w")
file.write(zones);
file.close()

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

        engine.execute(domains_table.insert().values(
            domain_linked_id=v_domain_linked_id,
            group_id=v_group_id,
            domain=v_domain,
            domain_active=v_domain_active,
            soa_ttl=v_soa_ttl,
            soa_serial=v_soa_serial,
            soa_retry=v_soa_retry,
            soa_expire=v_soa_expire,
            soa_minimum=v_soa_minimum
        ))

        print 'def'

        return 'def'

class ServerDNSConfig:
    """
    Encasulate the main entities to the XML-RPC server.
    """
    domain = DomainWrapper()

server_host = config.get('Server','server.host')
server_port = config.get('Server','server.port')

server = SimpleXMLRPCServer((server_host, int(server_port)), allow_none=True)
server.register_instance(ServerDNSConfig(), True)
server.serve_forever()
