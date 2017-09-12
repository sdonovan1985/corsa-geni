# Copyright Sean Donovan, Joaquin Chung
# Corsa-at-GENI project


import requests
import json
from tunnel import Tunnel
from connection_info import ConnectionInfo

# Disable warnings #FIXME!
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Bridge:
    ''' The Bridge object tracks and manages virtual switch objects. 
        Bridge
         - Name
         - Address
         - Send rest boolean
         - DPID
         - Controller info
           - IP or URL
           - TCP Port
         - HTTP connection info (private) - Inherited from Switch
           - IP or URL
           - Security info - REST API key  
         - List of tunnelss
    ''' 
    def __init__(self, name, href, urn, dont_send_rest, connection,
                 dpid=None, controller_addr=None, controller_port=None,
                 tunnels=[]):
        self.name = name
        self.href = href
        self.urn = urn
        self.dont_send_rest = dont_send_rest
        self.connection = connection
        self.dpid = dpid
        self.controller_addr = controller_addr
        self.controller_port = controller_port
        self.tunnels = list(tunnels)
        self.current_vport = 0

    def __str__(self):
        retstr = "BRIDGE %s\n%s\n%s, DPID: %s, Controller: %s:%d" % (self.href,
                                                          self.urn,
                                                          self.name,
                                                          self.dpid,
                                                          self.controller_addr,
                                                          self.controller_port)
        retstr += "\n  TUNNELS:"
        for cxn in self.tunnels:
            retstr += "\n    %s" % str(cxn)
        return retstr

    def __repr__(self):
        return self.__str__()
    
    def get_name(self):
        return self.name

    def get_href(self):
        return self.href

    def get_urn(self):
        return self.urn

    def get_connection_info(self):
        return self.connection

    def get_dpid(self):
        return self.dpid

    def get_controller_addr(self):
        return self.controller_addr

    def get_controller_port(self):
        return self.controller_port

    def get_tunnels(self):
        return self.tunnels

    def add_tunnel(self, dstname, physport, dstvlan):
        # NOTE: this doesn't check for whether or not this is a valid thing to
        # do. The user of this function should be confirming with the switch
        # that a particular VLAN/Port combination is valid.

        # Make sure there isn't already a 'dstname' in the tunnels list
        for tunnel in self.tunnels:
            if tunnel.get_name() == dstname:
                tunnel_names = []
                for t in self.tunnels:
                    tunnel_names.append(t.get_name())
                
                raise Exception("%s already exists as a tunnel name: %s" %
                                (dstname, tunnel_names))
        
        # Find open virtual port number
        self.current_vport += 1
        vport = self.current_vport

        # Create the Tunnel object
        tunnel_href = self.href + "/tunnels/" + str(dstname)
        tunnel = Tunnel(tunnel_href, dstname, physport, dstvlan, vport)

        # Make REST calls to instantiate this new tunnel
        self.add_tunnel_REST_helper(physport, vport, dstvlan)
        
        # Finally, add it to the local list of tunnels
        self.tunnels.append(tunnel)

        return tunnel

    def add_tunnel_REST_helper(self, port, vport, vlan_id):
        if self.dont_send_rest:
            return

        base_url = self.connection.get_address()
        rest_key = self.connection.get_rest_key()
        response = requests.post(base_url+'/api/v1/bridges/'+self.name+'/tunnels',
                                 {'port' : port,
                                  'ofport' : vport,
                                  'vlan-id' : vlan_id},
                                 headers={'authorization':rest_key},
                                 verify=False) #FIXME: fixed value

        if response.status_code != 201:
            #ERROR!
            raise Exception("_add_tunnel Response %d: %s" %
                            (response.status_code, json.dumps(response.json())))
        return response # May not be used

    def remove_tunnel(self, dstname):
        # NOTE: this doesn't check to see if the tunnel already exists on
        # the bridge (it does check if it exists in the Bridge data structure).

        # Find the tunnel in the local list of tunnels
        vport = None
        for tunnel in self.tunnels:
            if tunnel.get_name() == dstname:
                vport = tunnel.get_virtual_port()
                break
        if vport == None:
            raise Exception("dstname %s doesn't exist in tunnels:\n%s" %
                            (dstname, self.tunnels))

        # Make REST calls to delete the tunnel
        self.remove_tunnel_REST_helper(vport)

        self.tunnels.remove(tunnel)

    def remove_tunnel_REST_helper(self, vport):
        if self.dont_send_rest:
            return

        base_url = self.connection.get_address()
        rest_key = self.connection.get_rest_key()
        response = requests.delete(base_url+'/api/v1/bridges/'+self.name+
                                   '/tunnels/'+str(vport),
                                 headers={'authorization':rest_key},
                                 verify=False) #FIXME: fixed value

        if response.status_code != 204:
            #ERROR!
            raise Exception("_remove_tunnel Response %d: %s" %
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
            'bridge':'br1'
            'href': 'https://1.2.3.4/switches/corsa-a/bridges/br1',
            'urn': 'asdfqwerupo8iu12p3o4idsndinpvoin23in',
            'controller-addr': '2.3.4.5',
            'controller-port': '6633',
            'dpid': 'abcdef12345678',
            'tunnels':
              [
                <tunnel1>,
                <tunnel2>,
              ]
        }
        '''
        tunnel_json = []
        for cxn in self.tunnels:
            tunnel_json.append(cxn.to_json())

        retval = {
            'bridge':self.name,
            'href': self.href,
            'urn': self.urn,
            'controller-addr': self.controller_addr,
            'controller-port': self.controller_port,
            'dpid': self.dpid,
            'tunnels': tunnel_json
        } 
        
        return retval


    
