# Copyright Sean Donovan, Joaquin Chung
# Corsa-at-GENI project


import requests
from connection import Connection
from connection_info import ConnectionInfo

# Disable warnings #FIXME!
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Bridge(object):
    ''' The Bridge object tracks and manages virtual switch objects. 
        Bridge
         - Name
         - Address
         - DPID
         - Controller info
           - IP or URL
           - TCP Port
         - HTTP connection info (private) - Inherited from Switch
           - IP or URL
           - Security info - REST API key  
         - List of connections
    ''' 
    def __init__(self, name, href, connection,
                 dpid=None, controller_addr=None, controller_port=None,
                 connections=[]):
        self.name = name
        self.href = href
        self.connection = connection
        self.dpid = dpid
        self.controller_addr = controller_addr
        self.controller_port = controller_port
        self.connections = connections
        self.current_vport = 0

    def __str__(self):
        retstr = "%s\n%s, DPID: %s, Controller: %s:%d" % (self.href, self.name,
                                                          self.dpid,
                                                          self.controller_addr,
                                                          self.controller_port)
        retstr += "\n  CONNECTIONS:"
        for cxn in self.connections:
            retstr += "\n    %s" % str(cxn)
        return retstr

    def __del__(self):
        pass #FIXME

    def get_name(self):
        return self.name

    def get_href(self):
        return self.href

    def get_connection_info(self):
        return self.connection

    def get_dpid(self):
        return self.dpid

    def get_controller_addr(self):
        return self.controller_addr

    def get_controller_port(self):
        return self.controller_port

    def get_connections(self):
        return self.connections

    def add_connection(self, dstname, physport, dstvlan):
        # NOTE: this doesn't check for whether or not this is a valid thing to
        # do. The user of this function should be confirming with the switch
        # that a particular VLAN/Port combination is valid.

        # Find open virtual port number
        vport = self.current_vport
        self.current_vport += 1

        # Create the Connection object
        connection_href = self.href + "/connections/" + str(dstname)
        cxn = Connection(connection_href, dstname, physport, dstvlan, vport)

        # Make REST calls to instantiate this new connection
        self.add_connection_rest_helper(physport, vport, dstvlan)
        
        # Finally, add it ot the local list of bridges
        self.connections.append(connection)

        return connection

    def add_connection_REST_helper(self, port, vport, vlan_id):
        base_url = self.connection.get_address()
        rest_key = self.connection.get_rest_key()
        response = requests.post(url+'api/v1/bridges/'+self.name+'/tunnels',
                                 {'port' : port,
                                  'ofport' : vport,
                                  'vlan-id' : vlan_id},
                                 headers={'authorization':rest_key},
                                 verify=False) #FIXME: fixed value

        if response.status_code != 200:
            #ERROR!
            raise Exception("_add_connection Response %d: %s" %
                            (response.status_code, str(response)))
        return response # May not be used

    def remove_connection(self, dstname):
        # NOTE: this doesn't check to see if the connection already exists on
        # the bridge (it does check if it exists in the Bridge data structure).

        # Find the connection in the local list of connections
        vport = None
        for cxn in self.connections:
            if cxn.get_name() == dstname:
                vport = cxn.get_vport()
                break
        if vport == None:
            raise Exception("dstname %s doesn't exist in connections:\n%s" %
                            (dstname, self.connections))

        # Make REST calls to delete the connection
        self.remove_connection_REST_helper(vport)

    def remove_connection_REST_helper(self, vport):
        base_url = self.connection.get_address()
        rest_key = self.connection.get_rest_key()
        response = requests.delete(url+'api/v1/bridges/'+self.name+
                                   '/tunnels/'+vport,
                                 headers={'authorization':rest_key},
                                 verify=False) #FIXME: fixed value

        if response.status_code != 10000: #FIXME - What's the good number?
            #ERROR!
            raise Exception("_remove_connection Response %d: %s" %
                            (response.status_code, str(response)))
        return response # May not be used
    
    def set_dpid(self, dpid):
        self.dpid = dpid

    def set_controller(self, controller_addr, controller_port):
        self.controller_addr = controller_addr
        self.controller_port = controller_port

    def to_json(self):
        '''
        {
            'bridge':'sw1'
            'href': 'https://1.2.3.4/switches/corsa-a/bridges/sw1',
            'controller-addr': '2.3.4.5',
            'controller-port': '6633',
            'dpid': 'abcdef12345678',
            'connections':
              [
                <connection1>,
                <connection2>,
              ]
        }
        '''
        connection_json = []
        for cxn in self.connections:
            connection_json += cxn.to_json()

        retval = {
            'bridge':self.name: 
            'href': self.href,
            'controller-addr': self.controller_addr,
            'controller-port': self.controller_port,
            'dpid': self.dpid,
            'connections': connection_json
        } 
        
        return retval


    
