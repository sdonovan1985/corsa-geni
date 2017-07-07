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
        self.db = self._setup_database(options.database)
        self.switch_table = self.db['switches']
        self.bridge_table = self.db['bridges']
        self.connection_table = self.db['connections']
        
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
        db = dataset.connect('sqlite:///' + db_location, 
                             engine_kwargs={'connect_args':
                                            {'check_same_thread':False}})
        return db
        
        
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
