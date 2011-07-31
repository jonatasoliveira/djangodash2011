import xmlrpclib
import socket

def success(msg=None, result=None):
    return dict(type='success', message=msg, result=result)

def error(msg=None, result=None):
    return dict(type='error', message=msg, result=result)

class ConnectXMLRPC(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._connect()

    def _connect(self):
        try:
            self.client = xmlrpclib.ServerProxy('http://%s:%s' % (self.host, self.port), allow_none=True)
        except Exception, msg:
            return dict(type='error', message=msg)

class DomainSlaveWrapper(ConnectXMLRPC):
    """
    This class is used to separate the entities namespaces in the XML-RPC server.

    Usage in the server (example):
    >>> import xmlrpclib
    >>> client = xmlrpclib.ServerProxy('http://localhost:3000')
    >>> client.domain.list()
    """

#   def __init__(self,dir_db_files):
#       self.dir_db_files = dir_db_files

    def set_dir_db_file(self,dir_db_file):
        self.dir_db_file = dir_db_file

    def create_zone_file(self,verbose):
        try:
            result = self.client.domain.list()

            zones = ""

            for domain_row in result["result"]:

                zones += "zone \"" + domain_row["domain"] + "\" {\n"
                zones += "\ttype slave;\n"
                zones += "\tfile \"" + self.dir_db_file + "/db.slave." + domain_row["domain"] + "\";\n"
                zones += "\tmasters { 192.168.1.204; };\n"
                zones += "};\n\n"

            file = open("/var/named/chroot/etc/named.pyManDNS.slaves.zones", "w")
            file.write(zones);
            file.close()

        except socket.error, msg:
            print 'erro!!'

#    ''' Visualiza db file '''
#    def show(self,v_domain):
#
#        msg = self.pyZones.read_db_file(v_domain)
#        
#        return success(msg=msg)
#
#    ''' Get dominio '''
#    def get(self,v_domain):
#
#        domains_table = self.pyTables.domains_table()
#        records_table = self.pyTables.records_table()
#
#        domains_result = self.engine.execute(
#            domains_table.select().where("domain=:domain"),domain=v_domain)
#        domain_row = domains_result.first()
#
#        if domain_row:
#            # return domain_row
#            return success(result=domain_row)
#        else:
#            msg = "ERROR: Dominio not found"
#            return error(msg=msg)

class pyManDNS_Slave(object):

    def __init__(self,dir_db_files):
        self.dir_db_files = dir_db_files

    def startDomainSlaveWrapper(self,host,port):
        self.domainSlave = DomainSlaveWrapper(host,port)
