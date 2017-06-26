#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: dispathmethodrequest
#  function: DispathMethodRequest,_MethodRequestControlThread
#            
#  Author: ATT development group
#  version: V1.0
#  date: 2013.8.29
#  change log:
#  wangjun  20130829    create
# ***************************************************************************

import time
import threading
import datetime

#user denfine interface
from outputcontrol import ClientResponseHandle
from methodmappingagent import MethodMappingAgent, TR069UserClientCfg

#import log
from constantdefinitions import DEBUG_FLAG
if DEBUG_FLAG:
    from outlog import OutLog as log
else:
    import TR069.lib.common.logs.log  as log
    
    
#处理线程对象
client_request_control_thread_object_list=[]                         #处理线程对象句柄列表
client_request_control_thread_object_list_lock = threading.Lock()    #与处理线程对象句柄列表数据操作权限相关的锁



class DispathMethodRequest():
    
    @staticmethod
    def dispath_method_request_to_control_thread(in_method_data):
        """
        将method分发到空闲的线程去处理
        """
        global client_request_control_thread_object_list
        global client_request_control_thread_object_list_lock
        
        try:
            client_request_control_thread_object_list_lock.acquire()
            thread_object_count=len(client_request_control_thread_object_list)
            client_request_control_thread_object_list_lock.release()
                                    
            if 0 == thread_object_count:#len(client_request_control_thread_object_list):
                
                log.debug_info("New Method Request Control Thread and start run thread")
                               
                #创建新的处理线程，并将消息分发到该线程
                thread_node=_MethodRequestControlThread()
                
                #更新请求处理method相关数据内容
                temp_set_data_suc_flag=DispathMethodRequest.set_method_request_control_thread_management_property_data(thread_node,in_method_data)
                if not temp_set_data_suc_flag:
                    del thread_node
                    return 
                    
                #启动线程，开始处理数据
                thread_node.start()
                
                #保存有效线程对象句柄到处理线程对象句柄列表
                client_request_control_thread_object_list.append(thread_node)

            else:
                
                idle_thread_node_handle=DispathMethodRequest.get_idle_method_request_control_thread_handle()
                if not idle_thread_node_handle:
                    
                    log.debug_info("New Method Request Control Thread and start run thread")
                        
                    #创建新的处理线程，并将消息分发到该线程
                    thread_node=_MethodRequestControlThread()
                    
                    #更新请求处理method相关数据内容
                    temp_set_data_suc_flag=DispathMethodRequest.set_method_request_control_thread_management_property_data(thread_node,in_method_data)
                    if not temp_set_data_suc_flag:
                        del thread_node
                        return
                        
                    #启动线程，开始处理数据
                    thread_node.start()
                    
                    #保存有效线程对象句柄到处理线程对象句柄列表
                    client_request_control_thread_object_list.append(thread_node)
                
                else:
                    
                    log.debug_info("Push Method Request data to idle thread control module")
                        
                    #将消息分发到刚获取的空闲处理线程
                    idle_thread_node_handle.push_request_method_data_to_property(in_method_data)
            
        except Exception, e:
            err_info = "Dispath method request to control thread occurs expection: %s" % e
            log.debug_err(err_info)
            
            #返回错误消息 
            in_conn_handle=in_method_data.get_client_conn_handle()
            ClientResponseHandle.send_error_info_data_to_client(in_conn_handle,err_info)
            
            
    @staticmethod
    def set_method_request_control_thread_management_property_data(in_thread_handle,in_method_data):
        """
        更新请求处理method相关数据内容
        """
        if not in_thread_handle:
            return False
        
        #更新请求处理method相关数据内容
        temp_push_data_suc_flag=in_thread_handle.push_request_method_data_to_property(in_method_data)
        
        #数据处理对象句柄无效，错误处理
        if not temp_push_data_suc_flag:
                        
            err_info = "Dispath method request to control thread fail. Method control object handle is Invalid."
            log.debug_err(err_info)
                        
            #返回错误消息 
            in_conn_handle=in_method_data.get_client_conn_handle()
            ClientResponseHandle.send_error_info_data_to_client(in_conn_handle,err_info)
            return False
            
        return True
    

    @staticmethod
    def get_idle_method_request_control_thread_handle():
        """
        返回返回任一空闲的request处理线程对象句柄
        """
        global client_request_control_thread_object_list
        global client_request_control_thread_object_list_lock

        idle_thread_node_handle=None
        
        client_request_control_thread_object_list_lock.acquire()
        log.debug_info("BUFLIST METHOD THREAD COUNT=%d" % len(client_request_control_thread_object_list))
        
        for thread_node in client_request_control_thread_object_list:
            if thread_node.get_process_idle_flag():
                idle_thread_node_handle=thread_node
                
                break
                
        client_request_control_thread_object_list_lock.release()
        
        return idle_thread_node_handle


    @staticmethod
    def get_method_request_control_thread_total_count():
        """
        返回request处理线程对象总数
        """
        global client_request_control_thread_object_list
        
        log.debug_info("BUFLIST METHOD THREAD COUNT=%d" % len(client_request_control_thread_object_list))
        
        return len(client_request_control_thread_object_list)


    @staticmethod
    def get_method_request_control_thread_idle_count():
        """
        返回空闲的request处理线程对象总数
        """
        global client_request_control_thread_object_list
        global client_request_control_thread_object_list_lock
        
        idle_client_request_control_thread_object_count=0

        client_request_control_thread_object_list_lock.acquire()
        for thread_node in client_request_control_thread_object_list:

            if thread_node.get_process_idle_flag():
                idle_client_request_control_thread_object_count += 1
                
        client_request_control_thread_object_list_lock.release()
        
        log.debug_info("BUFLIST IDLE METHOD THREAD COUNT=%d" % idle_client_request_control_thread_object_count)
        
        
        return idle_client_request_control_thread_object_count


    @staticmethod
    def destroy_client_request_control_thread(in_thread_handle):
        """
        将即将实现的thread对象从处理线程对象句柄列表中清除
        """
        global client_request_control_thread_object_list
        global client_request_control_thread_object_list_lock
        
        client_request_control_thread_object_list_lock.acquire()
        
        if in_thread_handle in client_request_control_thread_object_list:
            client_request_control_thread_object_list.remove(in_thread_handle)
    
        client_request_control_thread_object_list_lock.release() 

    
    
