import ConfigParser
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey
from easyzone.zone_check import ZoneCheck

config = ConfigParser.ConfigParser()
config.read('./config.cfg');

db_engine = config.get('Database','db.engine')
db_user = config.get('Database','db.user')
db_pass = config.get('Database','db.pass')
db_host = config.get('Database','db.host')
db_name = config.get('Database','db.name')

engine = create_engine('%s://%s:%s@%s/%s?charset=utf8&use_unicode=0' % (db_engine,db_user,db_pass,db_host,db_name), pool_recycle=3600, echo=False)

metadata = MetaData()

# 
# Schema: http://schemabank.com/a/p9VxZ
#

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

#
# Required: http://www.dnspython.org/
# Required: http://pypi.python.org/pypi/easyzone/
#

dir_zone = config.get('Bind','dir.zone')

domains_result = engine.execute(domains_table.select())

zones = "";

for domain_row in domains_result:

    zone_type_NS = ""
    zone_type_MX = ""
    zone_type_A = ""
    zone_type_CNAME = ""
    zone_type_TXT = ""

    zone  = ";\n";
    zone += "; BIND data file for " + domain_row.domain + "\n"
    zone += ";\n"
    zone += "$TTL\t" + domain_row.soa_ttl + "\n"
    zone += "@\tIN\tSOA\t\tns1." + domain_row.domain + ". hostmaster." + domain_row.domain + ". (\n"
    zone += "\t\t\t\t\t" + domain_row.soa_serial + " ; Serial in YYYYMMDDXX (XX is increment)\n"
    zone += "\t\t\t\t\t" + domain_row.soa_refresh + " ; Refresh\n"
    zone += "\t\t\t\t\t" + domain_row.soa_retry + " ; Retry\n"
    zone += "\t\t\t\t\t" + domain_row.soa_expire + " ; Expire\n"
    zone += "\t\t\t\t\t" + domain_row.soa_minimum + ") ; Minimum\n"
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

    zones += "zone \"" + domain_row.domain + "\" {\n"
    zones += "\ttype master;\n"
    zones += "\tfile \"" + dir_zone + "/db." + domain_row.domain + "\";\n"
    zones += "};\n\n"

    print zone

file = open("/var/named/chroot/etc/named.pyManDNS.zones", "w")
file.write(zones);
file.close()
