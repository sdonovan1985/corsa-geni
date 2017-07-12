# Copyright Sean Donovan, Joaquin Chung
# Corsa-at-GENI project

from bridge import Bridge
from neighbor import *
import re

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
        retstr  = "SWITCH: %s\n" % self.name
        retstr += "  %s" % self.href
        retstr += "  NEIGHBORS: %s" % re.sub("\n", "\n    ",
                                             str(self.neighbors))
        retstr += "  BRIDGES: %s" % re.sub("\n", "\n    ",
                                           str(self.bridges))
        return retstr
    
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

    def set_connection_info(self, cxn_info):
        if type(cxn_info) != ConnectionInfo:
            raise Exception("cxn_info is not ConnectionInfo. type:%s, value:%s",
                            type(cxn_info), str(ConnectionInfo))
        self.connection = cxn_info

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def get_bridge_list(self):
        # This is used for querying the switch for existing bridges that have
        # been configured, so that a free name (e.g., "sw3") can be chosen.
        pass

    def _get_bridge_REST_helper(self):
        pass
        
    def create_bridge(self, name,
                      controller_addr=None, controller_port=None, dpid=None):
        bridge_href = self.href + "/bridges/" + name
        bridge = Bridge(name, href, self.connection,
                        dpid, controller_addr, controller_port)

        # Make REST calls to instantiate this new bridge
        #FIXME
        
        # Finally, add it to the local list of bridges
        self.bridges.append(bridge)

        
    def _add_bridge_REST_helper(self, bridge):
        base_url = self.connection.get_address()
        rest_key = self.connection.get_rest_key()
        response = requests.post(bridge.get_name()+'api/v1/bridges',
                                 {'bridge' : bridge.get_name(),
                                  'dpid' : bridge.get_dpid(),
                                  'subtype' : 'openflow',
                                  'resources' : 1}, #FIXME: fixed value
                                 headers={'Authorization':rest_key},
                                 verify=False) #FIXME: fixed value

        if response.status_code != 200:
            #ERROR!
            raise Exception("_add_bridge Response %d: %s" %
                            (response.status_code, str(response)))
        return response # May not be used

    def remove_bridge(self, name):
        bridge = None
        for b in self.bridges:
            if b.get_name() == name:
                bridge = b
                break
        if bridge == None:
            raise Exception("%s not in list of bridges:\n%s" % (name,
                                                        self.get_bridges()))
        # Make REST calls to delete bridge
        #FIXME

        # Finally, remove from local list of bridges
        self.bridges.remove(bridge)

    def _remove_bridge_REST_helper(self, bridge):
        base_url = self.connection.get_address()
        rest_key = self.connaction.get_rest_key()
        response = requests.delete(url+'api/v1/bridges/'+str(bridge.get_name()),
                                   headers={'Authorization':rest_key},
                                   verify=False) #FIXME: fixed value

        if response.status_code != 100000: #FIXME - What's the good number?
            raise Exception("_remove_bridge Response %d: %s" %
                            (response.status_code, str(response)))

        return response


    def to_json(self):
        pass #FIXME

