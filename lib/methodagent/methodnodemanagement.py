#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: methodnodemanagement
#  function: MethodNodeManagement,_MethodNodeManagementControlThread
#            
#  Author: ATT development group
#  version: V1.0
#  date: 2013.8.29
#  change log:
#  wangjun  20130829    create
# ***************************************************************************

import time
import threading

#user denfine interface
from outputcontrol import ClientResponseHandle
from dispathmethodrequest import DispathMethodRequest

#可开启的最大线程数，当处理对象的线程数大于这个数字时，消息在缓存队列中，等待空闲线程，然后处理。
from constantdefinitions import OPEN_CONTROL_THREAD_MAX_COUNT

#import log
from constantdefinitions import DEBUG_FLAG
if DEBUG_FLAG:
    from outlog import OutLog as log
else:
    import TR069.lib.common.logs.log  as log
    

#客户端消息节点缓存队列
client_request_node_list=[]                                 #客户端消息节点缓存队列
client_request_node_list_lock = threading.Lock()            #与客户端消息节点缓存队列数据操作权限相关的锁
client_request_node_list_management_thread_handle=None      #客户端消息节点缓存队列管理线程



class MethodNodeManagement():

    @staticmethod
    def _start_client_request_node_list_management_thread():
        global client_request_node_list_management_thread_handle
        
        if not client_request_node_list_management_thread_handle:
            client_request_node_list_management_thread_handle=_MethodNodeManagementControlThread()
            client_request_node_list_management_thread_handle.start()


    @staticmethod
    def push_client_request_node_to_wait_run_buffer_list(in_request_node):
        """
        将消息节点加入到客户端消息节点缓存队列
        """
        global client_request_node_list
        global client_request_node_list_lock
            
        #启动客户端消息节点缓存队列管理线程
        MethodNodeManagement._start_client_request_node_list_management_thread()
        
        #将请求节点插入到客户端消息节点缓存队列
        client_request_node_list_lock.acquire()
        if in_request_node not in client_request_node_list: 
            client_request_node_list.append(in_request_node)
            log.debug_info("push_client_request_node_to_wait_run_buffer_list SUC")
        else:
            log.debug_info("push_client_request_node_to_wait_run_buffer_list FAIL. Node is exist.")
            return False
        
        client_request_node_list_lock.release()
        
        #下发消息到处理线程接口
        #当有空闲处理线程时，将请求直接下放，否则将请求加入一个列表，当检测到有空闲处理线程时，再下放。
        return MethodNodeManagement._dispath_top_request()
    
    
    @staticmethod
    def _dispath_top_request():
        """
        下发消息到处理线程接口
        """
        try:
            
            #获取存在的request处理线程对象总数
            temp_request_control_thread_total_count=DispathMethodRequest.get_method_request_control_thread_total_count()
            
            #获取空闲的request处理线程对象总数，当有处理线程空闲时，直接下发消息节点
            temp_request_control_thread_idle_count=DispathMethodRequest.get_method_request_control_thread_idle_count()
    
            #存在空闲的request处理线程对象，直接下发消息节点
            if temp_request_control_thread_idle_count>0:
                
                log.debug_info("Dispath client request to idle control thread")
                        
                #获取客户端消息节点缓存队列最前面的消息节点
                client_request_node=MethodNodeManagement.\
                                            pop_client_request_node_from_wait_run_buffer_list()
                
                if not client_request_node:
                    
                    log.debug_info("BUFLIST: Not exist waiting method request")
                    return False

                #存在空闲的request处理线程对象，直接下发消息节点到该对象
                DispathMethodRequest.dispath_method_request_to_control_thread(client_request_node)
                return True
            
            elif temp_request_control_thread_total_count<OPEN_CONTROL_THREAD_MAX_COUNT:
                
                log.debug_info("Create new thread and dispath messages to the object")
                
                #获取客户端消息节点缓存队列最前面的消息节点
                client_request_node=MethodNodeManagement.\
                                            pop_client_request_node_from_wait_run_buffer_list()
                
                if not client_request_node:
                    
                    log.debug_info("BUFLIST: Not exist waiting method request")
                    return False
                
                #request线程对象都处于忙状态或者不存在request线程对象,创建新的处理线程节点并直接下发消息节点到该对象
                DispathMethodRequest.dispath_method_request_to_control_thread(client_request_node)
                
                return True
        
        except Exception, e:
            err_info = "Dispath client request to idle control thread occurs expection: %s" % e
            log.debug_err(err_info)
                
            #返回错误消息 
            in_conn_handle=client_request_node.get_client_conn_handle()
            ClientResponseHandle.send_error_info_data_to_client(in_conn_handle,err_info)

        return False
    
        
    @staticmethod
    def get_client_request_node_wait_run_buffer_list_count():
        global client_request_node_list
        return len(client_request_node_list)


    @staticmethod
    def pop_client_request_node_from_wait_run_buffer_list():
        """
        从客户端消息节点缓存队列中取出第0个节点
        """
        global client_request_node_list
        global client_request_node_list_lock
        
        client_request_node=None
        
        client_request_node_list_lock.acquire()
        if len(client_request_node_list):
            client_request_node=client_request_node_list.pop(0)
            log.debug_info("pop_client_request_node_from_wait_run_buffer_list SUC")
            
        client_request_node_list_lock.release()
        
        return client_request_node
    


class _MethodNodeManagementControlThread(threading.Thread):
    """
    处理method请求
    """

    def __init__(self):
        """
        初始化
        """
        threading.Thread.__init__(self)


    def run(self):
        """
        处理method请求
        """
        while 1:
            
            #获取客户端消息节点缓存队列中元素个数
            wait_buffer_list_count=MethodNodeManagement.get_client_request_node_wait_run_buffer_list_count()
            #log.debug_info( "BUF_METHOD_COUNT=%d" % wait_buffer_list_count)
            
            #当存在等待执行的节点时，将队列头的消息节点分发下去
            if wait_buffer_list_count>0:
                    
                #下发消息到处理线程接口
                rc_flag=MethodNodeManagement._dispath_top_request()
                    
                if not rc_flag:
                    time.sleep(1)
    
            else:
                #客户端消息节点缓存队列为空，间隔性闲置线程资源
                time.sleep(1)
        

