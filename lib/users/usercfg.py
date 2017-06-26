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
CONFIG_PATH = os.path.join(dirname(dirname(dirname(__file__))), "data", "user.cfg")

def read_config():
    ret, ret_data = config.read_cfg(path=CONFIG_PATH, keys = "user")
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
    AGENT_HTTP_IP           = str(dict_cfg.get("AGENT_HTTP_IP"))
    AGENT_HTTP_PORT         = int(dict_cfg.get("AGENT_HTTP_PORT"))
except Exception,e:    
    desc = "fail:%s" %(e)
    log.debug_err(desc)
    raise Exception(desc)


# worklist tcp ip+port
#AGENT_HTTP_IP               = "172.123.101.253"
#AGENT_HTTP_PORT             = 50000


#  -----------------------------------------------------------
USER_PAGE                   = "/user"


#  -----------------------------------------------------------
RPC_TIMEOUT                 = 520		# acs=500, agent=510; user=520
WORKLIST_TIMEOUT            = 3600
SHORT_CONNECTION_TIMEOUT    = 36        # user>agent>acs

WORKLIST_EXEC_QUERY_SLEEP   = 15 
WAIT_EVENTCODE_QUERY_SLEEP  = 3     # 2013-07-08;granularity


