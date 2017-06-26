#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: DUTQueue
#  function: deal with queue message
#  Author: ATT development group
#  version: V1.0
#  date: 2013.4.15
#  change log:
#  wangjun  20130415     create
#  wangjun  20130715     更新接口里的功能说明
#  wangjun  20130718     优化LOG信息
#  wangjun  20130722     删除DUTQueue类中send_event接口中更新从Agent发送出去消息的KEY_SEQUENCE属性数据接口，
#                        因为在这个地方无法拦截所有以Agent为客户端发送给ACS Server/Worklist Server的消息请求。
# ***************************************************************************

from time import sleep
import threading
import pickle
from cStringIO import StringIO
import agentcfg
import httpclienttoacs
import httpclienttoworklist

import DUTqueuemanagement
import constructWLrequesthandle
from responseclient import ResponseClientHandle
import copy

import TR069.lib.common.logs.log as log
import TR069.lib.common.event as event


# max idle time: one hour
MAX_IDLE_TIME = 3600


WAIT_RPC_RESPONSE_POST_FALG=True


class DUTQueueEventCtrlThread(threading.Thread):
    """
    subclassing threading, used to handle request in DUT's event queue
    """
    
    def __init__(self, dut_obj, dut_queue_type):
        """
        initial 
        """
        threading.Thread.__init__(self)
        
        self.dut_obj = dut_obj
        self.dut_queue_type = dut_queue_type
        
    def run(self):
        """
        override run
        """
        self.dut_obj.process_event(self.dut_queue_type)
        log.debug_err("stop thread name=%s" % self.getName())



