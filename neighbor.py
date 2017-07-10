# Copyright Sean Donovan, Joaquin Chung
# Corsa-at-GENI project

NETWORK = "network"
SWITCH  = "switch"


class Neighbor(object):
    ''' Physical switches have one or more "neighbors", which are neighboring 
        networks or other switches.
    '''

    def __init__(self, name, href, vlans, type=NETWORK):
        self.name = name
        self.href = href
        self.vlans = vlans
        self.type = type

    def __str__(self):
        retstr = "%s %s TYPE:%s VLANS: %s" % (self.href, self.name,
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
                 
