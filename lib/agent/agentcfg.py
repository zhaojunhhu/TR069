#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: agentcfg
#  function: define global variables used in agent model
#
#  Author: ATT development group
#  version: V1.0
#  date: 2012.10.15
#  change log:
#  lana     20121015     created
#  lana     20121204     get global veriables value from config file
# ***************************************************************************


import TR069.lib.common.config as config
from os.path import dirname, join
import socket

import TR069.lib.common.logs.log as log

# Agent error code
AGENT_ERROR_CODE = 8010


# internal config
AGENT2ACS_WAIT_RPC_REQUEST_CHENCK_TIMEOUT = 510
AGENT2ACS_HTTP_CLIENT_TIMEOUT = 30
AGENT2WL_HTTP_CLIENT_TIMEOUT = 30
AGENT_HTTP_SERVER_PATH="/user"


# config file path
CONFIG_PATH = join(dirname(dirname(dirname(__file__))),"data","agent.cfg")

# get local ip, if read config failed, used this ip addr
try:
    local_ip = socket.gethostbyname(socket.gethostname())
except Exception,e:
    local_ip ="127.0.0.1"

# read config file
def read_config():
    
    ret, ret_data = config.read_cfg(path=CONFIG_PATH, keys = "agent")
    if ret == config.FAIL:
        err_info = "Agent server read config file failed, err info:%s!" % ret_data
        log.debug_err(err_info)
        return {}
        
    return ret_data


dict_cfg = read_config()

if dict_cfg == {}:
    err_info = "Agent server read config file failed,using default values!, \
                \n agent_http_server_ip = '500', \
                \n agent_wait_acs_timeout = '30', \
                \n agent_http_server_ip = %s, \
                \n agent2acs_wait_request_check_timeout = '510', \
                \n agent_http_server_port = 50000, \
                \n agent_http_server_path=/user, \
                \n acs_http_server_url = 'http://%s:18015/user', \
                \n agent_wait_acs_timeout = '30', \
                \n worklist_http_server_url = 'http://%s:40000/user', \
                \n agent_wait_worklist_timeout = '500'" % (local_ip, local_ip, local_ip)
    log.debug_err(err_info)

    # agent
    AGENT_HTTP_SERVER_IP = local_ip
    AGENT_HTTP_SERVER_PORT = 50000
    AGENT_HTTP_SERVER_PATH="/user"
    
    # http connect timeout
    AGENT2ACS_WAIT_RPC_REQUEST_CHENCK_TIMEOUT=510

    # acs
    ACS_HTTP_SERVER_URL = "http://%s:18015/user" % local_ip
    AGENT2ACS_HTTP_CLIENT_TIMEOUT = 30
    
    # worklist
    WL_HTTP_SERVER_URL = "http://%s:40000/user" % local_ip
    AGENT2WL_HTTP_CLIENT_TIMEOUT = 30
    
else:
    #agent init
    if "agent_http_server_ip" in dict_cfg:
        AGENT_HTTP_SERVER_IP = dict_cfg.get("agent_http_server_ip")
    else:
        err_info = "agent.cfg file lose 'agent_http_server_ip',using default value '%s'" % local_ip
        log.debug_err(err_info)
        AGENT_HTTP_SERVER_IP = local_ip
        
    if "agent_http_server_port" in dict_cfg:
        AGENT_HTTP_SERVER_PORT = int(dict_cfg.get("agent_http_server_port"))
    else:
        err_info = "agent.cfg file lose 'agent_http_server_port',using default value '50000'" 
        log.debug_err(err_info)
        AGENT_HTTP_SERVER_PORT = 50000        
               
        
    # acs
    if (("acs_http_server_ip" in dict_cfg) and 
        ("acs_http_server_port" in dict_cfg)):
        ip = dict_cfg.get("acs_http_server_ip")
        port = dict_cfg.get("acs_http_server_port")
        ACS_HTTP_SERVER_URL = "http://%s:%s/user" %(ip, port)
    else:
        err_info = "agent.cfg file lose 'acs_http_server_url',using default value 'http://%s:18015/user'" % local_ip
        log.debug_err(err_info)
        ACS_HTTP_SERVER_URL = "http://%s:18015/user" % local_ip        
        
    # worklist
    if (("worklist_http_server_ip" in dict_cfg) and 
        ("worklist_http_server_port" in dict_cfg) ):
        ip = dict_cfg.get("worklist_http_server_ip")
        port = dict_cfg.get("worklist_http_server_port")
        WL_HTTP_SERVER_URL = "http://%s:%s/user" % (ip, port)
    else:
        err_info = "agent.cfg file lose 'worklist_http_server_url',using default value 'http://%s:40000/user'" % local_ip
        log.debug_err(err_info)
        WL_HTTP_SERVER_URL = "http://%s:40000/user" % local_ip                 
        