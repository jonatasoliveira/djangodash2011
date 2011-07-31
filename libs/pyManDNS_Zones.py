from pyManDNS_Tables import pyManDNS_Tables
import os

class pyManDNS_Zones(object): 

    def __init__(self,engine,pyTables):
        self.engine = engine
        self.pyTables = pyTables

    def create_db_file(self,dir_db_files,v_domain):
        ''' Cria arquivo DB File '''
    
        # Recupera dados do SOA
        soa_table = self.pyTables.soa_table()
        soa_result = self.engine.execute(soa_table.select())
        soa_row = soa_result.first();
    
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
    
        # Recupera dados do domain
        domains_table = self.pyTables.domains_table()
        domains_result = self.engine.execute(domains_table.select().where("domain=:domain"),domain=v_domain)
        domain_row = domains_result.first()
    
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
    
        records_table = self.pyTables.records_table()
        records_result = self.engine.execute(records_table.select().where("domain_id=:domain_id").order_by("record_type,record_name"),domain_id=domain_row.domain_id)
    
        if domain_row.domain_linked_id:
    
            records_result = self.engine.execute(
                records_table.select().where("domain_id=:domain_id").order_by("record_type,record_name"),domain_id=domain_row.domain_linked_id)
    
        for record_row in records_result:
    
            if record_row.record_type == "NS":
                zone_type_NS += "%s\tIN\tNS\t\t%s.\n" % (record_row.record_name,record_row.record_value)
    
            if record_row.record_type == "MX":
                zone_type_MX += "%s\tIN\tMX\t%s\t%s.\n" % (record_row.record_name,str(record_row.record_priority),record_row.record_value)
    
            if record_row.record_type == "A":
                zone_type_A += "%s\tIN\tA\t\t%s\n" % (record_row.record_name,record_row.record_value)
    
            if record_row.record_type == "CNAME":
                zone_type_CNAME += "%s\tIN\tCNAME\t\t%s.\n" % (record_row.record_name,record_row.record_value)
    
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
    
        file = open(dir_db_files + "/db." + domain_row.domain, "w")
        file.write(zone)
        file.close()
    
    ''' Cria arquivo apontando as zonas '''
    def create_zone_file(self,dir_db_files,verbose):
    
        domains_table = self.pyTables.domains_table()
        domains_result = self.engine.execute(domains_table.select())
    
        zones = ""
    
        for domain_row in domains_result:
            file = dir_db_files + "/db." + domain_row.domain;
            cmd = "/usr/sbin/named-checkzone -q " + domain_row.domain + " " + file
            result = os.system(cmd)
    
            if result != 0:
    
                if verbose == 1:
                   print ".Bad... bad domain " + domain_row.domain
    
            else:
    
                if verbose == 1:
                   print ".Good domain " + domain_row.domain
    
                zones += "zone \"" + domain_row.domain + "\" {\n"
                zones += "\ttype master;\n"
                zones += "\tfile \"" + dir_db_files + "/db." + domain_row.domain + "\";\n"
                zones += "};\n\n"
    
        file = open("/var/named/chroot/etc/named.pyManDNS.zones", "w")
        file.write(zones);
        file.close()
    
    ''' Roda RNDC '''
    def reload(self,domain=''):
    
        if domain == "":
            cmd = "/usr/sbin/rndc reload >> /dev/null"
        else:
            cmd = "/usr/sbin/rndc reload " + domain + " >> /dev/null"
    
        os.system(cmd)    
