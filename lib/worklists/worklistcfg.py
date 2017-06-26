#coding:utf-8

# ***************************************************************************
#
#  nwf      2013-05-24      refactor(unify)
#  nwf      2013-06-07      ini->py
# ***************************************************************************


import os
import sys
import TR069.lib.common.logs.log as log
import TR069.lib.common.config as config

dirname = os.path.dirname
# 2014-06-25; data split
CONFIG_PATH = os.path.join(dirname(dirname(dirname(__file__))), "data", "worklist.cfg")

def read_config():
    ret, ret_data = config.read_cfg(path=CONFIG_PATH, keys = "worklist")
    if ret == config.FAIL:
        err_info = "read config file failed, err info:%s!" % ret_data
        log.debug_err(err_info)
        ret_data = {}
    return ret_data

dict_cfg = read_config()
if (not dict_cfg):
    desc = "read config file=%s fail" %CONFIG_PATH
    log.debug_err(desc)
    raise Exception(desc)

# from cfg file --------------------------------------------------------
try:
    HTTP_IP                 = str(dict_cfg.get("WORKLIST_HTTP_IP"))
    HTTP_PORT               = int(dict_cfg.get("WORKLIST_HTTP_PORT"))
    AGENT_HTTP_IP           = str(dict_cfg.get("AGENT_HTTP_IP"))
    AGENT_HTTP_PORT         = int(dict_cfg.get("AGENT_HTTP_PORT"))
except Exception,e:    
    desc = "fail:%s" %(e)
    log.debug_err(desc)
    raise Exception(desc)


#HTTP_IP             = "172.123.101.253"
#HTTP_PORT           = 40000
AGENT2WORKLIST_PAGE = "/user"
    
#AGENT_HTTP_IP       = "172.123.101.253"
#AGENT_HTTP_PORT     = 50000

WORKLIST2AGENT_PAGE = "/user"

# -----------------------------------------------------------------    
SHORT_CONNECTION_TIMEOUT    	= 30

REBOOT_WAIT_NEXT_INFORM_TIMEOUT = 240

# -----------------------------------------------------------------
SCRIPT_ROOT_DIR_NAME        = "operator"
SCRIPT_ROOT_DIR             = os.path.join(dirname(dirname(__file__)), "worklists", SCRIPT_ROOT_DIR_NAME)

BUSINESS_DOMAINS            = "business"
SYSTEM_DOMAINS              = "system"

SCRIPT_DATA_FILE_NAME       = "data"
SCRIPT_FILE_NAME            = "script"  # no .py

DOMAIN_SCRIPT_FILE_ENTRY    = "test_script"   


