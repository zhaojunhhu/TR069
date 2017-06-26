#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: httpclient
#  function: send http request to WorkList Server, and relay the response to user
#            
#  Author: ATT development group
#  version: V1.0
#  date: 2012.10.27
#  change log:
#  lana     20121027     created
#  wangjun  20130419     modify WorkList Server server http response data control
#  wangjun  20130715     更新接口里的功能说明
#  wangjun  20130718     优化LOG信息
#  wangjun  20130722     添加更新从Agent发送出去消息的KEY_SEQUENCE属性数据接口
# ***************************************************************************

import httplib2
import threading
import pickle
from cStringIO import StringIO
import time

import TR069.lib.common.logs.log as log
import TR069.lib.common.event as event

import DUTqueue
import DUTqueuemanagement
import constructWLrequesthandle
from responseclient import ResponseClientHandle
import httpclienthandle

#add by wangjun 20130722
from  messageprocessing import MessageProcessing


class HttpClientToWorklistServer(threading.Thread):
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
        
        self.msg = None           # msg be sent to WorkList Server
        self.conn = None          # connection used to send response
        
        self.response = None      # response be received from WorkList Server
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
        
        log_info = ("HttpClientToWorklistServer construct sequence id: %s" % in_sequence_id )
        log.debug_info(log_info)
        
        self.msg= ResponseClientHandle.switch_msg_stream_type_dict2str(new_message)
        
        
    def run(self):
        """
        override run
        """

        #更新从Agent发送出去消息的KEY_SEQUENCE属性 #add by wangjun 20130722
        self.construct_agent_send_message_sequence_property()
        
        # send http request and recv response
        log.app_info("(Request from client %s)Send request(message=%s) to WorkList server's" %(ResponseClientHandle.get_client_ipaddress(self.conn),event.get_event_desc(self.msg_type)))

        res,self.response = httpclienthandle.HttClientHandle.send_http_msg(in_message=self.msg,
                                                          in_timeout=self.timeout,
                                                          in_try_count=3,
                                                          in_url=self.url,
                                                          in_method=self.method)
        
        log.app_info("(Request from client %s)Recv WorkList Server server's response(request message=%s)" %(ResponseClientHandle.get_client_ipaddress(self.conn),event.get_event_desc(self.msg_type)))

        # parse response data
        try:
            if res == "error":
                err_info = "Agent to WorkList server's http client error:" + self.response
                log.debug_err(err_info)
                self.handle_request_except(self.msg,self.conn,err_info)
                return
                    
            elif res == "fail":
                err_info = "Agent to WorkList server's http client fail:" + self.response
                log.debug_err(err_info)
                self.handle_request_except(self.msg,self.conn,err_info)
                return

            elif res == "response":

                #检查消息的完整性
                check_complete_flag=ResponseClientHandle.check_message_complete(self.response)
                if False == check_complete_flag:
                    err_info = "Recv HTTP server's response incomplete"
                    log.debug_info(err_info)
                    self.handle_request_except(self.msg,self.conn,err_info)
                    return
                
                else:
                    self.hanale_worklistserver_response(self.response,self.conn)
                    return
             
        except Exception, e:
            err_info = "Pickle object occurs exception: %s" % e
            log.debug_err(err_info)
            self.handle_request_except(self.msg,self.conn,err_info)
            return


    def set_worklist_execute_request_WLServer_check_response(self,response_type):
        """
        更新数据到发起工单执行的地方，表示工单执行check响应
        """
        if not (event.EV_WORKLIST_EXECUTE_RQST==self.msg_type):
            return
        
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
        log.debug_info("Set Worklist Server's response client request check suc")
        self.dut_obj_handle.set_worklist_execute_request_WLServer_check_response(response_type)


    def hanale_worklistserver_response(self,message,conn):
        """
        check worklist server response data and call continue event
        """
        
        #检查消息的完整性
        tmp_msg_is_complete=ResponseClientHandle.check_message_complete(message)
        if False == tmp_msg_is_complete:
            log.debug_info(message)
            err_info = "Recv WorkList server's response incomplete"
            log.debug_info(err_info)
            self.handle_request_except(self.msg,self.conn,err_info)
            return
        
        else:
            response=ResponseClientHandle.switch_msg_stream_type_str2dict(message)

            msg_group = int(response.get(event.KEY_MESSAGE)) & 0xFF00
            if (msg_group == event.EVENT_WORKLIST_GROUP): 
                
                #检查返回消息与请求消息的匹配关系
                if not self.handle_response_message_type_verify(response.get(event.KEY_MESSAGE)):
                    err_info = "WorkList server's response message type error"
                    log.debug_info(err_info)
                    self.handle_request_except(self.msg,self.conn,err_info)
                    return

                #当请求消息是执行工单时，特殊处理，
                if (event.EV_WORKLIST_EXECUTE_RQST==self.msg_type):
                    
                    #更新工单等待执行状态，表示发起工单成功
                    self.set_worklist_execute_request_WLServer_check_response("request_suc")
                    
                else: #worklist download
                    
                    #其他消息正常处理
                    # send worklist down to user or ACS
                    ResponseClientHandle.handle_send_response(response,conn)
                    
            else:
                err_info = "Unsupport msg event group:%d" % msg_group
                log.debug_info(err_info)
                self.handle_request_except(self.msg,self.conn,err_info)

        return


    def handle_response_message_type_verify(self,response_msg_type):
        """
        检查返回消息与请求消息的匹配关系，在请求消息的基础上，+1默认为成功消息，+2默认为失败消息，其他异常
        """
        # check response message type
        if ((self.msg_type+1) == response_msg_type or
            (self.msg_type+2)== response_msg_type ):
            return True
        
        else:
            return False


    def handle_request_except(self,message,conn,err_info):
        """
        异常处理模块，分工单执行异常或普通消息处理异常
        """
        if (event.EV_WORKLIST_EXECUTE_RQST == self.msg_type):
            DUTqueue.ResponseWLexecHandle.handle_WLexec_request_except(self.msg,err_info)

        else:
            ResponseClientHandle.handle_except(message,conn,err_info)
