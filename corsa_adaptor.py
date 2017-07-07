# Copyright Sean Donovan, Joaquin Chung
# Corsa-at-GENI project

import logging
import dataset
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

        # Parse Config File
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
            Config file has Switch information
             - Name
             - Connection info 
             - Neighbors
        '''
        pass

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
 
    if not options.manifest:
        parser.print_help()
        exit()
        
    adaptor = CorsaAdaptor(options)
    adaptor._main_loop()
