#coding:utf-8

"""
    nwf 2014-03-05  create

"""

# sys lib
import  sys
import  os
import  random
import  time
from    datetime                        import  datetime
from    datetime                        import  timedelta


# user lib
from    TR069.lib.common.error          import  *
from    TR069.lib.common.event          import  *
import  TR069.lib.common.logs.log       as      log 
import  TR069.lib.common.database       as      db
import  TR069.lib.acss.acs.webservercfg         as      webservercfg
from    TR069.lib.common.function       import  print_trace, get_id

# ----------------------------------  ----------------------------

class CpeDbIndex(object):
    """
    cpe db index
    """    
    
    
    def __init__(self, cpe):
        """
        
        """
        self.cpe                        = cpe        

        self.rpc_id                     = 0
        self.soap_204_id                = 0         # 204 soap id
        self.soap_inform_id             = 0         # all inform soap id
        self.soap_inform_id_4rpc        = 0         # inform soap id for rpc        

    def get_rpc_id(self):
        return self.rpc_id
    def set_rpc_id(self, id_):
        self.rpc_id = id_

    def get_soap_204_id(self):
        return self.soap_204_id
    def set_soap_204_id(self, id_):
        self.soap_204_id = id_

    def get_soap_inform_id_4rpc(self):
        return self.soap_inform_id_4rpc
    def set_soap_inform_id_4rpc(self, id_):        
        self.soap_inform_id_4rpc = id_

    def get_soap_inform_id(self):
        return self.soap_inform_id
    def set_soap_inform_id(self, id_):
        self.soap_inform_id = id_            


