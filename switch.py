# Copyright Sean Donovan, Joaquin Chung
# Corsa-at-GENI project

from bridge import Bridge
from neighbor import Neighbor

class Switch(object):
    ''' Each physical switch will be represented by a switch object.
        
        Switch
         - Name
         - Address (REST address, e.g., /app/switches/sw1)
         - List of neighbors
         - List of bridges
         - HTTP connection info (private)
           - IP or URL
           - Security info - REST API key 
    '''

    def __init__(self, name, href,
                 neighbors=[], bridges=[], connection=None):
        self.name = name
        self.href = href
        self.neighbors = neighbors
        self.bridges = bridges
        self.connection = connection

    def __str__(self):
        pass #FIXME
    
    def get_name(self):
        return self.name

    def get_href(self):
        return self.href

    def get_neighbors(self):
        return self.neighbors

    def get_bridges(self):
        return self.bridges

    def get_connection_info(self):
        return self.connection

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def add_bridge(self, bridge):
        self.bridges.append(bridge)

    def to_json(self):
        pass #FIXME

