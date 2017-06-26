#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: __init__
#  function: start_service
#            
#  Author: ATT development group
#  version: V1.0
#  date: 2013.8.29
#  change log:
#  wangjun  20130829    create
# ***************************************************************************

print "[file=%s] loaded." %__file__

#user denfine interface
from methodagentserver import StartMethodAgentServer
from constantdefinitions import METHOD_AGENT_SERVER_IP, METHOD_AGENT_SERVER_PORT

#import log
from constantdefinitions import DEBUG_FLAG
if DEBUG_FLAG:
    from outlog import OutLog as log
else:
    import TR069.lib.common.logs.log  as log


def start_service():
    """
    启动服务器模块
    """

    try:
        StartMethodAgentServer(METHOD_AGENT_SERVER_IP, METHOD_AGENT_SERVER_PORT)
        
    except Exception, e:
        err_info = "iTest agent service occurs expection: %s" % e
        log.debug_err(err_info)



if __name__ == '__main__':
    start_service()