class _MethodRequestControlThread(threading.Thread):
    
    def __init__(self):
        """
        初始化
        """
        threading.Thread.__init__(self)
        
        self._process_idle_flag=True
        self._process_idle_time=None
        self._process_invalid_time_length=60*60
        self._method_data_noe=None
        self._process_method_agent_obj=None
        self.init_process_method_agent_object()


    def init_process_method_agent_object(self):
        """
        初始化method代理对象
        """
        if not self._process_method_agent_obj:
            self._process_method_agent_obj=TR069UserClientCfg.create_tr069_user_client_object()
            self._process_idle_time=datetime.datetime.now()

    
    def get_process_idle_flag(self):
        """
        返程线程是否正在处理method标志
        """
        return self._process_idle_flag
    
    
    def push_request_method_data_to_property(self,in_methond_data):
        """
        将method数据保存到对象数据中
        """
        log.debug_info("METHOD_THREAD_STATUS=%s" % self._process_idle_flag )
        
        if self._process_idle_flag:
            self._process_idle_flag=False
            self._method_data_noe=in_methond_data
            self._process_idle_time=datetime.datetime.now()
            return True
        
        else:
            return False
    
    
    def run(self):
        """
        处理method请求
        """
        
        #退出线程
        if not self._process_method_agent_obj:
            return
        
        while 1:
            
            #线程处于空闲状态
            if not self._process_idle_flag:

                if self._method_data_noe:
                    
                    log.debug_info("Thread running method START" )

                    #读取method名字以及参数数据
                    tmp_client_conn=self._method_data_noe.get_client_conn_handle()
                    tmp_sequence_id=self._method_data_noe.get_request_sequence_id()
                    temp_method_name=self._method_data_noe.get_request_method_name()
                    temp_method_parameters_list=self._method_data_noe.get_request_method_parameters()
                    temp_cpe_id=self._method_data_noe.get_request_cpe_id()
                    
                    #调用方法映射接口执行method对应的方法
                    MethodMappingAgent.mapping_method(self._process_method_agent_obj,
                                                          tmp_client_conn,
                                                          tmp_sequence_id,
                                                          temp_method_name,
                                                          temp_cpe_id,
                                                          temp_method_parameters_list)
                        
                    log.debug_info("Thread running method END" )
                        
                    #还原线程空闲状态以及清空数据节点的值
                    self._process_idle_flag=True
                    self._method_data_noe=None
                    log.debug_info("Reset thread running data info" )
            
            else:
                
                #获取当前系统时间
                current_time_object=datetime.datetime.now()
                #log.debug_info(("current time: %s" % current_time_object.strftime('%Y-%m-%d %H:%M:%S' )) )
                
                #获取线程空闲的时长,当空闲超过60分钟，退出线程，释放系统资源
                difference_seconds=(current_time_object - self._process_idle_time).seconds
                if difference_seconds >= self._process_invalid_time_length:
                            
                    #将即将实现的thread对象从处理线程对象句柄列表中清除
                    DispathMethodRequest.destroy_client_request_control_thread(self)
                    log.debug_info(("Invalid thread, call destroy_client_request_control_thread interface") )
                    break
                
                else:
                    
                    time.sleep(1)
                    continue
            