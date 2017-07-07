# Copyright Sean Donovan, Joaquin Chung
# Corsa-at-GENI project

class Connection(object):
    ''' A connection describes how a bridge's virtual port is mapped to its
        switch's physical port/VLAN combination
        
        Connection
         - Address
         - Destination Name
         - Destination Physical Port
         - Destination VLAN
         - Virtual Port
    '''

    def __init__(self, href, name, physport, vlan, vport):
        self.href = href
        self.name = name
        self.physport = physport
        self.vlan = vlan
        self.vport = vport

    def __str__(self):
        pass #FIXME

    def get_href(self):
        return self.href

    def get_destination_name(self):
        return self.name

    def get_desitnation_physical_port(self):
        return self.physport
    
    def get_destination_vlan(self):
        return self.vlan
    
    def get_virtual_port(self):
        return self.vport

    def to_json(self):
        pass #FIXME
