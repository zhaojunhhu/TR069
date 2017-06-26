#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: httpclient
#  function: send http request to ACS, and relay the response to user
#            
#  Author: ATT development group
#  version: V1.0
#  date: 2012.10.27
#  change log:
#  lana     20121027     created
#  wangjun  20130419     modify ACS server http response data control
#  wangjun  20130715     更新接口里的功能说明
#  wangjun  20130718     优化LOG信息
#  wangjun  20130722     添加更新从Agent发送出去消息的KEY_SEQUENCE属性数据接口
# ***************************************************************************

import httplib2
import threading
import pickle
from cStringIO import StringIO
import time


import DUTqueue
import DUTqueuemanagement
import constructWLrequesthandle
from responseclient import ResponseClientHandle
import httpclienthandle

import TR069.lib.common.logs.log as log
import TR069.lib.common.event as event

#add by wangjun 20130722
from  messageprocessing import MessageProcessing


class HttpClientToACS(threading.Thread):
    """
    subclassing threading, used to send http request
    """
    
    def __init__(self, dut_handle, url="127.0.0.1", timeout=300):
        """
        initial 
        """
        threading.Thread.__init__(self)
        
        self.url = url            # http server url
        self.method = "POST"      # http method
        self.timeout = timeout    # http request timeout
        
        self.msg = None           # msg be sent to ACS Server
        self.conn = None          # connection used to send response
        
        self.response = None      # response be received from ACS Server
        self.msg_type = None      # msg type
        
        self.dut_obj_handle=dut_handle #save DUTQueue object handle


    def construct_agent_send_message_sequence_property(self):
        """
        更新从Agent发送出去消息的KEY_SEQUENCE属性
        """
        new_message = ResponseClientHandle.switch_msg_stream_type_str2dict(self.msg)
        
        #生成sequence_id
        in_sequence_id=MessageProcessing.construct_sequence_id(event.KEY_SENDER_AGENT)
        
        #更新sequence属性数据
        new_message[event.KEY_SEQUENCE] = in_sequence_id
        
        log_info = ("HttpClientToACS construct sequence id: %s" % in_sequence_id )
        log.debug_info(log_info)
        
        self.msg= ResponseClientHandle.switch_msg_stream_type_dict2str(new_message)
    
    
    def run(self):
        """
        override run
        """
        
        #更新从Agent发送出去消息的KEY_SEQUENCE属性 #add by wangjun 20130722
        self.construct_agent_send_message_sequence_property()
        
        # send http request and recv response
        log.app_info("(Request from client %s)Send request(message=%s) to ACS server's" %(ResponseClientHandle.get_client_ipaddress(self.conn),event.get_event_desc(self.msg_type)))

        res,self.response = httpclienthandle.HttClientHandle.send_http_msg(in_message=self.msg,
                                                          in_timeout=self.timeout,
                                                          in_try_count=3,
                                                          in_url=self.url,
                                                          in_method=self.method)
        
        log.app_info("(Request from client %s)Recv ACS server's response(request message=%s)" %(ResponseClientHandle.get_client_ipaddress(self.conn),event.get_event_desc(self.msg_type)))

        # parse response data
        try:
            if res == "error":
                err_info = "Agent to ACS server's http client error:" + self.response
                log.debug_err(err_info)
                ResponseClientHandle.handle_except(self.msg,self.conn,err_info)
                return
                    
            elif res == "fail":
                err_info = "Agent to ACS server's http client fail:" + self.response
                log.debug_err(err_info)
                ResponseClientHandle.handle_except(self.msg,self.conn,err_info)
                return

            elif res == "response":
                
                #检查消息的完整性
                check_complete_flag=ResponseClientHandle.check_message_complete(self.response)
                if False == check_complete_flag:
                    err_info = "Recv HTTP server's response incomplete"
                    log.debug_info(err_info)
                    ResponseClientHandle.handle_except(self.msg,self.conn,err_info)
                    return
                
                else:
                    
                    #处理响应消息
                    #log.debug_info(self.response)
                    self.handle_acsserver_response(self.response,self.conn)
                    
                    return
                
        except Exception, e:
            err_info = "Pickle object occurs exception: %s" % e
            log.debug_err(err_info)
            ResponseClientHandle.handle_except(self.msg,self.conn,err_info)
            return
                

    def handle_acsserver_response(self,message,conn):
        """
        check acs server response data and call continue event
        """
        response=ResponseClientHandle.switch_msg_stream_type_str2dict(message)
        
        msg_type=response.get(event.KEY_MESSAGE)
        msg_group = int(msg_type) & 0xFF00
        
        #特殊处理AGENT 构建的给ACS的TIMOUT消息响应
        if self.msg_type ==  event.EV_RPC_AGENT_TIMEOUT_POST:
            if msg_type == event.EV_RPC_AGENT_TIMEOUT_RSP:
                log.debug_info("ACS server's response check agent timeout rpc request suc")
            else:
                log.debug_info("ACS server's response check agent timeout rpc request fail")
                
            return
        
        #检查消息的合法性
        #response message type error
        if not self.handle_response_message_type_verify(msg_group,msg_type,response):
            #check EV_RPC_CHECK_FAIL response
            if (msg_type==event.EV_RPC_CHECK_FAIL):

                tmp_obj = response.get(event.KEY_OBJECT)
                strio = StringIO(tmp_obj)
                tmp_msg_key_obj = pickle.load(strio)
            
                if not (isinstance(tmp_msg_key_obj,event.MsgUserRpcCheck)):
                    err_info = "ACS server's rpc response message type error"
                    log.debug_info(err_info)

                else:
                    tmp_response_dict_ret=tmp_msg_key_obj.dict_ret
                    if "str_result" in tmp_response_dict_ret:
                        rc_str_result = tmp_response_dict_ret.get("str_result")
                        err_info = "ACS server's rpc response check message fail, str_result: " + rc_str_result
                        log.debug_info(err_info)
                        
                    else:
                        err_info = "ACS server's rpc response message not found dict_ret data"
                        log.debug_info(err_info)
                        
            else:
                err_info = "ACS server's rpc response message type error"
                log.debug_info(err_info)
            
            ResponseClientHandle.handle_except(self.msg,self.conn,err_info)
            return
        
        #response rpc post
        if (msg_group == event.EVENT_QUERY_GROUP or
            msg_group == event.EVENT_CONFIGURE_GROUP ): 
            
            # send response to user or ACS
            ResponseClientHandle.handle_send_response(response,conn)
            
        elif (msg_group == event.EVENT_RPC_GROUP):
            
            if not DUTqueue.WAIT_RPC_RESPONSE_POST_FALG:
                # send response to user or ACS
                ResponseClientHandle.handle_send_response(response,conn)
            else:
                self.set_rpc_request_ACSServer_check_response("request_suc")
        
        #response worklist build/bind/reserve/start/finish info post
        elif (msg_group == event.EVENT_WORKLIST_GROUP):

            self.handle_ACS_worklist_info_response(response,conn)
            
        else:
            err_info = "Unsupport msg event group:%d" % msg_group
            log.debug_info(err_info)
            ResponseClientHandle.handle_except(self.msg,self.conn,err_info)

    
    def handle_ACS_worklist_info_response(self,message,conn):
        """
        check acs server response worklist info data and call continue event
        """
        response=ResponseClientHandle.switch_msg_stream_type_str2dict(message)
        
        msg_type=response.get(event.KEY_MESSAGE)
        msg_group = int(msg_type) & 0xFF00
        
        if (msg_group == event.EVENT_WORKLIST_GROUP):
            
            # check worklist reseve response
            if(msg_type == event.EV_WORKLIST_RESERVE_RSP):
                log.debug_info("ACS server's response worklist reserve suc")

                # call worklist execute start request   
                DUTqueue.ResponseWLexecHandle.handle_WLexec_start_request(self.msg,response,None)
                
            elif(msg_type == event.EV_WORKLIST_RESERVE_FAIL):
                log.debug_info("ACS server's response worklist reserve fail")

                ResponseClientHandle.handle_send_response(response,conn)
             
            # check worklist start response   
            elif(msg_type == event.EV_WORKLIST_EXEC_START_RSP):
                log.debug_info("ACS server's response worklist execute start suc")
                
                # call worklist execute request
                DUTqueue.ResponseWLexecHandle.handle_WLexec_request(self.dut_obj_handle,self.msg,response,conn)

            elif(msg_type == event.EV_WORKLIST_EXEC_START_FAIL):
                log.debug_info("ACS server's response worklist execute start fail")
                
                ResponseClientHandle.handle_send_response(response,conn)

            # check worklist finish response   
            elif(msg_type == event.EV_WORKLIST_EXEC_FINISH_RSP):
                log.debug_info("ACS server's response worklist execute finish suc")

            elif(msg_type == event.EV_WORKLIST_EXEC_FINISH_FAIL):
                log.debug_info("ACS server's response worklist execute finish fail")
            
            # check worklist build/bind/download response
            else:
                ResponseClientHandle.handle_send_response(response,conn)
                
        else:
            err_info = "Unsupport msg event group:%d" % msg_group
            log.debug_info(err_info)
            ResponseClientHandle.handle_except(self.msg,self.conn,err_info)


    def set_rpc_request_ACSServer_check_response(self,response_type):

        if not self.dut_obj_handle:
            err_info = "dut_handle is None."
            log.debug_err(err_info)
            self.handle_request_except(self.msg,self.conn,err_info)
            return

        if not (isinstance(self.dut_obj_handle, DUTqueue.DUTQueue)):
            err_info = "dut_handle instance not DUTQueue object."
            log.debug_err(err_info)
            self.handle_request_except(self.msg,self.conn,err_info)
            return
    
        #send exec worklist event to WLserver response
        log.debug_info("Set ACS Server's response client request check suc")
        self.dut_obj_handle.set_rpc_request_ACSServer_check_response(response_type)


    def handle_response_message_type_verify(self,msg_group,response_msg_type,message):
        """
        """
        # check response message type
        if (msg_group == event.EVENT_RPC_GROUP):
            
            if not DUTqueue.WAIT_RPC_RESPONSE_POST_FALG:
                if ((self.msg_type+1) == response_msg_type or
                    (self.msg_type+2)== response_msg_type ):
                    return True
            
                else:
                    return False
            
            tmp_obj = message.get(event.KEY_OBJECT)
            strio = StringIO(tmp_obj)
            tmp_msg_key_obj = pickle.load(strio)
            
            if not (isinstance(tmp_msg_key_obj,event.MsgUserRpcCheck)):
                return False
            
            tmp_event_request=tmp_msg_key_obj.event_rqst

            #log.debug_info(response_msg_type)
            log.debug_info("request message=%s" % event.get_event_desc(self.msg_type))
            log.debug_info("response message=%s" % event.get_event_desc(tmp_event_request))

            if (response_msg_type==event.EV_RPC_CHECK_RSP):
                if (self.msg_type == tmp_event_request):
                        return True
                else:
                    return False
            
            elif (response_msg_type==event.EV_RPC_CHECK_FAIL):
                return False
                
            else:
                return False

        elif (msg_group == event.EVENT_QUERY_GROUP or
              msg_group == event.EVENT_CONFIGURE_GROUP or 
              msg_group == event.EVENT_WORKLIST_GROUP):
            
            if ((self.msg_type+1) == response_msg_type or
                (self.msg_type+2)== response_msg_type ):
                return True
            
            else:
                return False
            
        return False
    
    