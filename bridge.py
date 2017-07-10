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

    def add_connection(self, connection):
        self.connections.append(connection)

    def set_dpid(self, dpid):
        self.dpid = dpid

    def set_controller(self, controller_addr, controller_port):
        self.controller_addr = controller_addr
        self.controller_port = controller_port

    def delete_bridge(self, ...):
        pass #FIXME - is this even necessary?

    def to_json(self):
        pass #FIXME
    
