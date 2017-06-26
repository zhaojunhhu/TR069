#coding:utf-8


# ***************************************************************************
#
#  nwf      2013-05-24      refactor(unify)
#  nwf      2013-06-07      ini->py
#  nwf		2014-06-25		py拆分=py + cfg
# ***************************************************************************


import os
import sys
import TR069.lib.common.logs.log as log
import TR069.lib.common.config as config

dirname = os.path.dirname
# 2014-06-25; data split
CONFIG_PATH = os.path.join(dirname(dirname(dirname(dirname(__file__)))), "data", "acs.cfg")

def read_config():
    ret, ret_data = config.read_cfg(path=CONFIG_PATH, keys = "acs")
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
    HTTP_IP                 = str(dict_cfg.get("ACS_HTTP_IP"))
    HTTP_PORT               = int(dict_cfg.get("ACS_HTTP_PORT"))
    AGENT_HTTP_IP           = str(dict_cfg.get("AGENT_HTTP_IP"))
    AGENT_HTTP_PORT         = int(dict_cfg.get("AGENT_HTTP_PORT"))

    DB_SERVER               = str(dict_cfg.get("DB_SERVER"))
    DB_PORT                 = int(dict_cfg.get("DB_PORT"))
    DB_DATABASE             = str(dict_cfg.get("DB_DATABASE"))
    DB_UID                  = str(dict_cfg.get("DB_UID"))
    DB_PWD                  = str(dict_cfg.get("DB_PWD"))
    
except Exception,e:    
    desc = "fail:%s" %(e)
    log.debug_err(desc)
    raise Exception(desc)

#  -----------------------------------------------------------   
SUPPORT_CLIENT_VERSIONS_STABLE      = ["v2.3.0", "v2.3.1", "v2.3.2"]
SUPPORT_CLIENT_VERSIONS_BETA        = ["v.beta131021.svn1719"]


# ini->py
#HTTP_IP                = "172.123.101.253"
#HTTP_PORT              = 9090

# url 			    = http://172.123.101.253:9090/ACS-server/ACS
CPE2ACS_PAGE            = "/ACS-server/ACS"
USER_PAGE               = "/user"   

#AGENT_HTTP_IP          = "172.123.101.253"
#AGENT_HTTP_PORT        = 50000


ACS2AGENT_PAGE          = "/user"   


#  -----------------------------------------------------------    
# if cpe send inform, then cpe is online; if cpe not send inform, and interval time> 86400, then acs send get_url to check cpe is online
CHECK_CPE_ONLINE_TIMEINTERVAL                   = 86400     # seconds
CHECK_ACS_LOGIC_WORKLIST_STATUS_TIMEINTERVAL    = 604800    # seconds, 7 day

WAIT_CPE_SESSION_LOST_TIMEOUT                   = 20

ACS_WAIT_AGENT_WORKLIST_EXEC_RSP_TIMEOUT        = 30
SHORT_CONNECTION_TIMEOUT                        = 30
ACS_WORKLIST_RESERVE_WAIT_EXEC_START_TIMEOUT    = 500
ACS_WAIT_WORKLIST_EXEC_FINISH_TIMEOUT           = 3600

#  -----------------------------------------------------------
ACS2CPE_LOGIN_NAME          = "itms"
ACS2CPE_LOGIN_PASSWORD      = "itms"

CPE2ACS_LOGIN_NAME          = "hgw"
CPE2ACS_LOGIN_PASSWORD      = "hgw"


#  -----------------------------------------------------------
LOGIC_WORKLIST_NO_RPC_NAME  = "WORKLIST_NO_RPC_NAME"    # no case 
LOGIC_WORKLIST_NO_RPC_ID    = "WORKLIST_NO_RPC_ID"
LOGIC_WORKLIST_LIFETIME     = 7                         # days

MONITOR_INFORM_LIFETIME     = 3                         # days


# db
DB_DRIVER                   = "{MySQL ODBC 5.2 Unicode Driver}"
#DB_SERVER                   = "127.0.0.1"
#DB_PORT                     = 3306
#DB_DATABASE                 = "TR069"
#DB_UID                      = "root"
#DB_PWD                      = "root"
DB_CHARSET                  = "utf8"



