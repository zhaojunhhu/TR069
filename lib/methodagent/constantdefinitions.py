#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: constantdefinitions
#  function: 
#            
#  Author: ATT development group
#  version: V1.0
#  date: 2013.8.29
#  change log:
#  wangjun  20130829    create
# ***************************************************************************

import os
import sys
import TR069.lib.common.logs.log as log
import TR069.lib.common.config as config

dirname = os.path.dirname
# 2014-06-25; data split
CONFIG_PATH = os.path.join(dirname(dirname(dirname(__file__))), "data", "methodagent.cfg")

def read_config():
    ret, ret_data = config.read_cfg(path=CONFIG_PATH, keys = "methodagent")
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
    METHOD_AGENT_SERVER_IP          = str(dict_cfg.get("METHOD_AGENT_SERVER_IP"))
    METHOD_AGENT_SERVER_PORT        = int(dict_cfg.get("METHOD_AGENT_SERVER_PORT"))
    
except Exception,e:    
    desc = "fail:%s" %(e)
    log.debug_err(desc)
    raise Exception(desc)


#服务器处于DEBUG模式
DEBUG_FLAG=False


#服务器接收数据相关常量定义
#-----------------------------------
#每次接收BUF的最大长度
MAX_ONE_RECV_BUF_LENGTH = 1024

#服务器每次并发监听的最大连接数据
MAX_LISTEM_CONNECT_NUMBER=100

#接收数据超时的时间长度
RECV_TIMEOUT_LENGTH=1

#消息长度和消息体数据分割符合
MESSAGE_TOTAL_LENGTH_DATA_SPLIT_STRING="########" 
#-----------------------------------


#并发处理线程管理
#-----------------------------------
#可开启的最大线程数，当处理对象的线程数大于这个数字时，消息在缓存队列中，等待空闲线程，然后处理。
OPEN_CONTROL_THREAD_MAX_COUNT=20
#-----------------------------------


#XML相关常量定义
#-----------------------------------
#XML数据加密标志
XML_VALUE_DECODE_FALG=True

#打印XML解析中间数据过程标志
OPEN_XML_PROCESS_LOG=True
#-----------------------------------


#TR069相关常量定义
#-----------------------------------
#调用TR069 user client相关常量定义
TR069_SWITCH_CPE_METHOD_NAME="switch_cpe"

#-----------------------------------       


#心跳包数据常量定义
#-----------------------------------
CLIETN2SERVER_KEEPALIVE_DATA="keepalive?"
SERVER2CLIETN_KEEPALIVE_DATA="keepalive"

CLIETN2SERVER_KEEPALIVE_INVALID_TIME_LENGTH=60*3
#-----------------------------------