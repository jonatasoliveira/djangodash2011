import ConfigParser
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey

config = ConfigParser.ConfigParser()
config.read('./config.cfg');

db_engine = config.get('Database','db.engine')
db_user = config.get('Database','db.user')
db_pass = config.get('Database','db.pass')
db_host = config.get('Database','db.host')
db_name = config.get('Database','db.name')

engine = create_engine('%s://%s:%s@%s/%s?charset=utf8&use_unicode=0' % (db_engine,db_user,db_pass,db_host,db_name), pool_recycle=3600)

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
    Column('soa_refresh_seconds', String(10), nullable=True),
    Column('soa_retry', String(10), nullable=True),
    Column('soa_expire', String(10), nullable=True),
    Column('soa_minimum', String(10), nullable=True),
    mysql_engine='InnoDB'
)

records_table = Table('records', metadata,
    Column('record_id', Integer, primary_key=True),
    Column('domain_id', Integer, ForeignKey('domains.domain_id')),
    Column('record_type', String(5), nullable=False),
    Column('record_name', String(64), nullable=True),
    Column('record_value', String(255), nullable=False),
    Column('record_priority', Integer, nullable=True),
    mysql_engine='InnoDB'
)

soa_table = Table('soa', metadata,
    Column('soa_ttl', String(10), nullable=False),
    Column('soa_refresh_seconds', String(10), nullable=False),
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
