# Copyright Sean Donovan, Joaquin Chung
# Corsa-at-GENI project

from bridge import Bridge
from connection_info import ConnectionInfo
from neighbor import Neighbor
import re
import requests
import json
import hashlib

# Disable warnings #FIXME!
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Switch(object):
    ''' Each physical switch will be represented by a switch object.
        
        Switch
         - Name
         - Address (REST address, e.g., /app/switches/sw1)
         - Send rest boolean
         - List of neighbors
         - List of bridges
         - HTTP connection info (private)
           - IP or URL
           - Security info - REST API key 
    '''

    def __init__(self, name, href, dont_send_rest,
                 neighbors=[], bridges=[], connection=None, max_br=100):
        self.name = name
        self.href = href
        self.dont_send_rest = dont_send_rest
        self.neighbors = neighbors
        self.bridges = bridges
        self.connection = connection
        self.max_br = max_br

        # bridge_ht is a handmade hashtable. It's used to reserve br number.
        self.bridge_ht = [None] * self.max_br
        self.bridge_ht[0] = 'reserved' # 0 is always reserved.



    def __str__(self):
        retstr  = "SWITCH: %s\n" % self.name
        retstr += "  %s" % self.href
        n = ""
        for neighbor in self.neighbors:
            n += "\n" + str(neighbor)
        retstr += "\n  NEIGHBORS: %s" % re.sub("\n", "\n    ", n)
        b = ""
        for bridge in self.bridges:
            b += "\n" + str(bridge)
        retstr += "\n  BRIDGES: %s" % re.sub("\n", "\n    ", b)
        return retstr

    def __repr__(self):
        return self.__str__()
    
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

    def set_reserved_bridges(self, list_of_bridges):
        for bridge in list_of_bridges:
            if (self.bridge_ht[bridge] != None):
                raise Exception("set_reserved_bridges: bridge %d is already reserved: %s" % (bridge, self.bridge_ht[bridge]))
            self.bridge_ht[bridge] = "reserved"

    def _get_bridge_ht(self):
        return self.bridge_ht

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def get_bridge_list(self):
        # This is used for querying the switch for existing bridges that have
        # been configured, so that a free name (e.g., "sw3") can be chosen.

        bridge_list = self._get_bridge_REST_helper()
        return bridge_list

    def _get_bridge_REST_helper(self):
        if self.dont_send_rest:
            return
        
        base_url = self.connection.get_address()
        rest_key = self.connection.get_rest_key()
        response = requests.get(base_url+'/api/v1/bridges',
                                headers={'Authorization':rest_key},
                                verify=False)

        print response.json()

        bridge_list = []
        for entry in response.json()['links']:
            bridge_list.append(entry)

        return bridge_list
        
    def create_bridge(self, urn,
                      controller_addr=None, controller_port=None, dpid=None):
        # Figure out the bridge's name. This involves a helper function
        name = self._get_and_reserve_br_name(urn)

        bridge_href = self.href + "/bridges/" + name
        bridge = Bridge(name, bridge_href, urn,
                        self.dont_send_rest, self.connection,
                        dpid, controller_addr, controller_port)

        # Make REST calls to instantiate this new bridge
        self._create_bridge_REST_helper(bridge)
        self._set_controller_REST_helper(bridge)
        
        # Finally, add it to the local list of bridges
        self.bridges.append(bridge)

        return bridge
    def _get_and_reserve_br_name(self, urn):
        orig_hash = int(hashlib.sha224(urn).hexdigest(), 16) % self.max_br

        hash_number = orig_hash

        while (self.bridge_ht[hash_number] != None or
               self.bridge_ht[hash_number] == "reserved"):
            print hash_number
            hash_number += 1
            if hash_number == self.max_br:
                hash_number = 0
            # We've looped all the way through. Not good.
            if hash_number == orig_hash:
                raise Exception("_get_and_reserve_br_name: Ran out of numbers (%d,%d): %s" % (hash_number, orig_hash, self.bridge_ht))

        # Reserve
        self.bridge_ht[hash_number] = urn

        # Return
        return "br%d" % hash_number

    def _unreserve_br_name(self, name):
        # Remove "br" from name (e.g., "br45") to get hash_number
        hash_number = int(name[2:])
        if ((self.bridge_ht[hash_number] == None) or
            (self.bridge_ht[hash_number] == "reserved")):
            raise Exception("_unreserve_br_name: bridge_ht[%d] is invalid: %s" % (hash_number, self.bridge_ht[hash_number]))

        # Unreserve
        self.bridge_ht[hash_number] = None
        
    def _create_bridge_REST_helper(self, bridge):
        if self.dont_send_rest:
            return

        base_url = self.connection.get_address()
        rest_key = self.connection.get_rest_key()
        response = requests.post(base_url+'/api/v1/bridges',
                                 {'bridge' : bridge.get_name(),
                                  'dpid' : bridge.get_dpid(),
                                  'subtype' : 'openflow',
                                  'resources' : 1}, #FIXME: fixed value
                                 headers={'Authorization':rest_key},
                                 verify=False) #FIXME: fixed value

        if response.status_code != 201:
            #ERROR!
            raise Exception("_add_bridge Response %d: %s" %
                            (response.status_code, json.dumps(response.json())))
        return response # May not be used

    def _set_controller_REST_helper(self, bridge):
        if self.dont_send_rest:
            return

        base_url = self.connection.get_address()
        rest_key = self.connection.get_rest_key()
        response = requests.post(base_url+'/api/v1/bridges/'+bridge.get_name()+"/controllers",
                                 {'controller':'ADAPTOR',
                                  'ip':bridge.get_controller_addr(),
                                  'port':bridge.get_controller_port()},
                                 headers={'Authorization':rest_key},
                                 verify=False) #FIXME: fixed value
        if response.status_code != 201:
            #ERROR!
            raise Exception("_set_controller Response %d: %s" %
                            (response.status_code, json.dumps(response.json())))
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
        self._remove_bridge_REST_helper(bridge)

        # Unreserve br number
        self._unreserve_br_name(name)

        # Finally, remove from local list of bridges
        self.bridges.remove(bridge)

    def _remove_bridge_REST_helper(self, bridge):
        if self.dont_send_rest:
            return

        base_url = self.connection.get_address()
        rest_key = self.connection.get_rest_key()
        response = requests.delete(base_url+'/api/v1/bridges/'+str(bridge.get_name()),
                                   headers={'Authorization':rest_key},
                                   verify=False) #FIXME: fixed value

        if response.status_code != 204:
            raise Exception("_remove_bridge Response %d: %s" %
                            (response.status_code, json.dumps(response.json())))

        return response


    def to_json(self):
        '''
        {
            'switch':'sox-switch',
            'href':'https://1.2.3.4/switches/sox-switch',
            'neighbors':
                [
                  <neighbor1>,
                  <neighbor2>
                ],
            'bridges':
                [
                  <bridge1>,
                  <bridge2>
                ]
        }
        '''
        neighbors_json = []
        for n in self.neighbors:
            neighbors_json.append(n.to_json())

        bridges_json = []
        for b in self.bridges:
            bridges_json.append(b.to_json())

        retval = {
            'switch':self.name,
            'href':self.href,
            'neighbors':neighbors_json,
            'bridges':bridges_json
        }

        return retval
            

    def corsa_api_get(self, path):
        if self.dont_send_rest:
            return

        base_url = self.connection.get_address()
        rest_key = self.connection.get_rest_key()
        # The "/" is because the leading "/" will be stripped out of the path.
        response = requests.get(base_url + "/" + str(path),
                                headers={'Authorization':rest_key},
                                verify=False)
        print response.json()
        return response.json()

    def big_red_button(self):
        ''' This cleans up everything on a switch. More than a little dangerous.
        '''
        if self.dont_send_rest:
            return

        base_url = self.connection.get_address()
        rest_key = self.connection.get_rest_key()

        # Get all bridges - based on _get_bridge_REST_helper()
        response = requests.get(base_url+'/api/v1/bridges',
                                headers={'Authorization':rest_key},
                                verify=False)
        bridge_links = {}
        for entry in response.json()['links']:
            bridge_links[str(entry)] = str(response.json()['links'][entry]['href'])

        # for each bridge, delete all tunnels then delete the bridge itself.
        for bridge in bridge_links.keys():
            bridge_href = bridge_links[bridge]

            # Get all tunnels:
            response = requests.get(bridge_href + "/tunnels",
                                    headers={'Authorization':rest_key},
                                    verify=False)

            # For each tunnel, delete
            for entry in response.json()['links']:
                requests.delete(response.json()['links'][entry]['href'],
                                headers={'Authorization':rest_key},
                                verify=False)
            
            # Delete bridge
            requests.delete(bridge_href,
                            headers={'Authorization':rest_key},
                            verify=False)
            
