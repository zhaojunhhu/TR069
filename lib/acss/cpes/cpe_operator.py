#coding:utf-8

"""
    nwf 2014-06-14  create

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



class CpeOperator(object):
    """
    """    
    
    m_dict_operator_cfg                 = dict()    # {("CT","v3.0"):cfg1, }
    m_dict_operator_default             = dict()    # {"CT":"v3.0",}
    m_list_operator                     = []        # ["CT",]
    m_dict_operator_versions            = {}        # {"CT":["v3.0',"v4.0"]}

    
    def __init__(self, name, interface_version):
        """        
        """
        self.name                       = name                  # key1
        self.interface_version          = interface_version     # key2
        
        self.base_isp                  = "CT"
        self.eventcode_map              = ""
        self.cpe2acs_name               = ""
        self.cpe2acs_password           = ""
        self.acs2cpe_name               = ""
        self.acs2cpe_password           = ""


    @staticmethod
    def get_operator(name, interface_version):
        """
        """
        d1 = CpeOperator.m_dict_operator_cfg
        pair1 = (name, interface_version)
        operator = d1.get(pair1)
        if (not operator):
            operator = CpeOperator(name, interface_version)
            
        return operator

        
    @staticmethod
    def set_operator(name, interface_version, operator):
        """
        """
        d1 = CpeOperator.m_dict_operator_cfg
        pair1 = (name, interface_version)
        d1[pair1] = operator


    @staticmethod
    def set_operator_interface_version_default(name, interface_version_default):
        """
        """
        CpeOperator.m_dict_operator_default[name] = interface_version_default
        
        
    @staticmethod
    def get_operator_interface_version_default(name):
        """
        """        
        return CpeOperator.m_dict_operator_default.get(name)


    @staticmethod
    def get_operator_eventcode_map(name, interface_version):
        """
        """
        eventcode_map = ""
        
        d1 = CpeOperator.m_dict_operator_cfg
        pair1 = (name, interface_version)
        operator = d1.get(pair1)
        if (operator):
            eventcode_map = operator.eventcode_map

        return eventcode_map


    @staticmethod
    def set_operator_name(name):
        """
        """
        list1 = CpeOperator.m_list_operator
        if (name not in list1):
            list1.append(name)       


    @staticmethod
    def get_operators_name():
        """
        """
        return CpeOperator.m_list_operator


    @staticmethod
    def set_operator_version(name, version1):
        """
        """
        dict1 = CpeOperator.m_dict_operator_versions
        if (not dict1.get(name)):
            dict1[name] = []
        dict1[name].append(version1)


    @staticmethod
    def get_operator_versions(name):
        """
        """
        list1 = CpeOperator.m_dict_operator_versions.get(name, [])
        return list1
      