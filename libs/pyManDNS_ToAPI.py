import re


def success(msg=None, result=None):
    return dict(type='success', message=msg, result=result)

def error(msg=None, result=None):
    return dict(type='error', message=msg, result=result)


class DomainWrapper(object):
    """
    This class is used to separate the entities namespaces in the XML-RPC server.

    Usage in the server (example):
    >>> import xmlrpclib
    >>> client = xmlrpclib.ServerProxy('http://localhost:3000')
    >>> client.domain.list()
    """

    def __init__(self,engine,pyTables,pyZones):
        self.engine = engine
        self.pyTables = pyTables
        self.pyZones = pyZones

    ''' Visualiza db file '''
    def show(self,v_domain):

        msg = self.pyZones.read_db_file(v_domain)
        
        return success(msg=msg)

    ''' Get dominio '''
    def get(self,v_domain):

        domains_table = self.pyTables.domains_table()
        records_table = self.pyTables.records_table()

        domains_result = self.engine.execute(
            domains_table.select().where("domain=:domain"),domain=v_domain)
        domain_row = domains_result.first()

        if domain_row:
            # return domain_row
            return success(result=domain_row)
        else:
            msg = "ERROR: Dominio not found"
            return error(msg=msg)

    ''' Delete dominio '''
    def delete(self,v_domain):

        domains_table = self.pyTables.domains_table()
        records_table = self.pyTables.records_table()

        domains_result = self.engine.execute(
            domains_table.select("domain_id").where("domain=:domain"),domain=v_domain)
        domain_row = domains_result.first()

        if domain_row:
            msg = "SUCCESS: Dominio removido"

            domains_delete_result = self.engine.execute(
                domains_table.select("domain_id").where("domain_linked_id=:domain_id"),domain_id=domain_row.domain_id)
            
            for domain_delete_row in domains_delete_result:
                self.engine.execute(records_table.delete("domain_id=:domain_id"),domain_id=domain_delete_row.domain_id)
                self.engine.execute(domains_table.delete("domain_id=:domain_id"),domain_id=domain_delete_row.domain_id)

            self.engine.execute(records_table.delete("domain_id=:domain_id"),domain_id=domain_row.domain_id)
            self.engine.execute(domains_table.delete("domain_id=:domain_id"),domain_id=domain_row.domain_id)

            self.pyZones.create_zone_file(1)
            self.pyZones.reload()

            return success(msg=msg)

        else:
            msg = "ERROR: Dominio not found"
            return error(msg=msg)

    ''' Lista dominios '''
    def list(self):
        domains_table = self.pyTables.domains_table()

        domains = []

        domains_result = self.engine.execute(domains_table.select())

        for domain_row in domains_result:
            domains.append({ 'domain_id': domain_row.domain_id, 'domain': domain_row.domain })

        return success(result=domains)

    ''' Grava dominios '''
    def create(self, v_domain, v_domain_active=True, v_soa_ttl=None, v_soa_serial=None,
               v_soa_refresh=None, v_soa_retry=None, v_soa_expire=None,
               v_soa_minimum=None, v_group_id=None, v_domain_linked=None, v_domain_copy=None):

        ''' Dados padrao '''
        if not v_soa_serial:
            v_soa_serial = 1

        ''' Instancia tabelas '''
        domains_table = self.pyTables.domains_table()
        records_table = self.pyTables.records_table()
        records_default_table = self.pyTables.records_default_table()

        ''' Nao pode ser feito link e copia ao mesmo tempo '''
        if v_domain_linked and v_domain_copy:
            msg = "ERROR: Nao pode ser feito link e copia ao mesmo tempo"
            return error(msg=msg)

        ''' Verifica se dominio ja existe '''
        domains_result = self.engine.execute(
            domains_table.select("domain_id").where("domain=:domain"),domain=v_domain)
        domain_row = domains_result.first()

        if domain_row:
            msg = "ERROR: Dominio ja existe..."
            return error(msg=msg)

        ''' Tratamento de v_domain_copy '''
        v_domain_copy_id = None;

        if v_domain_copy:

            domains_copy_result = self.engine.execute(
                domains_table.select("domain_id").where("domain=:domain"),domain=v_domain_copy)
            domain_copy_row = domains_copy_result.first()

            if domain_copy_row:
                v_domain_copy_id = domain_copy_row.domain_id;
            else:
                msg = "ERROR: Dominio origem para copia not found..."
                return error(msg=msg)

        ''' Tratamento de v_domain_linked '''
        v_domain_linked_id = None;

        if v_domain_linked:

            domains_linked_result = self.engine.execute(
                domains_table.select("domain_id").where("domain=:domain"),domain=v_domain_linked)
            domain_linked_row = domains_linked_result.first()

            if domain_linked_row:
                v_domain_linked_id = domain_linked_row.domain_id;
            else:
                msg = "Dominio origem para link not found..."
                return error(msg=msg)

        ''' Adiciona dominio '''
        insert = self.engine.execute(domains_table.insert().values(
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

        ''' Recupera ultimo ID adicionado '''
        last_insert_id = insert.lastrowid

        if v_domain_copy_id:
            ''' Verifica se deve ser feito copia '''

            records_result = self.engine.execute(
                records_table.select().where("domain_id=:domain_id"),domain_id=v_domain_copy_id)

            for record_row in records_result:
                record_value = record_row.record_value;
                record_value = re.sub(r'^' + v_domain_copy, v_domain, record_value, re.IGNORECASE)
                record_value = re.sub(r'\.' + v_domain_copy, '.' + v_domain, record_value, re.IGNORECASE)

                ''' Grava registros recuperados '''
                self.engine.execute(records_table.insert().values(
                    domain_id=last_insert_id,
                    record_type=record_row.record_type,
                    record_name=record_row.record_name,
                    record_value=record_value,
                    record_priority=record_row.record_priority
                ))

        else:
            ''' Recupera registros padrao '''
            records_default_result = self.engine.execute(records_default_table.select())

            for record_default_row in records_default_result:
                record_default_value = record_default_row.record_default_value;
                record_default_value = record_default_value.replace("DOMAIN",v_domain)

                ''' Grava registros recuperados '''
                self.engine.execute(records_table.insert().values(
                    domain_id=last_insert_id,
                    record_type=record_default_row.record_default_type,
                    record_name=record_default_row.record_default_name,
                    record_value=record_default_value,
                    record_priority=record_default_row.record_default_priority
                ))

        self.pyZones.create_db_file(v_domain)
        self.pyZones.create_zone_file(1)
        self.pyZones.reload()

        msg  = "SUCCESS: Dominio " + v_domain + " adicionado.\n\n"
        msg += self.pyZones.read_db_file(v_domain)
        
        return success(msg=msg)

    ''' Atualiza dominio '''
    def update(self, v_domain, v_domain_active=True, v_soa_ttl=None, v_soa_serial=None,
               v_soa_refresh=None, v_soa_retry=None, v_soa_expire=None,
               v_soa_minimum=None, v_group_id=None, v_domain_linked=None):

        ''' Instancia tabelas '''
        domains_table = self.pyTables.domains_table()
        records_table = self.pyTables.records_table()
        records_default_table = self.pyTables.records_default_table()

        ''' Verifica se dominio ja existe '''
        domains_result = self.engine.execute(
            domains_table.select().where("domain=:domain"),domain=v_domain)
        domain_row = domains_result.first()

        if domain_row == "":
            msg = "ERROR: Dominio nao existe..."
            return error(msg=msg)

        ''' Tratamento de v_domain_linked '''
        v_domain_linked_id = None;

        if v_domain_linked:

            domains_linked_result = self.engine.execute(
                domains_table.select("domain_id").where("domain=:domain"),domain=v_domain_linked)
            domain_linked_row = domains_linked_result.first()

            if domain_linked_row:
                v_domain_linked_id = domain_linked_row.domain_id;
            else:
                msg = "Dominio origem para link not found..."
                return error(msg=msg)

        ''' Adiciona dominio '''
        insert = self.engine.execute(domains_table.update().values(
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
        ).where("domain_id=:b_domain_id"),b_domain_id=domain_row.domain_id)

        return success(msg='ok')

#        ''' Recupera ultimo ID adicionado '''
#        last_insert_id = insert.lastrowid
#
#        if v_domain_copy_id:
#            ''' Verifica se deve ser feito copia '''
#
#            records_result = self.engine.execute(
#                records_table.select().where("domain_id=:domain_id"),domain_id=v_domain_copy_id)
#
#            for record_row in records_result:
#                record_value = record_row.record_value;
#                record_value = re.sub(r'^' + v_domain_copy, v_domain, record_value, re.IGNORECASE)
#                record_value = re.sub(r'\.' + v_domain_copy, '.' + v_domain, record_value, re.IGNORECASE)
#
#                ''' Grava registros recuperados '''
#                self.engine.execute(records_table.insert().values(
#                    domain_id=last_insert_id,
#                    record_type=record_row.record_type,
#                    record_name=record_row.record_name,
#                    record_value=record_value,
#                    record_priority=record_row.record_priority
#                ))
#
#        else:
#            ''' Recupera registros padrao '''
#            records_default_result = self.engine.execute(records_default_table.select())
#
#            for record_default_row in records_default_result:
#                record_default_value = record_default_row.record_default_value;
#                record_default_value = record_default_value.replace("DOMAIN",v_domain)
#
#                ''' Grava registros recuperados '''
#                self.engine.execute(records_table.insert().values(
#                    domain_id=last_insert_id,
#                    record_type=record_default_row.record_default_type,
#                    record_name=record_default_row.record_default_name,
#                    record_value=record_default_value,
#                    record_priority=record_default_row.record_default_priority
#                ))
#
#        self.pyZones.create_db_file(v_domain)
#        self.pyZones.create_zone_file(1)
#        self.pyZones.reload()
#
#        msg  = "SUCCESS: Dominio " + v_domain + " adicionado.\n\n"
#        msg += self.pyZones.read_db_file(v_domain)
#        
#        return msg


class pyManDNS_ToAPI(object):

    def __init__(self,engine,pyTables,pyZones):
        self.engine = engine
        self.pyTables = pyTables
        self.pyZones = pyZones

    def startDomainWrapper(self):
        self.domain = DomainWrapper(self.engine,self.pyTables,self.pyZones)


