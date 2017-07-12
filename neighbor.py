# Copyright Sean Donovan, Joaquin Chung
# Corsa-at-GENI project

NETWORK = "network"
SWITCH  = "switch"


class Neighbor(object):
    ''' Physical switches have one or more "neighbors", which are neighboring 
        networks or other switches.
    '''

    def __init__(self, name, href, vlans, physport, type=NETWORK):
        self.name = name
        self.href = href
        self.physport = physport
        self.vlans = vlans
        self.type = type

    def __str__(self):
        retstr = "NEIGHBOR %s %s TYPE:%s VLANS: %s" % (self.href, self.name,
                                                       self.type, self.vlans)
        return retstr

    def get_name(self):
        return self.name

    def get_href(self):
        return self.href

    def get_vlans(self):
        return self.vlans

    def get_type(self):
        return self.type

    def to_json(self):
        '''
        {
            'neighbor':'gatech-ig',
            'href': 'https://1.2.3.4/switches/corsa-a/neighbors/gatech-ig',
            'physical-port': 2,
            'vlans': [3535, 3536, 3537, 3538, 3539],
            'type': 'network'
        }
        '''
        retval = {
            'neighbor':self.name,
            'href':self.href,
            'physical-port':self.physport,
            'vlans':self.vlans,
            'type':self.type
        }

        return retval
