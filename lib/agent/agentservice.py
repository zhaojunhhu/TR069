#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: agentservice
#  function: start agentservice
#            
#  Author: ATT development group
#  version: V1.0
#  date: 2012.10.29
#  change log:
#  lana     20121029    created
#  wangjun  20130529    changed: 切换TCP服务器到HTTP服务器模式
# ***************************************************************************

import agenthttpserver
import TR069.lib.common.logs.log as log
import TR069.lib.common.event as event

def start_service():
    """
    start service of useragent
    """
    
    log.debug_info("Start agent service...")

    # start SocketServer to wait for client connection
    try:
        ss_obj = agenthttpserver.start_http_server()
        
    except Exception, e:
        err_info = "Agent service occurs expection: %s" % e
        log.debug_err(err_info)
    
    
if __name__ == '__main__':
    
    start_service()