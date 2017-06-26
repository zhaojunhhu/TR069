#!/usr/bin/env python
import os
SUCCESS = 1
FAIL = -1
from ConfigParser import ConfigParser

class CaseSConfigParser(ConfigParser):
    def __init__(self):
        ConfigParser.__init__(self)


    def optionxform(self, optionstr):
        return optionstr

def read_cfg(path = "", keys = ""):
    """
    path = config file's path  + file name
    return:
        success:(1, dict_data)
        fail:(-1, str_fail_message)
    """
    try:
        config = CaseSConfigParser()
        
        if os.path.exists(path):
            config.read(path)
            bool_value = config.has_section(keys)
            if bool_value:
                return SUCCESS, dict(config.items(keys))
            else:
                return FAIL, "Can't find  %s in the config file!" % keys
        else:
            return FAIL, "Can't find  config file %s" % path
    except Exception,e:
        return FAIL, e
        
def write_cfg(path = "", section = "", dict_data = {}):
    """
    path = config file's path  + file name
    return:
        success: (1,"")
        fail:(-1, str_fail_message)
    """
    try:
        config = CaseSConfigParser()
        if os.path.exists(path):
            config.read(path)
            if config.has_section(section):
                pass
            else:
                config.add_section(section)
                
            for k,v in dict_data.items():
                config.set(section,k,v)
            config.write(open(path, "w"))
            return SUCCESS, ""
        else:
            return FAIL, "Can't find  config file %s" % path
    except Exception,e:
        return FAIL,e
    
def read_cfg_sectios_list(path = ""):
    """
    path = config file's path  + file name
    return:
            list_data  all sectios
            None  
    """
    try:
        config = CaseSConfigParser()
        
        if os.path.exists(path):
            config.read(path)
            list_sectios = config.sections()
            if list_sectios and len(list_sectios) > 0:
                return SUCCESS, list_sectios
            else:
                return FAIL, "Not data in the %s" % path
        else:
            return FAIL, "Can't find  config file %s" % path
    except Exception,e:
        return FAIL, e
    
def remove_sectios(path = "", sectios = ""):
    """
    path = config file's path  + file name
    return:
            list_data  all sectios
            None  
    """
    try:
        config = CaseSConfigParser()
        
        if os.path.exists(path):
            config.read(path)
            list_sectios = config.remove_section(sectios)
            config.write(open(path, "w"))
            return SUCCESS, None
        else:
            return FAIL, "Can't find  config file %s" % path
    except Exception,e:
        return FAIL, e

def read_option(path, section, option):
    """
    """
    try:
        config = ConfigParser.ConfigParser()
        
        if os.path.exists(path):
            config.read(path)
            value = config.get(section, option)
        else:
            return FAIL, "Can't find  config file %s" % path
    except Exception,e:
        return FAIL, e
    
    return SUCCESS, value
    
    
if __name__ == '__main__':
    path = "c:/rasphone.pbk"
    obj = open(path,"r+")
    m = []
    for i in obj:
       i = i.replace("\n", "")
       i = i.replace("\r", "")
       m.append(i)   
    print m
        