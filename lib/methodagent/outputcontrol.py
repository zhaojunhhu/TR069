#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: outputcontrol
#  function: ClientConnectCount,ClientResponseHandle
#            
#  Author: ATT development group
#  version: V1.0
#  date: 2013.8.29
#  change log:
#  wangjun  20130829    create
# ***************************************************************************

import time
import socket
import threading
import copy

#import log
from constantdefinitions import DEBUG_FLAG
if DEBUG_FLAG:
    from outlog import OutLog as log
else:
    import TR069.lib.common.logs.log  as log
    
g_tcp_client_count=0                           #客户端连接句柄总数
g_tcp_client_count_lock = threading.Lock()     #与客户端连接句柄数据操作权限相关的锁


class ClientConnectCount():
    
    @staticmethod
    def get_tcp_client_count():
        
        global g_tcp_client_count
        return g_tcp_client_count
    
    @staticmethod
    def updata_tcp_client_count_value(in_conn_increase_flag):
        
        global g_tcp_client_count
        global g_tcp_client_count_lock

        g_tcp_client_count_lock.acquire()
    
        if in_conn_increase_flag:
            g_tcp_client_count = g_tcp_client_count + 1
        else:
            if g_tcp_client_count>0:
                g_tcp_client_count = g_tcp_client_count - 1
                
        g_tcp_client_count_lock.release()
        


class ClientResponseHandle():
    
    RESPONSE_STATUS_SUC=0
    RESPONSE_STATUS_FAILE=-1
    
    @staticmethod
    def write_keepalive_data_to_client(in_conn_handle,in_response_data):
        """
        通过Client连接句柄发送心跳响应到连接客户端
        """  

        #写心跳包数据
        if in_conn_handle:

            try:
                #in_conn_handle.send(str(in_response_data))
                log.debug_info("write_keepalive_data_to_client SUC")

                return True
            
            except Exception, e:
                err_info = "write_keepalive_data_to_client occurs expection: %s" % e
                log.debug_err(err_info)
                log.debug_info("write_keepalive_data_to_client FAIL")
                
                return False
            
        else:

            log.debug_err("write_keepalive_data_to_client in_conn_handle is None")
            return False


    @staticmethod
    def write_data_to_client(in_conn_handle,in_response_data):
        """
        通过Client连接句柄发送响应数据到连接客户端
        """  
        global g_tcp_client_count
        global g_tcp_client_count_lock

        #写数据
        if in_conn_handle:

            #检查当前系统中有效的连接接句柄总数
            log.debug_err("Client connected handle count number=%d" % ClientConnectCount.get_tcp_client_count())
            
            if 0 == ClientConnectCount.get_tcp_client_count():
                in_conn_handle=None
                log.debug_info("write_data_to_client FAIL")
                return False
        
            try:
                in_conn_handle.send(str(in_response_data))
                in_conn_handle.close()
                log.debug_info("write_data_to_client SUC")

                return True
            
            except Exception, e:
                err_info = "write_data_to_client occurs expection: %s" % e
                log.debug_err(err_info)
                log.debug_info("write_data_to_client FAIL")
                
                return False
            
            finally:
                
                #更新连接接句柄总数，send一次，接接句柄总数减一
                if ClientConnectCount.get_tcp_client_count() > 0:
                    ClientConnectCount.updata_tcp_client_count_value(False)
                    log.debug_err("Client connected handle count number=%d" % ClientConnectCount.get_tcp_client_count())
        else:
            
            log.debug_err("write_data_to_client in_conn_handle is None")
            return False


    @staticmethod
    def send_response_data_to_client(in_conn_handle,in_response_data):
        """
        给Client回响应数据已更新消息处理状态
        """
        try:
            #发送响应到当前保存Client句柄
            rc=ClientResponseHandle.write_data_to_client(in_conn_handle,in_response_data)
            
            #保存消息处理结果已经消息处理状态
            from methodsequencemanagement import MethodSequenceManagement
            MethodSequenceManagement.finish_method_sequence_obj(in_conn_handle, in_response_data, rc)
            
            log.debug_info("send_response_data_to_client SUC")
            
        except Exception, e:
            err_info = "send_response_data_to_client occurs expection: %s" % e
            log.debug_err(err_info)
            log.debug_info("send_response_data_to_client FAIL")
    
    
    @staticmethod
    def send_error_info_data_to_client(in_conn_handle,in_error_info):
        """
        构造错误信息并将错误返回给Client
        """
        try:
            #获取消息message_id 
            from methodsequencemanagement import MethodSequenceManagement
            in_sequence_id=MethodSequenceManagement.get_method_connect_handle_link_object_sequence_id_property(in_conn_handle)
            if None == in_sequence_id:
                in_sequence_id=0
            
            #构建返回XML数据
            from dataprocess import ConstructResponseData
            out_data=ConstructResponseData.construct_response_data(in_sequence_id,
                                                                   ClientResponseHandle.RESPONSE_STATUS_FAILE,
                                                                   in_error_info)
        except Exception, e:
            err_info = "Construct response message data occurs expection: %s" % e
            log.debug_err(err_info)
            log.debug_info("send_error_info_data_to_client FAIL")
            return
        
        ClientResponseHandle.send_response_data_to_client(in_conn_handle,out_data)
            