# Copyright Sean Donovan, Joaquin Chung
# Corsa-at-GENI project

class Tunnel(object):
    ''' A tunnel describes how a bridge's virtual port is mapped to its
        switch's physical port/VLAN combination
        
        Tunnel
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
        retstr = ("%s %s, Physical Port: %d, VLAN: %d, Virtual Port: %s" %
                  (self.href, self.name, self.physport, self.vlan, self.vport))
        return retstr

    def __repr__(self):
        return self.__str__()
    
    def get_href(self):
        return self.href

    def get_name(self):
        return self.name

    def get_physical_port(self):
        return self.physport
    
    def get_vlan(self):
        return self.vlan
    
    def get_virtual_port(self):
        return self.vport

    def to_json(self):
        '''
        {
            'tunnel':'clemson',
            'href':'https://1.2.3.4/switches/corsa-a/bridges/br1/tunnels/clemson',
            'physical-port':3,
            'vlan':3535,
            'virtual-port':6,
        }
        '''
        retval = {
            'tunnel':self.name,
            'href':self.href,
            'physical-port':self.physport,
            'vlan':self.vlan,
            'virtual-port':self.vport
        }

        return retval
        