class DUTQueue(object):
    """
    """
    DUTQUEUE_SUC = 0
    DUTQUEUE_FAIL = -1

    def __init__(self,dut_id):
        
        self.dut_id = dut_id                           # DUTQueue object id
        
        #init queue expire default property
        self.DUT_QUEUE_MODULE_TYPE_QUERY = 0
        self.DUT_QUEUE_MODULE_TYPE_REQUEST = 1
    
        #add by wangjun 20130522
        self.DUT_QUEUE_MODULE_TYPE_WL_REQUEST = 2
        
        self.dict_queue_expire_property={}
        self.init_queue_expire_property()

        #define queue item
        self.query_queue=[]                          # CPE query/configure and Worklist build/bind queue
        self.query_queue_lock=threading.Lock()       # used to lock query_queue

        self.request_queue_priority_normal=[]        # CPE RPC and Worklist start queue
        self.request_queue_priority_high=[]
        self.request_queue_lock=threading.Lock()     # used to lock request_queue

        self.cur_handle_request=[]                   # current handling request
        
        #add by wangjun 20130522
        self.WLrpc_queue=[]                          # Worklist rpc request queue
        self.WLrpc_queue_lock=threading.Lock()       # used to lock WLrpc_queue
        
        #add by 20130530
        #self.wait_WLexec_worklist_process_response_flag=False            #wait exec worklist response flag
        
        self.WLexec_request_node_message=None
        self.request_WLexec_worklist_suc_flag=False  
        
        self.wait_request_response_timeout_length=int(agentcfg.AGENT2ACS_WAIT_RPC_REQUEST_CHENCK_TIMEOUT)   #wait exec worklist response timeout length
        self.check_WLexec_status_totalcount=0

        #add by wangjun 20130603
        self.request_rpc_suc_flag=False
        self.rpc_request_node_message=None
        self.check_RPC_status_totalcount=0
        
        
    def init_queue_expire_property(self):
        """
        初始化消息队列处理线程是否有效状态标志
        """
        self.dict_queue_expire_property[self.DUT_QUEUE_MODULE_TYPE_QUERY]=-1
        self.dict_queue_expire_property[self.DUT_QUEUE_MODULE_TYPE_REQUEST]=-1
        
        #add by wangjun 20130522
        self.dict_queue_expire_property[self.DUT_QUEUE_MODULE_TYPE_WL_REQUEST]=-1
        
        return
        

    def get_dut_expire_property(self):
        """
        获取消息队列处理线程是否有效状态标志
        """
        tmp_expire_property=True
            
        expire_property_list = self.dict_queue_expire_property.keys()
        for tmp_expire in expire_property_list:
            if 0 == tmp_expire:
                tmp_expire_property=False
                break;
        
        return tmp_expire_property

    
    def intercept_client_worklist_execute_post(self,msg_type,request):
        """
        当接收到client请求执行工单消息，立即回工单check消息给client,后续工单的执行状态，由client自己负责查询
        """
        if msg_type == event.EV_WORKLIST_EXECUTE_RQST:
            log.debug_info("Agent response client exec worklist request event")
            
            #init data
            message=request[0]
            conn=request[1]
            tmp_WLexec_request_msg=message.copy()
                
            #response user exec worklist request event
            ResponseClientHandle.handle_response_client_WLexec_request(tmp_WLexec_request_msg,conn)
                
            #clear client connected handle
            request[1]=None
            
        return
    

    def handle_response_message_type_verify(self,request_msg_type,response_msg_type):
        """
        检查返回消息与请求消息的匹配关系，在请求消息的基础上，+1默认为成功消息，+2默认为失败消息，其他异常
        """
        # check response message type
        if ((request_msg_type+1) == response_msg_type or
            (request_msg_type+2)== response_msg_type ):
            
            return True
        else:
            return False


    def dispath_event(self,msg_type,msg_priority_level,request,msg_key_sender):
        """
        分发消息总入口
        """
        log.debug_info("(Request from client %s)DUTQueue dispath event key_sender=%s" %(ResponseClientHandle.get_client_ipaddress(request[1]),msg_key_sender))
        tmp_intercept_flag=False

        if (event.KEY_SENDER_USER==msg_key_sender or
            event.KEY_SENDER_AGENT==msg_key_sender):
            
            #处理AGENT自己构建的消息 #add by wangjun 20130717
            if event.KEY_SENDER_AGENT==msg_key_sender:
                msg_key_sender=event.KEY_SENDER_USER
                
            tmp_intercept_flag=self.handle_event_user2agent(msg_type,msg_priority_level,request,msg_key_sender)
        
        elif (event.KEY_SENDER_ACS==msg_key_sender):
            tmp_intercept_flag=self.handle_event_acsserver2agent(msg_type,msg_priority_level,request,msg_key_sender)
        
        elif (event.KEY_SENDER_WORKLIST==msg_key_sender):
            tmp_intercept_flag=self.handle_event_worklistserver2agent(msg_type,msg_priority_level,request,msg_key_sender)

        else:
            log.debug_info("(Request from client %s)DUTQueue dispath event error,unsupport message key_sender" % ResponseClientHandle.get_client_ipaddress(request[1]))
            
        if not tmp_intercept_flag:
            err_info = "DUTQueue dispath event error"
            log.debug_err(err_info)
            message=request[0]
            conn=request[1]
            ResponseClientHandle.handle_except(message,conn, err_info)
            
    
    
    def handle_event_user2agent(self,msg_type,msg_priority_level,request,msg_key_sender):
        """
        分发从USER端来的消息
        """
        if not (event.KEY_SENDER_USER==msg_key_sender):
            return False
    
        #特殊处理EV_RPC_GETRPCMETHODS_RQST方法
        #当有工单正在执行时，将该方法插入到工单RPC队列，等待马上执行
        #当无工单正在执行时，将该方法加入到RPC HIGH队列，优先执行
        if msg_type == event.EV_RPC_GETRPCMETHODS_RQST:
            
            if self.WLexec_request_node_message:
                log.debug_info("(Request from client %s)Insert EV_RPC_GETRPCMETHODS_RQST msg to worklist running rpc queue" % ResponseClientHandle.get_client_ipaddress(request[1]) )
                #dispath event to WLrpc_queue
                self.dispath_event_to_WLrpc(msg_type,request)
                return True
            
            else:
                #up request KEY_PRIORITY_LEVEL value
                request[0][event.KEY_PRIORITY_LEVEL]=event.PRIORITY_HIGH
                msg_priority_level=event.PRIORITY_HIGH

        #特殊处理从USER端来的请求执行工单消息
        elif msg_type == event.EV_WORKLIST_EXECUTE_RQST:
            log.debug_info("(Request from client %s)Agent response user exec worklist request event" % ResponseClientHandle.get_client_ipaddress(request[1]))
            self.intercept_client_worklist_execute_post(msg_type,request)
            
        else:
            pass
        
        #将消息分发到具体的消息队列query_queue or request_queue
        self.dispath_event_to_normal(msg_type,msg_priority_level,request)
        
        return True


    def handle_event_acsserver2agent(self,msg_type,msg_priority_level,request,msg_key_sender):
        """
        分发从ACS端来的消息,消息来源分为执行逻辑工单和RPC方法响应。
        """
        if not (event.KEY_SENDER_ACS==msg_key_sender):
            return False
        
        msg_group = int(msg_type) & 0xFF00
        if (msg_group == event.EVENT_WORKLIST_GROUP):
            
            #特殊处理从ACS端来的请求执行工单消息
            if msg_type == event.EV_WORKLIST_EXECUTE_RQST:
                log.debug_info("(Request from client %s)Agent response ACS's exec worklist request event" % ResponseClientHandle.get_client_ipaddress(request[1]) )
                
                self.intercept_client_worklist_execute_post(msg_type,request)
                
                #dispath event to query_queue or request_queue
                self.dispath_event_to_normal(msg_type,msg_priority_level,request)
            
            else:
                return False

        elif (msg_group == event.EVENT_RPC_GROUP):
            
            #特殊处理从ACS端来的RPC响应消息
            if not WAIT_RPC_RESPONSE_POST_FALG:
                return True
            
            #[step-1]
            message=request[0]
            conn=request[1]
            if not self.rpc_request_node_message:
                log.debug_err("(Request from client %s)DUTQueue not found running rpc request" % ResponseClientHandle.get_client_ipaddress(request[1]) )

                dict_ret = {}
                dict_ret['str_result'] = "DUTQueue not found running rpc request"
                dict_ret['dict_data'] = {}

                ResponseClientHandle.handle_send_rpc_check_toACS_request_reponse(message,conn,True,dict_ret)
                return True
            
            #防止RPC线程在服务器返回信息以后，由于处理时间差仍然超时的问题。
            #add by wangjun 20130627
            self.reset_check_rpc_status_totalcount()
            log.debug_err("Reset check_RPC_status_totalcount=%d" % self.check_RPC_status_totalcount )
            
            #[step-2]
            # check response from ACS server's(client rpc request)
            tmp_request_msg_type=self.rpc_request_node_message[0].get(event.KEY_MESSAGE)
            log.debug_info("(Request from client %s)ACS server's rpc response RPC request(message=%s)" % (ResponseClientHandle.get_client_ipaddress(request[1]),event.get_event_desc(tmp_request_msg_type)))
            
            #[step-3]
            if not self.handle_response_message_type_verify(tmp_request_msg_type,msg_type):
                #[step-3-1]
                # send response to user or ACS and reset self.rpc_request_node_message value
                self.handle_close_wait_rpc_response_control()
                
                #[step-3-2]
                # send resoponse rpc check message to ACS
                dict_ret = {}
                dict_ret['str_result'] = "ACS server's rpc response message type error"
                dict_ret['dict_data'] = {}
            
                ResponseClientHandle.handle_send_rpc_check_toACS_request_reponse(message,conn,True,dict_ret)
                log.debug_info("(Request from client %s)ACS server's rpc response message fail" % ResponseClientHandle.get_client_ipaddress(request[1]))
                
            else:
                #[step-3-1]
                # send response to user or ACS and reset self.rpc_request_node_message value
                self.handle_close_wait_rpc_response_control(response_suc_flag=True,response_message=message)
                
                #[step-3-2]
                # send resoponse rpc check message to ACS
                ResponseClientHandle.handle_send_rpc_check_toACS_request_reponse(message,conn)
                log.debug_info("(Request from client %s)ACS server's rpc response message suc" % ResponseClientHandle.get_client_ipaddress(request[1]))

        else:
            log.app_info("(Request from client %s)ACS server's query or configure response message suc" % ResponseClientHandle.get_client_ipaddress(request[1]))
            return False

        return True


    def handle_close_wait_rpc_response_control(self,response_suc_flag=False,response_message=None):
        """
        关闭等待PRC执行结果控制，根据ACS返回结果进程处理，并将消息发送回RPC请求端
        """
        if not self.rpc_request_node_message:
            return
        
        #[step-0]
        tmp_request_msg=self.rpc_request_node_message[0]
        tmp_request_client_conn=self.rpc_request_node_message[1]
            
        #[step-1]
        if (True == response_suc_flag and
            None != response_message):
            # send rpc response message to client
            ResponseClientHandle.handle_send_response(response_message,tmp_request_client_conn)
            log.debug_info("Agent send rpc response suc to client")
            
        else:
            # send rpc except message to client
            err_info = "ACS server's rpc response message type error"
            log.debug_err(err_info)
            ResponseClientHandle.handle_except(tmp_request_msg,tmp_request_client_conn, err_info)
            log.debug_info("Agent send rpc response error to client")

        #[step-2]
        #reset self.rpc_request_node_message value
        self.rpc_request_node_message=None
        
        
    def handle_event_worklistserver2agent(self,msg_type,msg_priority_level,request,msg_key_sender):
        """
        分发从WorklistServer端来的消息，主要分为RPC请求和执行工单消息响应。
        """
        if not (event.KEY_SENDER_WORKLIST==msg_key_sender):
            return False
        
        msg_group = int(msg_type) & 0xFF00
        if (msg_group == event.EVENT_RPC_GROUP):
            
            #工单过程中的RPC方法，将它分发到 WLrpc_queue
            self.dispath_event_to_WLrpc(msg_type,request)
                
        elif (msg_group == event.EVENT_WORKLIST_GROUP):
            
            #工单执行的消息响应，工单执行结果
            # intercept worklist server response worklist execute data
            if msg_type == event.EV_WORKLIST_EXECUTE_RSP_RQST:

                #防止工单执行线程在服务器返回信息以后，由于处理时间差仍然超时的问题。
                #add by wangjun 20130627
                self.reset_check_WLexec_status_totalcount()
                log.debug_info("Reset check_WLexec_status_totalcount=%d" % self.check_WLexec_status_totalcount )

                #[step-1] response EV_WORKLIST_EXECUTE_RSP_PSP to worklist server
                message=request[0]
                conn=request[1]
                ResponseClientHandle.handle_response_worklistserver_WLexec_response_post(message,conn)

                #[step-2] response EV_WORKLIST_EXECUTE_PSP to acs server
                if not self.WLexec_request_node_message:
                    err_info="DUTQueue not found running worklist request" 
                    log.debug_err(err_info)
                    ResponseWLexecHandle.handle_WLexec_request_except(message,err_info)
                    return True

                # set worklist exec response to ACS
                ResponseWLexecHandle.handle_WLexec_finish_request(self.WLexec_request_node_message[0],message,conn)
                
                #[step-3]
                #reset self.WLexec_request_node_message value
                self.WLexec_request_node_message=None
                    
            else:
                log.debug_err("DUTQueue not found event type request" )
                return False
                
        else:
            return False

        return True 

    def dispath_event_to_WLrpc(self,msg_type,request):
        """
        将工单RPC方法加入到WLrpc_queue队列
        """
        # dispatch
        try:
            if not self.WLexec_request_node_message:
                log.debug_err("DUTQueue not found running worklist request." )

            self.reset_check_WLexec_status_totalcount()
            log.debug_info("Reset check_WLexec_status_totalcount=%d" % self.check_WLexec_status_totalcount )
            
            self.join_WLrpc_event_queue(request)

        except Exception,e:
            err_info = "DUTQueue dispath_event_to_WLrpc function occurs exception:%s" % e
            log.debug_err(err_info)
            message=request[0]
            conn=request[1]
            ResponseClientHandle.handle_except(message,conn, err_info)

        return

    
    def dispath_event_to_normal(self,msg_type,msg_priority_level,request):
        """
        将消息分发到默认的处理队列query_queue或request_queue
        """
        # dispatch
        try: 
            msg_group = int(msg_type) & 0xFF00
            
            if (msg_group == event.EVENT_QUERY_GROUP or
                msg_group == event.EVENT_CONFIGURE_GROUP ):
                
                self.join_query_event_queue(msg_priority_level,request)

            elif (msg_group == event.EVENT_RPC_GROUP):
                
                self.join_request_event_queue(msg_priority_level,request)

            elif (msg_group == event.EVENT_WORKLIST_GROUP):

                #特殊处理工单消息，进入agent自己构建的工单执行逻辑模块。reserve->start->execute->finish
                if msg_type == event.EV_WORKLIST_EXECUTE_RQST:
                    
                    #进入工单预约流程
                    log.debug_info("msg_type == event.EV_WORKLIST_RESERVE_RQST")
                    ResponseWLexecHandle.handle_WLreserve_request(request)

                elif msg_type == event.EV_WORKLIST_EXEC_START_RQST:
                    
                    #进入工单开始流程，这里开始加入RPC队列等待执行。
                    log.debug_info("msg_type == event.EV_WORKLIST_EXEC_START_RQST")
                    self.join_request_event_queue(msg_priority_level,request)
                    
                else:
                    # /********************************************************
                    #msg_type is:
                    # event.EV_WORKLIST_BUILD_RQST or
                    # event.EV_WORKLIST_BIND_PHISIC_RQST or
                    # event.EV_WORKLIST_BIND_LOGIC_RQST or
                    # event.EV_WORKLIST_RESERVE_RQST or
                    # event.EV_WORKLIST_EXEC_FINISH_RQST
                    # event.EV_WORKLIST_DOWNLOAD_RQST
                    # event.EV_WORKLIST_QUERY_RQST
                    # *********************************************************
                    
                    self.join_query_event_queue(msg_priority_level,request)

            else:
                err_info = "DUTQueue dispath_event_to_normal: user message group(=%d) not support." %msg_group
                log.debug_err(err_info)
                message=request[0]
                conn=request[1]
                ResponseClientHandle.handle_except(message,conn, err_info)
            
        except Exception,e:
            err_info = "DUTQueue dispath_event_to_normal function occurs exception:%s" % e
            log.debug_err(err_info)
            message=request[0]
            conn=request[1]
            ResponseClientHandle.handle_except(message,conn, err_info)
        
        return 
                
                        
    def start_queue_event_ctrl_thread(self, queue_type,request):
        """
        状态消息队列处理线程
        """
        if queue_type in self.dict_queue_expire_property:
            tmp_expire=self.dict_queue_expire_property[queue_type]
            
            if -1 == tmp_expire or 1 == tmp_expire:
                # changed queue expire property value
                self.dict_queue_expire_property[queue_type]=0
                
                # create one thread to call queue event control thread
                tmp_queue_event_ctr_thread = DUTQueueEventCtrlThread(self,queue_type)
                
                tmp_thread_name="tname_"
                tmp_thread_name+=str(queue_type)
                tmp_queue_event_ctr_thread.setName(tmp_thread_name)
                log.debug_err("new thread name=%s" % tmp_thread_name)
                
                # start queue event control thread
                tmp_queue_event_ctr_thread.start()
            else:
                pass
            
        else:
            err_info = "DUTQueue queue_type(=%d) not found!" %queue_type
            log.debug_err(err_info)
            message=request[0]
            conn=request[1]
            ResponseClientHandle.handle_except(message,conn, err_info)
            return DUTQueue.DUTQUEUE_FAIL
        
        return DUTQueue.DUTQUEUE_SUC
    
            
    def join_query_event_queue(self,msg_priority_level,request):
        """
        将消息加入到查询队列，如果消息的优先级高，则放入队列头
        """
        log.debug_err("join_query_event_queue")
        
        # start dut queue event ctrl thread
        rc=self.start_queue_event_ctrl_thread(self.DUT_QUEUE_MODULE_TYPE_QUERY,request)
        if DUTQueue.DUTQUEUE_FAIL==rc:
            return rc
        
        # get lock to update self.qurey_queue
        self.query_queue_lock.acquire()
        
        if msg_priority_level==event.PRIORITY_HIGH:
            self.query_queue.insert(0, request)
        else:
            # msg_priority_level default value:event.PRIORITY_DEFAULT
            self.query_queue.append(request)
            
        self.query_queue_lock.release()
        
        return DUTQueue.DUTQUEUE_SUC


    def join_request_event_queue(self,msg_priority_level,request):
        """
        将消息加入到请求队列，如果消息的优先级高，则将消息加入到HIGH队列，该队列会优先执行
        """
        log.debug_err("join_request_event_queue")
        
        # start dut request event ctrl thread
        rc=self.start_queue_event_ctrl_thread(self.DUT_QUEUE_MODULE_TYPE_REQUEST,request)
        if DUTQueue.DUTQUEUE_FAIL==rc:
            return rc
        
        # get lock to update self.request_queue
        self.request_queue_lock.acquire()
                    
        if msg_priority_level==event.PRIORITY_HIGH:
            self.request_queue_priority_high.append(request)
        else:
            # msg_priority_level default value:event.PRIORITY_DEFAULT
            self.request_queue_priority_normal.append(request)
            
        self.request_queue_lock.release()    
        
        return DUTQueue.DUTQUEUE_SUC
    

    #add by wangjun 20130522
    def join_WLrpc_event_queue(self,request):
        """
        将消息加入到工单RPC队列，该队列是用来处理执行工单过程中，工单的RPC请求。
        """
        log.debug_err("join_WLrpc_event_queue")
        
        # start dut queue event ctrl thread
        rc=self.start_queue_event_ctrl_thread(self.DUT_QUEUE_MODULE_TYPE_WL_REQUEST,request)
        if DUTQueue.DUTQUEUE_FAIL==rc:
            return rc
        
        # get lock to update self.qurey_queue
        self.WLrpc_queue_lock.acquire()
        self.WLrpc_queue.append(request)
        self.WLrpc_queue_lock.release()
        
        return DUTQueue.DUTQUEUE_SUC
    
    
    def process_event(self,queue_type):
        """
        队列消息处理线程回调接口，这里根据队列类型完成了不同消息队列消息节点的处理。
        """
        log.debug_err("process_event start, queue type=(%d)." % queue_type)
        
        # used to counter how long there is no request send to current DUTQueue
        counter = 0
        
        # check queue expire property and loop read queue message request
        while (0==self.get_queue_expire_property(queue_type)):
            
            request_node=None
            
            # get queue header node
            if self.DUT_QUEUE_MODULE_TYPE_QUERY == queue_type:
                request_node=self.get_query_event_queue_header_node()
                
            elif self.DUT_QUEUE_MODULE_TYPE_REQUEST==queue_type:
                request_node=self.get_request_event_queue_header_node()

            #add by wangjun 20120522
            elif self.DUT_QUEUE_MODULE_TYPE_WL_REQUEST==queue_type:
                request_node=self.get_WLrpc_event_queue_header_node()
                
            else:
                request_node=None
            
            if None==request_node:
                # when self.request_queue is [], set self.cur_handle_request to []
                if self.DUT_QUEUE_MODULE_TYPE_REQUEST==queue_type:
                    self.cur_handle_request = []

                counter += 1     # when there is no request , counter add 1
                # if current dut don't have request in max idle time , set expire to 1
                if counter >= (MAX_IDLE_TIME/2):
                    self.set_queue_expire_property(queue_type,1)

                else:
                    sleep(2)
                    
                continue
            else:
                counter = 0
                
                if self.DUT_QUEUE_MODULE_TYPE_REQUEST==queue_type:
                    self.cur_handle_request = request_node
                    
                message = request_node[0]
                conn = request_node[1]
                self.send_event(queue_type,message,conn)
        
        
        log.debug_err("process_event exit, queue type=(%d)." % queue_type)

    
    def get_queue_expire_property(self,queue_type):
        """
        获取消息队列对应的线程状态标志
        """
        tmp_expire_property=-1
        
        if self.DUT_QUEUE_MODULE_TYPE_QUERY == queue_type:
            tmp_expire_property=self.dict_queue_expire_property[self.DUT_QUEUE_MODULE_TYPE_QUERY]

        elif self.DUT_QUEUE_MODULE_TYPE_REQUEST==queue_type:
            tmp_expire_property=self.dict_queue_expire_property[self.DUT_QUEUE_MODULE_TYPE_REQUEST]
           
        #add by wangjun 20130522
        elif self.DUT_QUEUE_MODULE_TYPE_WL_REQUEST==queue_type:
            tmp_expire_property=self.dict_queue_expire_property[self.DUT_QUEUE_MODULE_TYPE_WL_REQUEST]
            
        else:
            pass
        
        return tmp_expire_property

        
    def set_queue_expire_property(self,queue_type,expire_property):
        """
        设置消息队列对应的线程状态标志
        """
        if self.DUT_QUEUE_MODULE_TYPE_QUERY == queue_type:
            self.dict_queue_expire_property[self.DUT_QUEUE_MODULE_TYPE_QUERY]=expire_property

        elif self.DUT_QUEUE_MODULE_TYPE_REQUEST==queue_type:
            self.dict_queue_expire_property[self.DUT_QUEUE_MODULE_TYPE_REQUEST]=expire_property
        
        #add by wangjun 201305200
        elif self.DUT_QUEUE_MODULE_TYPE_WL_REQUEST==queue_type:
            self.dict_queue_expire_property[self.DUT_QUEUE_MODULE_TYPE_WL_REQUEST]=expire_property
            
        else:
            return -1
        

    def get_query_event_queue_header_node(self):
        """
        获取查询消息队列消息节点
        """
        if self.query_queue != []:
            # handle request start from query_queue header
            # get lock to update self.query_queue
            self.query_queue_lock.acquire()
            request = self.query_queue.pop(0)
            self.query_queue_lock.release()
            
            return request
        
        return None


    def get_request_event_queue_header_node(self):
        """
        获取RPC请求消息队列消息节点
        """

        if self.request_queue_priority_high != []:
            # handle request start from request_queue_priority_high header
            # get lock to update self.request_queue
            self.request_queue_lock.acquire()
            request = self.request_queue_priority_high.pop(0)
            self.request_queue_lock.release()
            
            return request
            
        elif self.request_queue_priority_normal != []:
            # handle request start from request_queue_priority_normal header
            # get lock to update self.request_queue
            self.request_queue_lock.acquire()
            request = self.request_queue_priority_normal.pop(0)
            self.request_queue_lock.release()
            
            return request
        
        return None


    def get_WLrpc_event_queue_header_node(self):
        """
        获取工单RPC消息队列消息节点
        """
        if self.WLrpc_queue != []:
            # handle request start from WLrpc_queue header
            # get lock to update self.WLrpc_queue
            self.WLrpc_queue_lock.acquire()
            request = self.WLrpc_queue.pop(0)
            self.WLrpc_queue_lock.release()
            
            return request
        
        return None


    def send_event(self,queue_type,message,conn):
        """
        处理消息请求，并将消息分发到具体的功能服务器。
        """
        
        err_info = ("(Request from client %s)DUTQueue send_event message(%s)" % (ResponseClientHandle.get_client_ipaddress(conn),event.get_event_desc(message.get(event.KEY_MESSAGE)) ) )
        log.debug_info(err_info)
        
        #查询消息队列查询消息节点
        if self.DUT_QUEUE_MODULE_TYPE_QUERY == queue_type:

            msg_type=message.get(event.KEY_MESSAGE)
            
            if msg_type == event.EV_WORKLIST_DOWNLOAD_RQST:
                RequestClientHandle.send_event_to_WLserver(self,message,conn)
                
            elif msg_type == event.EV_WORKLIST_EXEC_FINISH_RQST:
                RequestClientHandle.send_event_to_acsserver(self,message,conn,True)
                
            else:
                RequestClientHandle.send_event_to_acsserver(self,message,conn)
        
        #请求消息队列消息节点   
        elif self.DUT_QUEUE_MODULE_TYPE_REQUEST==queue_type:
            
            if not WAIT_RPC_RESPONSE_POST_FALG:
                RequestClientHandle.send_event_to_acsserver(self,message,conn,True)
                
            else:
                msg_group = int(message.get(event.KEY_MESSAGE)) & 0xFF00
                if msg_group == event.EVENT_RPC_GROUP:
                    self.send_event_rpc_methond(message,conn)
                else:
                    RequestClientHandle.send_event_to_acsserver(self,message,conn,True)

        #工单RPC消息队列消息节点
        elif self.DUT_QUEUE_MODULE_TYPE_WL_REQUEST==queue_type:
            
            if not WAIT_RPC_RESPONSE_POST_FALG:
                RequestClientHandle.send_event_to_acsserver(self,message,conn,True)
            else:
                self.send_event_rpc_methond(message,conn)
        else:
            pass
        
        return


    #rpc request process contrl
    def reset_check_rpc_status_totalcount(self):
        self.check_RPC_status_totalcount=(int)(self.wait_request_response_timeout_length/10)
        
        
    def set_rpc_request_ACSServer_check_response(self,response_type):
        if "request_suc" == response_type:
            self.request_rpc_suc_flag=True


    def send_event_rpc_methond(self,message,conn):
        """
        发送RPC消息请求到ACS
        """
        # reset flag to default value
        self.request_rpc_suc_flag=False
        self.rpc_request_node_message=[message,conn]

        log.debug_err("send_event_rpc_methond")
        
        # send rpc request to ACS Server
        RequestClientHandle.send_event_to_acsserver(self,message,conn,True)

        # check send http request response
        if False == self.request_rpc_suc_flag:
            log.app_info("(Request from client %s)ACS server's http request response except" % ResponseClientHandle.get_client_ipaddress(conn))
        
        else:
            log.app_info("(Request from client %s)Begin wait ACS server's rpc response data." % ResponseClientHandle.get_client_ipaddress(conn))
            
            self.check_RPC_status_totalcount=int(self.wait_request_response_timeout_length/10)
            
            while self.rpc_request_node_message and self.check_RPC_status_totalcount > 0 :
                self.check_RPC_status_totalcount -=1
                log.debug_err("self.check_RPC_status_totalcount=%d" % self.check_RPC_status_totalcount)
                sleep(10)
            
            if 0 == self.check_RPC_status_totalcount:
                err_info = ("(Request from client %s)Wait ACS server's rpc event response timeout" % ResponseClientHandle.get_client_ipaddress(conn))
                log.debug_err(err_info)

                ResponseClientHandle.handle_except(message,conn,err_info)
                
                #send rpc request timeout to ACS Server #add by wangjun 20130624
                tmp_rpc_timeout_message=self.build_rpc_request_timeout_message(message)
                RequestClientHandle.send_event_to_acsserver(None,tmp_rpc_timeout_message,None,True)
                
            log.app_info("(Request from client %s)End wait ACS server's rpc response data." % ResponseClientHandle.get_client_ipaddress(conn))
            
        #reset self.rpc_request_node_message value
        self.rpc_request_node_message=None


    # add by wangjun 20130624
    def build_rpc_request_timeout_message(self,request_message):
        """
        构建等待RPC响应超时消息
        """
        new_message=copy.deepcopy(request_message)
        msg=ResponseClientHandle.switch_msg_stream_type_str2dict(new_message)

        #new MsgRpcTimeout object
        msg_cpe_sn=msg.get(event.KEY_SN)
        
        #delete by wangjun 20130627
        #msg_event=msg.get(event.KEY_MESSAGE)
        
        #add by wangjun 20130627
        tmp_obj = msg.get(event.KEY_OBJECT)
        strio = StringIO(tmp_obj)
        msg_user_rpc_obj = pickle.load(strio)
        
        #changed by wangjun 20130627
        new_msg_timeout_obj=event.MsgRpcTimeout(msg_cpe_sn,msg_user_rpc_obj)
        
        #up new message type and event
        msg[event.KEY_MESSAGE_TYPE]=event.EVENT_RPC_GROUP
        msg[event.KEY_MESSAGE] = event.EV_RPC_AGENT_TIMEOUT_POST
        msg[event.KEY_SENDER]=event.KEY_SENDER_AGENT
        
        #up new message key object
        strio = StringIO()
        pickle.dump(new_msg_timeout_obj, strio)
        msg[event.KEY_OBJECT] = strio.getvalue()
        
        return msg


    #worklist execute process contrl
    def reset_check_WLexec_status_totalcount(self):
        self.check_WLexec_status_totalcount=(int)(self.wait_request_response_timeout_length//10)


    def set_worklist_execute_request_WLServer_check_response(self,response_type):
        if "request_suc" == response_type:
            self.request_WLexec_worklist_suc_flag=True


    def send_worklist_execute_event_to_WLserver(self,dut_handle,message,conn):
        """
        发送执行工单消息请求到Worklist Server
        """
        # reset flag to default value
        self.WLexec_request_node_message=[message,conn]
        self.request_WLexec_worklist_suc_flag=False
        
        # send worklist execture request to worklist Server
        RequestClientHandle.send_event_to_WLserver(dut_handle,message,conn,True)

        # check send http request response
        if False == self.request_WLexec_worklist_suc_flag:
            log.app_info("(Request from client %s)WorkList server's http request response except." % ResponseClientHandle.get_client_ipaddress(conn))
        
        else:
            log.app_info("(Request from client %s)Begin wait WorkList server's execute worklist response data." % ResponseClientHandle.get_client_ipaddress(conn))
            
            self.reset_check_WLexec_status_totalcount()
            
            while (self.WLexec_request_node_message and
                  self.check_WLexec_status_totalcount > 0 ):
                    
                self.check_WLexec_status_totalcount -=1
                log.debug_err("self.check_WLexec_status_totalcount=%d" % self.check_WLexec_status_totalcount)
                sleep(10)
            
            if 0 == self.check_WLexec_status_totalcount:
                err_info = ("(Request from client %s)Wait WorkList server's exec worklist event response timeout" % ResponseClientHandle.get_client_ipaddress(conn))
                log.debug_err(err_info)
                ResponseWLexecHandle.handle_WLexec_request_except(message,err_info)
        
            log.app_info("(Request from client %s)End wait WorkList server's execute worklist response data." % ResponseClientHandle.get_client_ipaddress(conn))
            
        #reset self.WLexec_request_node_message value
        self.WLexec_request_node_message=None


class ResponseWLexecHandle(object):
    
    @staticmethod
    def handle_WLreserve_request(request):
        """
        构建工单预约消息，并分发到DUTQueue对象
        """
        log.debug_err("handle_WLreserve_request start")
        
        message=request[0]
        conn=request[1]
        
        # construct worklist reseve request
        tmp_WLreserve_msg=constructWLrequesthandle.ConstructWLRequestHandle.construct_WLreserve_request(message)
        if None==tmp_WLreserve_msg:
            err_info = "DUTQueue construct WLreserve request fail."
            log.debug_err(err_info)
            ResponseClientHandle.handle_except(message,conn,err_info)
        else:
            try:
                #dispath message to queue object
                tmp_dict_msg=ResponseClientHandle.switch_msg_stream_type_str2dict(tmp_WLreserve_msg)
                DUTqueuemanagement.DUTQueueManagement.insert_dut_obj([tmp_dict_msg, conn])
                
            except Exception, e:
                err_info = "DUTQueueManagement dispath request event occurs exception:%s" % e
                log.debug_err(err_info)
                ResponseClientHandle.handle_except(message,conn, err_info)


    @staticmethod
    def handle_WLexec_start_request(request_event_msg,message,conn):
        """
        构建工单开始消息，并分发到DUTQueue对象，加入到request_queue队列排队，等待处理
        """
        log.debug_err("handle_WLexec_start_request start")

        # construct worklist execute start request
        tmp_WLexecutestart_msg=constructWLrequesthandle.ConstructWLRequestHandle.construct_WLexec_start_request(message)
        if None==tmp_WLexecutestart_msg:
            err_info = "Construct WLexecute start request fail."
            log.debug_err(err_info)
            ResponseClientHandle.handle_except(request_event_msg,conn,err_info)
            return
            
        else:
            try:
                #dispath worklist exectrue start request to queue object
                tmp_dict_msg=ResponseClientHandle.switch_msg_stream_type_str2dict(tmp_WLexecutestart_msg)
                DUTqueuemanagement.DUTQueueManagement.insert_dut_obj([tmp_dict_msg, conn])
                
            except Exception, e:
                err_info = "DUTQueueManagement dispath request event occurs exception:%s" % e
                log.debug_err(err_info)
                ResponseClientHandle.handle_except(request_event_msg, conn, err_info)
              
                
    @staticmethod
    def handle_WLexec_request(dut_handle,request_event_msg,message,conn):
        """
        构建工单执行消息，并将消息发送到Worklist Server
        """
        log.debug_err("handle_WLexec_request start")
        
        # construct worklist execute request
        tmp_WLexecute_msg=constructWLrequesthandle.ConstructWLRequestHandle.construct_WLexec_request(message)
        if None==tmp_WLexecute_msg:
            err_info = "Construct WLexecute request fail."
            log.debug_err(err_info)
            ResponseClientHandle.handle_except(request_event_msg,conn,err_info)
            return
        
        else:
            # send worklist execture request to worklist Server
            if not dut_handle:
                err_info = "dut_handle is None."
                log.debug_err(err_info)
                ResponseClientHandle.handle_except(request_event_msg,conn,err_info)
                return

            if not (isinstance(dut_handle, DUTQueue)):
                err_info = "dut_handle instance not DUTQueue object."
                log.debug_err(err_info)
                ResponseClientHandle.handle_except(request_event_msg,conn,err_info)
                return

            dut_handle.send_worklist_execute_event_to_WLserver(dut_handle,tmp_WLexecute_msg,conn)
            
        return
    
    
    @staticmethod
    def handle_WLexec_finish_request(WLexec_r_message,message,conn): #request_event_msg
        """
        构建工单执行结果消息
        """
        # construct worklist execute start request
        tmp_WLexecutefinish_msg=constructWLrequesthandle.ConstructWLRequestHandle.construct_WLexec_finish_request(message)
        #log.debug_err(tmp_WLexecutefinish_msg)
        
        if not tmp_WLexecutefinish_msg:
            err_info = "Construct WLexecute finish request fail."
            log.debug_err(err_info)
            ResponseWLexecHandle.handle_WLexec_request_except(WLexec_r_message,err_info)
            
        else:
            tmp_dict_msg=ResponseClientHandle.switch_msg_stream_type_str2dict(tmp_WLexecutefinish_msg)
            DUTqueuemanagement.DUTQueueManagement.insert_dut_obj([tmp_dict_msg, conn])


    @staticmethod
    def get_WLexec_worklist_sn(WL_event_message):
        """
        获取工单SN
        """
        tmp_message=(ResponseClientHandle.switch_msg_stream_type_str2dict(WL_event_message))
        
        tmp_wl_obj = tmp_message.get(event.KEY_OBJECT)
        strio = StringIO(tmp_wl_obj)
        tmp_msg_key_obj = pickle.load(strio)
        
        if (isinstance(tmp_msg_key_obj, event.MsgWorklistBuild)):
            return None
        
        tmp_key_sn=None
        if (isinstance(tmp_msg_key_obj, event.MsgWorklist)):
            
            tmp_key_sn=tmp_message.get(event.KEY_SN)
            if not tmp_key_sn:
                tmp_key_sn=tmp_msg_key_obj.sn
            
            if tmp_key_sn:
                log.debug_err(tmp_key_sn)
            else:
                log.debug_err("Not found worklist sn data")
                
            return tmp_key_sn
        
        else:
            log.debug_err("Not found worklist sn data")
        
        return tmp_key_sn
        
        
    @staticmethod
    def get_WLexec_worklist_id(WL_event_message):
        """
        获取工单ID或SN
        """
        
        """
        MSG_WL_DATA_STRUCT_LIST=[event.MsgWorklist,
                                 event.MsgWorklistBuild,
                                 event.MsgWorklistBindPhysical,
                                 event.MsgWorklistBindLogical,
                                 event.MsgWorklistExecute,
                                 event.MsgWorklistExecStart,
                                 event.MsgWorklistExecRsp,
                                 event.MsgWorklistExecFinish,
                                 event.MsgWorklistReserve,
                                 event.MsgWorklistQuery]
        """
        
        tmp_message=(ResponseClientHandle.switch_msg_stream_type_str2dict(WL_event_message))
        
        tmp_wl_obj = tmp_message.get(event.KEY_OBJECT)
        strio = StringIO(tmp_wl_obj)
        tmp_msg_key_obj = pickle.load(strio)
        
        #print tmp_msg_key_obj
        #print event.MsgWorklist
        
        tmp_wl_id=None
        if (isinstance(tmp_msg_key_obj, event.MsgWorklist)):
            tmp_wl_id=tmp_msg_key_obj.id_
            if tmp_wl_id:
                log.debug_err(tmp_wl_id)
            else:
                log.debug_err("Not found worklist id data") 
        else:
            log.debug_err("Not found worklist id data")
        
        return tmp_wl_id

    
    @staticmethod
    def handle_WLexec_request_except(WLexec_r_message,except_info):
        """
        执行工单异常处理
        """
        if not WLexec_r_message:
            err_info = "WLexec request message is None."
            return
        
        tmp_worklistid=ResponseWLexecHandle.get_WLexec_worklist_id(WLexec_r_message)
        if None==tmp_worklistid:
            return
        
        tmp_dict_ret = {}
        tmp_dict_ret['str_result'] = except_info
        tmp_dict_ret['dict_data'] = {"FaultCode":agentcfg.AGENT_ERROR_CODE,"FaultString":"Agent error"}

        tmp_WLexecute_except_msg=constructWLrequesthandle.ConstructWLRequestHandle.construct_WLexec_request_except(tmp_worklistid,tmp_dict_ret)
        log.debug_err(tmp_WLexecute_except_msg)
        if None==tmp_WLexecute_except_msg:
            err_info = "Construct WLexecute request except fail."
            log.debug_err(err_info)

        else:
            try:
                #log.debug_err(tmp_WLexecute_except_msg)
                    
                #dispath worklist exectrue finish request to queue object
                tmp_dict_msg=ResponseClientHandle.switch_msg_stream_type_str2dict(tmp_WLexecute_except_msg)
                DUTqueuemanagement.DUTQueueManagement.insert_dut_obj([tmp_dict_msg, None])
                
            except Exception,e:
                err_info = "DUTQueueManagement dispath request event occurs exception:%s" % e
                log.debug_err(err_info)



class RequestClientHandle(object):
    """
    HTTP分发消息接口
    """
    
    @staticmethod   
    def send_event_to_acsserver(dut_obj_handle,message,conn,block=False):
        """
        used to send http request to ACS Server
        """

        try:
            thread_i = httpclienttoacs.HttpClientToACS(dut_handle=dut_obj_handle,
                                                    url=agentcfg.ACS_HTTP_SERVER_URL,
                                                    timeout=agentcfg.AGENT2ACS_HTTP_CLIENT_TIMEOUT)
            thread_i.msg = ResponseClientHandle.switch_msg_stream_type_dict2str(message)
            thread_i.msg_type=(ResponseClientHandle.switch_msg_stream_type_str2dict(message)).get(event.KEY_MESSAGE)
            thread_i.conn = conn
            thread_i.start()
            
            if True==block:
                thread_i.join()
            
        except Exception, e:
            err_info = ("(Request from client %s)Start http client to ACS's occurs exception:%s" % (ResponseClientHandle.get_client_ipaddress(conn), e))
            log.debug_err(err_info)
            ResponseClientHandle.handle_except(message,conn, err_info)


    @staticmethod  
    def send_event_to_WLserver(dut_obj_handle,message,conn,block=True):
        """
        used to send tcp request to Worklist Server
        """

        try:
            thread_i = httpclienttoworklist.HttpClientToWorklistServer(dut_handle=dut_obj_handle,
                                                    url=agentcfg.WL_HTTP_SERVER_URL,
                                                    timeout=agentcfg.AGENT2WL_HTTP_CLIENT_TIMEOUT)

            thread_i.msg = ResponseClientHandle.switch_msg_stream_type_dict2str(message)
            thread_i.msg_type=(ResponseClientHandle.switch_msg_stream_type_str2dict(message)).get(event.KEY_MESSAGE)
            thread_i.conn = conn
            thread_i.start()
            
            if True==block:
                thread_i.join()
            
        except Exception, e:
            err_info = ("(Request from client %s)Start http client to WorkList's occurs exception:%s" % (ResponseClientHandle.get_client_ipaddress(conn), e))
            log.debug_err(err_info)
            ResponseClientHandle.handle_except(message, conn, err_info)
