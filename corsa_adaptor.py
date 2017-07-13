# Copyright Sean Donovan, Joaquin Chung
# Corsa-at-GENI project

import logging
import json
from threading import Timer, Lock, Thread
from datetime import datetime, timedelta

from connection_info import ConnectionInfo
from switch import Switch
from neighbor import Neighbor
from bridge import Bridge
from tunnel import Tunnel

from flask import Flask, jsonify

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
        
        # Setup Flask configuration stuff
        self.host = options.host
        self.port = options.port

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

        for switch in data['switches']:
            switch_name = switch['name']
            connection_info = switch['connection-info']
            neighbors = switch['neighbors']

            # Determine the correct href for the switch we're creating
            switch_href = self.base_url + "switches/" + switch_name
            
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

                switch.add_neighbor(neighbor_object)
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

    def get_tunnel(self, switch_name, bridge_name, tunnel_name):
        bridge = self.get_bridge(switch_name, bridge_name)
        for c in bridge.get_tunnels():
            if c.get_name() == tunnel_name:
                return c
        return None

    def main_loop(self):
        app = Flask(__name__, static_url_path='', static_folder='')
        
        @app.route('/', strict_slashes=False, methods=['GET'])
        def flask_index():
            return "Hello World!"

        @app.route('/api/v1/switches', strict_slashes=False, methods=['GET'])
        def flask_switches():
            sw_dict = {}
            for key in self.switches.keys():
                sw_dict[key] = self.switches[key].to_json()
            print sw_dict
            return jsonify(sw_dict)

        @app.route('/api/v1/switches/<switch_name>',
                   strict_slashes=False, methods=['GET'])
        def flask_specific_switch(switch_name):
            sw = self.get_switch(switch_name)
            return jsonify(sw.to_json())

        @app.route('/api/v1/switches/<switch_name>/neighbors',
                   strict_slashes=False, methods=['GET'])
        def flask_neighbors(switch_name):
            sw = self.get_switch(switch_name)
            n_dict = {}
            for n in sw.get_neighbors():
                n_dict[n.get_name()] = n.to_json()
            return jsonify(n_dict)

        @app.route('/api/v1/switches/<switch_name>/neighbors/<neighbor_name>',
                   strict_slashes=False, methods=['GET'])
        def flask_specific_neighbor(switch_name, neighbor_name):
            n = self.get_neighbor(switch_name, neighbor_name)
            return jsonify(n.to_json())

        @app.route('/api/v1/switches/<switch_name>/bridges',
                   strict_slashes=False, methods=['GET'])
        def flask_bridges(switch_name):
            sw = self.get_switch(switch_name)
            b_dict = {}
            for b in sw.get_bridges():
                b_dict[b.get_name()] = b.to_json()
            return jsonify(b_dict)

        @app.route('/api/v1/switches/<switch_name>/bridges/<bridge_name>',
                   strict_slashes=False, methods=['GET'])
        def flask_specific_bridge(switch_name, bridge_name):
            b = self.get_bridge(switch_name, bridge_name)
            return jsonify(b.to_json())

        @app.route('/api/v1/switches/<switch>/bridges/<bridge>/tunnels',
                   strict_slashes=False, methods=['GET'])
        def flask_tunnels(switch, bridge):
            b = self.get_bridge(switch, bridge)
            t_dict = {}
            for t in b.get_tunnels():
                t_dict[t.get_name()] = t.to_json()
            return jsonify(t_dict)

        @app.route('/api/v1/switches/<switch>/bridges/<bridge>/tunnels/<tunnel>',
                   strict_slashes=False, methods=['GET'])
        def flask_specific_tunnel(switch, bridge, tunnel):
            t = self.get_tunnel(switch, bridge, tunnel)
            return jsonify(t.to_json())

        print "STARTING APP.RUN"
        app.run(host=self.host, port=self.port)


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
    
    br.add_tunnel("temp1", 1,  2000)
    br.add_tunnel("temp2", 1,  2001)

    print br

    # Delete tunnel
    br.remove_tunnel("temp1")

    print br
    
    
    # Cleanup!
    sw.remove_bridge("br50")
    print sw
    
    print "\n\n\n\n"
    print json.dumps(sw.get_bridge_list(), indent=2)
    print "\n\n\n\n"


def REST_setup_for_testing(adaptor):
    # Add a few bridges and tunnels for REST testing
    sw = adaptor.get_switch("sox-switch")
    
    br1 = sw.create_bridge("br50", "10.2.3.4", 6633, "100000")
    br2 = sw.create_bridge("br51", "10.2.3.4", 6634, "100001")

    br1.add_tunnel("temp1", 1,  2000)
    br1.add_tunnel("temp2", 1,  2001)
    br2.add_tunnel("temp3", 1,  2002)
    br2.add_tunnel("temp4", 1,  2003)
    br2.add_tunnel("temp5", 1,  2004)
    br2.add_tunnel("temp6", 1,  2005)

    print "br1 tunnels: %s" % br1.get_tunnels()
    print "br2 tunnels: %s" % br2.get_tunnels()

    print "SETUP COMPLETE"


    


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-c", "--config-file", dest="config", type=str, 
                        action="store", help="Specifies the configuration file")

    parser.add_argument("-l", "--log-file", dest="logfile", type=str,
                        action="store", help="Specifies the logfile name",
                        default="corsa_adaptor.log")

    parser.add_argument("-H", "--host", dest="host", type=str,
                        action="store", help="Specifes the host address to use",
                        default="0.0.0.0")
    
    parser.add_argument("-p", "--port", dest="port", type=int,
                        action="store", help="Specifes the port to use",
                        default=5000)
    
                        

    options = parser.parse_args()
    print options
 
    if not options.config:
        parser.print_help()
        exit()

    adaptor = CorsaAdaptor(options)

    #REST_setup_for_testing(adaptor)
    
    adaptor.main_loop()

    #testing(adaptor)



