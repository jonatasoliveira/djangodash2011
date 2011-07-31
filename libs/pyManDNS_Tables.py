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

        # Verifica se existe informacao de SOA
        soa_table = self.soa_table()
        soa_result = self.engine.execute(soa_table.select())
        soa_row = soa_result.first()

        if not soa_row:

            self.engine.execute(soa_table.insert().values(
                soa_ttl='14400',
                soa_refresh='10800',
                soa_retry='3600',
                soa_expire='604800',
                soa_minimum='38400'
            ))

        # Verifica se existe registro padrao
        records_default_table = self.records_default_table()
        records_default_result = self.engine.execute(records_default_table.select())
        record_default_row = records_default_result.first()

        if not record_default_row:

            self.engine.execute(records_default_table.insert().values(
                record_default_type='NS',
                record_default_name='',
                record_default_value='ns1.DOMAIN'
            ))

            self.engine.execute(records_default_table.insert().values(
                record_default_type='NS',
                record_default_name='',
                record_default_value='ns2.DOMAIN'
            ))

            self.engine.execute(records_default_table.insert().values(
                record_default_type='A',
                record_default_name='ns1',
                record_default_value='192.168.1.1'
            ))

            self.engine.execute(records_default_table.insert().values(
                record_default_type='A',
                record_default_name='ns2',
                record_default_value='192.168.1.2'
            ))

            self.engine.execute(records_default_table.insert().values(
                record_default_type='A',
                record_default_name='',
                record_default_value='127.0.0.1'
            ))

            self.engine.execute(records_default_table.insert().values(
                record_default_type='CNAME',
                record_default_name='www',
                record_default_value='DOMAIN'
            ))

            self.engine.execute(records_default_table.insert().values(
                record_default_type='CNAME',
                record_default_name='mail',
                record_default_value='ghs.google.com'
            ))

            self.engine.execute(records_default_table.insert().values(
                record_default_type='CNAME',
                record_default_name='docs',
                record_default_value='ghs.google.com'
            ))

            self.engine.execute(records_default_table.insert().values(
                record_default_type='CNAME',
                record_default_name='calendar',
                record_default_value='ghs.google.com'
            ))

            self.engine.execute(records_default_table.insert().values(
                record_default_type='TXT',
                record_default_name='',
                record_default_value='v=spf1 a mx include:aspmx.googlemail.com ~all'
            ))

            self.engine.execute(records_default_table.insert().values(
                record_default_type='MX',
                record_default_name='',
                record_default_value='aspmx.l.google.com',
                record_default_priority='10'
            ))

            self.engine.execute(records_default_table.insert().values(
                record_default_type='MX',
                record_default_name='',
                record_default_value='alt1.aspmx.l.google.com',
                record_default_priority='20'
            ))

            self.engine.execute(records_default_table.insert().values(
                record_default_type='MX',
                record_default_name='',
                record_default_value='alt2.aspmx.l.google.com',
                record_default_priority='20'
            ))

            self.engine.execute(records_default_table.insert().values(
                record_default_type='MX',
                record_default_name='',
                record_default_value='aspmx2.googlemail.com',
                record_default_priority='30'
            ))

            self.engine.execute(records_default_table.insert().values(
                record_default_type='MX',
                record_default_name='',
                record_default_value='aspmx3.googlemail.com',
                record_default_priority='30'
            ))

            self.engine.execute(records_default_table.insert().values(
                record_default_type='MX',
                record_default_name='',
                record_default_value='aspmx4.googlemail.com',
                record_default_priority='30'
            ))

            self.engine.execute(records_default_table.insert().values(
                record_default_type='MX',
                record_default_name='',
                record_default_value='aspmx5.googlemail.com',
                record_default_priority='30'
            ))
