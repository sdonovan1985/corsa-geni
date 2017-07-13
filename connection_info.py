# Copyright Sean Donovan, Joaquin Chung
# Corsa-at-GENI project

class ConnectionInfo(object):
    ''' Holder class for connection info used by switches and bridges. '''

    def __init__(self, address, rest_key):
        self.address = address
        self.rest_key = rest_key

    def __str__(self):
        retstr = "%s:%s" % (self.address, self.rest_key)
        return retstr

    def get_address(self):
        return self.address

    def get_rest_key(self):
        return self.rest_key
