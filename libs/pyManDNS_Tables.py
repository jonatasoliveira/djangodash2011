from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey

class pyManDNS_Tables(object):

    metadata = MetaData()

    def __init__(self,engine):
        self.engine = engine

    def groups_table(self):
    
        return Table('groups', self.metadata,
            Column('group_id', Integer, primary_key=True),
            Column('name', String(128), nullable=False),
            mysql_engine='InnoDB'
        )
    
    def domains_table(self):
    
        return Table('domains', self.metadata,
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
            mysql_engine='InnoDB',
            extend_existing=True
        )
    
    def records_table(self):
    
        return Table('records', self.metadata,
            Column('record_id', Integer, primary_key=True),
            Column('domain_id', Integer, ForeignKey('domains.domain_id')),
            Column('record_type', String(5), nullable=False),
            Column('record_name', String(64), nullable=False),
            Column('record_value', String(255), nullable=False),
            Column('record_priority', Integer, nullable=True),
            mysql_engine='InnoDB',
            extend_existing=True
        )
    
    def records_default_table(self):
    
        return Table('records_default', self.metadata,
            Column('record_default_id', Integer, primary_key=True),
            Column('record_default_type', String(5), nullable=False),
            Column('record_default_name', String(64), nullable=False),
            Column('record_default_value', String(255), nullable=False),
            Column('record_default_priority', Integer, nullable=True),
            extend_existing=True
        )
    
    def soa_table(self):
    
        return Table('soa', self.metadata,
            Column('soa_ttl', String(10), nullable=False),
            Column('soa_refresh', String(10), nullable=False),
            Column('soa_retry', String(10), nullable=False),
            Column('soa_expire', String(10), nullable=False),
            Column('soa_minimum', String(10), nullable=False),
            extend_existing=True
        )
    
    def queue_table(self):
    
        return Table('queue', self.metadata,
            Column('queue_id', Integer, primary_key=True),
            Column('queue_type', String(10), nullable=False),
            Column('domain', String(64), nullable=False),
            Column('completed', String(1), nullable=False)
        )
    
    def create(self):
    
        self.metadata.create_all(self.engine)
