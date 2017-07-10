# Copyright Sean Donovan, Joaquin Chung
# Corsa-at-GENI project

import logging
import dataset
import json
import cPickle as pickle
from threading import Timer, Lock, Thread
from datetime import datetime, timedelta

from bridge import Bridge
from connection import Connection
from switch import Switch
from connection_info import ConnectionInfo


class CorsaAdaptor(object):
    ''' The CorsaAdaptor is used to run the adaptation work. 
    '''

    def __init__(self, options):
        # Setup logging
        self._setup_logger(options.logfile, 'adaptor')
        
        # Setup DB
        self._setup_database(options.database)

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

    def _setup_database(self, db_location):
        ''' Returns DB link. '''
        self.db = dataset.connect('sqlite:///' + db_location, 
                                  engine_kwargs={'connect_args':
                                                 {'check_same_thread':False}})
        self.switch_table = self.db['switches']
        self.bridge_table = self.db['bridges']
        self.connection_table = self.db['connections']

    def _parse_config_file(self, config_file):
        ''' Config file has general configuration, such as href prefix.
            Config file has information for Switches
             - Name
             - Connection info 
             - Neighbors
        '''
        with open(config_filename) as data_file:
            data = json.load(data_file)

        self.base_url = data['adaptor-href-base']

        for switch in data['switches']:
            switch_name = data['switches'][switch]['name']
            connection_info = data['switches'][switch]['connection-info']
            neighbors = data['switches'][switch]['neighbors']

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
                neighbor_vlans = neighbor['vlans']
                neighbor_href = switch_href + "/neighbors/" + neighbor_name
                neighbor_object = Neighbor(neighbor_name, neighbor_href,
                                           neighbor_vlans, neighbor_type)
                self.upsert_neighbor(neighbor)
                
                switch.add_neighbor(neighbor)
            # Insert switch into DB
            self.upsert_switch(switch)

    # Read https://dataset.readthedocs.io/en/latest/api.html#dataset.Table.upsert for how upsert works
    def upsert_switch(self, switch):
        pass

    def upsert_neighbor(self, neighbor):
        pass

    def upsert_bridge(self, bridge):
        pass

    def upsert_connection(self, connection):
        pass


    def get_switch(self, switch_name):
        pass

    def get_neighbor(self, switch_name, neighbor_name):
        pass

    def get_bridge(self, switch_name, bridge_name):
        pass

    def get_connection(self, switch_name, bridge_name, connection_name):
        pass
        
    # FLASK main loop
    def _main_loop(self):
        pass
        
    # FLASK Endpoints




if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-d", "--database", dest="database", type=str, 
                        action="store", help="Specifies the database ", 
                        default=":memory:")
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
