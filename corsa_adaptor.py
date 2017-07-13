# Copyright Sean Donovan, Joaquin Chung
# Corsa-at-GENI project

import logging
import json
from threading import Timer, Lock, Thread
from datetime import datetime, timedelta

from bridge import Bridge
from connection import Connection
from switch import Switch
from neighbor import Neighbor
from connection_info import ConnectionInfo


class CorsaAdaptor(object):
    ''' The CorsaAdaptor is used to run the adaptation work. 
    '''

    def __init__(self, options):
        # Setup logging
        self._setup_logger(options.logfile, 'adaptor')

        # Setup local storage
        self.switches = {}
        
        # Parse Config File. The following will be set:
        #   - self.base_url
        self._parse_config_file(options.config)

        
        # Setup Flask nonsense

        # 

        pass

    def _setup_logger(self, filename, logname):
        ''' Internal function for setting up the logger formats. '''
        # reused from https://github.com/sdonovan1985/netassay-ryu/blob/master/base/mcm.py
        formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
        console = logging.StreamHandler()
        console.setLevel(logging.WARNING)
        console.setFormatter(formatter)
        logfile = logging.FileHandler(filename)
        logfile.setLevel(logging.DEBUG)
        logfile.setFormatter(formatter)
        self.logger = logging.getLogger(logname)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(console)
        self.logger.addHandler(logfile)
        
    def _parse_config_file(self, config_file):
        ''' Config file has general configuration, such as href prefix.
            Config file has information for Switches
             - Name
             - Connection info 
             - Neighbors
        '''
        with open(config_file) as data_file:
            data = json.load(data_file)

        self.base_url = data['adaptor-href-base']

        print json.dumps(data, indent=2)
        
        for switch in data['switches']:
            switch_name = switch['name']
            connection_info = switch['connection-info']
            neighbors = switch['neighbors']

            # Determine the correct href for the switch we're creating
            switch_href = self.base_url + "/switches/" + switch_name
            
            # Create Switch object
            switch = Switch(switch_name, switch_href)
            
            # Create the ConnectionInfo object and add it to the switch
            cxn_info_object = ConnectionInfo(connection_info['address'],
                                             connection_info['rest_key'])
            switch.set_connection_info(cxn_info_object)


            # Create all the neighbors and add them to the switch object
            for neighbor in neighbors:
                neighbor_name = neighbor['name']
                neighbor_type = neighbor['type']
                neighbor_physport = neighbor['port']
                neighbor_vlans = neighbor['vlans']
                neighbor_href = switch_href + "/neighbors/" + neighbor_name
                neighbor_object = Neighbor(neighbor_name, neighbor_href,
                                           neighbor_physport, neighbor_vlans,
                                           neighbor_type)

                switch.add_neighbor(neighbor)
            # Save off switch
            self.switches[switch_name] = switch

    def get_switch(self, switch_name):
        return self.switches[switch_name]

    def get_neighbor(self, switch_name, neighbor_name):
        neighbors = self.switches[switch_name].get_neighbors()
        for n in neighbors:
            if n.get_name() == neighbor_name:
                return n
        return None

    def get_bridge(self, switch_name, bridge_name):
        bridges = self.get_switch(switch_name).get_bridges()
        for b in bridges:
            if b.get_name() == bridge_name:
                return b
        return None

    def get_connection(self, switch_name, bridge_name, connection_name):
        bridge = self.get_bridge(switch_name, bridge_name)
        for c in bridge.get_connections():
            if c.get_name() == connection_name:
                return c
        return None
        
    # FLASK main loop
    def _main_loop(self):
        pass

    
    # FLASK Endpoints


def testing(adaptor):
    # Testing code.
    print adaptor.switches

    sw = adaptor.get_switch("sox-switch")
    print "switch is:\n%s" % sw

    print "\n\n\n\n"
    print json.dumps(sw.get_bridge_list(), indent=2)
    print "\n\n\n\n"


    # Create bridge
    sw.create_bridge("br50", "10.2.3.4", 6633, "100000")
    
    print "CREATED NEW BRIDGE:\n%s" % sw
    
    print "\n\n\n\n"
    print json.dumps(sw.get_bridge_list(), indent=2)
    print "\n\n\n\n"
    
    
    
    # Create tunnel
    br = adaptor.get_bridge("sox-switch", "br50")
    print br
    
    br.add_connection("temp1", 1,  2000)
    br.add_connection("temp2", 1,  2001)

    print br

    # Delete tunnel
    br.remove_connection("temp1")

    print br
    
    
    # Cleanup!
    sw.remove_bridge("br50")
    print sw
    
    print "\n\n\n\n"
    print json.dumps(sw.get_bridge_list(), indent=2)
    print "\n\n\n\n"



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-c", "--config-file", dest="config", type=str, 
                        action="store", help="Specifies the configuration file")

    parser.add_argument("-l", "--log-file", dest="logfile", type=str,
                        action="store", help="Specifies the logfile name.",
                        default="corsa_adaptor.log")

    options = parser.parse_args()
    print options
 
    if not options.config:
        parser.print_help()
        exit()
        
    adaptor = CorsaAdaptor(options)
    adaptor._main_loop()
    #testing(adaptor)



