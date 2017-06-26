#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: DUTQueue
#  function: create agent send response to client function
#  Author: ATT development group
#  version: V1.0
#  date: 2012.4.15
#  change log:
#  wangjun  20130415     create
#  wangjun  20130716     添加发送消息出去的时候将消息更新到MessageSequence对象中处理
#  wangjun  20130718     优化LOG信息
# ***************************************************************************

import threading
from time import sleep
import agentcfg
import pickle
from cStringIO import StringIO
import copy

from twisted.internet import reactor, threads
from twisted.internet.defer import Deferred, DeferredList, succeed
from twisted.web import http
from twisted.web.http import Request
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.web.server import NOT_DONE_YET

import TR069.lib.common.logs.log as log
import TR069.lib.common.event as event


# Agent http connnect count
g_http_client_count=0

#add by wangjun 20130716
from  messagesequencemanagement import MessageSequenceManagement


class connHandle(object):
    
    @staticmethod    
    def http_respose_write(conn, msg):
        """
        通过conn连接句柄将消息返回给client
        """

        global g_http_client_count
        
        #检查当前系统中有效的连接接句柄总数
        if 0 == g_http_client_count:
            log.debug_info("client connected handle not found, g_http_client_count=%d" % g_http_client_count)
            conn=None
            return


        send_suc_flag=False
        if conn:
            
            send_message_event_string=ResponseClientHandle.get_msg_event_number_string(msg)
            log.debug_info("Agent send message(%s) to client ipaddress=%s" % (send_message_event_string, ResponseClientHandle.get_client_ipaddress(conn)) )
            
            try:
                #发送消息到client
                conn.write(str(msg))
                conn.finish()

                #断开连接
                if conn.transport:
                    conn.transport.loseConnection()
                    
                log.debug_info("Agent send message suc")
                               
            except Exception, e:
                err_info = "Agent send message occurs exception: %s" % e
                log.debug_error(err_info)
                    
            #更新连接接句柄总数，成功send一次，接接句柄总数减一
            if g_http_client_count>0:
                g_http_client_count-=1
                log.debug_info("loseConnection: Agent HTTP connected client count: %d" % g_http_client_count)
            
            send_suc_flag=True
        else:
            send_suc_flag=False
        
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #add by wangjun 20130716
        #获取MessageSequence对象句柄，并将数据处理结果更新到MessageSequence对象中
        MessageSequenceManagement.finish_message_sequence_obj(conn,str(msg),send_suc_flag)
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        #清空通讯句柄的值，该句柄只能使用一次
        conn=None
        log.debug_info(u"Agent send response data to client end")



class ResponseClientHandle(object):
    
    @staticmethod
    def check_message_complete(message):
        """
        check message complete
        """
        if not message:
            return False
        
        MESSAGE_KEY_LIST=['KEY_MESSAGE_TYPE','KEY_SN','KEY_QUEUE','KEY_MESSAGE','KEY_OBJECT']

        check_message=ResponseClientHandle.switch_msg_stream_type_str2dict(message)
        for key in MESSAGE_KEY_LIST:
            if not key in check_message.keys():
                log.debug_info("check_message_complete: data incomplete")
                return False

        return True


    @staticmethod
    def switch_msg_stream_type_str2dict(message):
        """
        switch message stream type str to dict
        """
        tmp_msg_dict = message
        if (isinstance(message, str)):
            switch_message=copy.deepcopy(message)
            tmp_msg_dict = eval(switch_message)
            
        return tmp_msg_dict
    
    
    @staticmethod
    def switch_msg_stream_type_dict2str(message):
        """
        switch message stream type dict to str
        """
        tmp_msg_str = message
        if (isinstance(message, dict)):
            switch_message=copy.deepcopy(message)
            tmp_msg_str = str(switch_message)
            
        return tmp_msg_str
    
    
    @staticmethod
    def get_msg_event_number_string(message):
        """
        解析消息，获取消息ID
        """
        temp_message=copy.deepcopy(message)
        new_message=ResponseClientHandle.switch_msg_stream_type_str2dict(temp_message)

        send_message_type=new_message.get(event.KEY_MESSAGE)
        #print event.get_event_desc(send_message_type)
        
        return event.get_event_desc(send_message_type)
    

    @staticmethod
    def get_client_ipaddress(conn):
        """
        返回客户端连接的IP地址
        """
        if conn and conn.transport:
            return conn.transport.getPeer().host
        else:
            return ""
    
    @staticmethod
    def handle_send_response(message,conn):
        """
        send message to user
        """
        
        msg=ResponseClientHandle.switch_msg_stream_type_dict2str(message)
        
        # send response to user
        try:
            log.debug_info("Agent send response to client")
            connHandle.http_respose_write(conn,msg)
            
            
        except Exception, e:
            err_info = "Agent send response to client occurs exception: %s" % e
            log.debug_err(err_info)


    @staticmethod
    def handle_except(message, conn, err_info):
        """
        when handle_message occurs exception, return fail to user
        """
        new_message=copy.deepcopy(message)
        
        msg=ResponseClientHandle.switch_msg_stream_type_str2dict(new_message)

        msg_group=msg.get(event.KEY_MESSAGE)
        
        try:
            tmp_obj = msg.get(event.KEY_OBJECT)
            strio = StringIO(tmp_obj)
            obj = pickle.load(strio)
            
            # write err_info to dict_ret
            obj.dict_ret = {}
            obj.dict_ret['str_result'] = err_info
            obj.dict_ret['dict_data'] = {"FaultCode":agentcfg.AGENT_ERROR_CODE,"FaultString":err_info} #"Agent error"
            
            strio = StringIO()
            pickle.dump(obj, strio)
            
            msg[event.KEY_MESSAGE] = int(msg_group) + 2
            msg[event.KEY_OBJECT] = strio.getvalue()
            
        except Exception, e:
            err_info = "Pickle object occurs exception: %s" % e
            log.debug_err(err_info)
            
            msg[event.KEY_MESSAGE] = int(msg_group) + 2
            msg[event.KEY_OBJECT] = {}
        
        ResponseClientHandle.handle_send_response(msg,conn)
        return


    @staticmethod
    def handle_response_client_WLexec_request(message, conn):
        """
        response user/acs exec worklist request event
        """
        new_message=copy.deepcopy(message)

        new_message[event.KEY_MESSAGE_TYPE]=event.EVENT_WORKLIST_GROUP
        new_message[event.KEY_MESSAGE] = event.EV_WORKLIST_EXECUTE_RSP

        log.debug_err("handle_response_client_WLexec_request")
        log.debug_err(new_message)
        
        ResponseClientHandle.handle_send_response(new_message,conn)
        return
    
    
    
    @staticmethod
    def handle_response_worklistserver_WLexec_response_post(message, conn):
        """
        response worlistserver post exec worklist response event
        """
        new_message=copy.deepcopy(message)
        
        new_message[event.KEY_MESSAGE_TYPE]=event.EVENT_WORKLIST_GROUP
        new_message[event.KEY_MESSAGE] = event.EV_WORKLIST_EXECUTE_RSP_RSP

        log.debug_err("handle_response_worklistserver_WLexec_response_post")
        log.debug_err(new_message)
        
        ResponseClientHandle.handle_send_response(new_message,conn)
        return
    

    @staticmethod
    def handle_send_rpc_check_toACS_request_reponse(message,conn,request_response_error=True,dict_ret={}):
        """
        send rpc check event form acs rpc response post 
        """
        
        new_message=copy.deepcopy(message)
        
        tmp_sn=copy.deepcopy(new_message.get(event.KEY_SN))
        tmp_event_request=copy.deepcopy(new_message.get(event.KEY_MESSAGE))
 
        new_message[event.KEY_MESSAGE_TYPE]=event.EVENT_RPC_GROUP
        if True == request_response_error:
            new_message[event.KEY_MESSAGE] = event.EV_RPC_CHECK_FAIL
        else:
            new_message[event.KEY_MESSAGE] = event.EV_RPC_CHECK_RSP

        new_message[event.KEY_SENDER]=event.KEY_SENDER_AGENT

        # pickle KEY_OBJECT value
        try:
            # build key_object 
            tmp_obj = event.MsgUserRpcCheck(tmp_sn,tmp_event_request,dict_ret)
        
            strio = StringIO()
            pickle.dump(tmp_obj, strio)
            new_message[event.KEY_OBJECT] =  strio.getvalue()

        except Exception,e:
            err_info = "pickle event.KEY_OBJECT occurs error:%s" % e
            log.run_err(err_info)
            ResponseClientHandle.handle_except(new_message,conn,err_info)

        log.debug_err("handle_send_rpc_check_toACS_request_reponse")
        #log.debug_err(new_message)
        
        ResponseClientHandle.handle_send_response(new_message,conn)


    @staticmethod
    def handle_send_response_dutqueue_requestqueue_busy(parent_msg,conn, event_list):
        """
        """
        msg=copy.deepcopy(parent_msg)
        
        # return user all requests in queue    
        msg[event.KEY_MESSAGE_TYPE] = event.MSG_TYPE_QUEUE_CHECK
        
        try:
            tmp_obj = parent_msg.get(event.KEY_OBJECT)
            strio = StringIO(tmp_obj)
            obj = pickle.load(strio)
            
            # write data to dict_ret
            obj.dict_ret = {}
            obj.dict_ret['str_result'] = "Check user whether like to queue!"
            obj.dict_ret['dict_data'] = {"queue_info":event_list}
            
            strio = StringIO()
            pickle.dump(obj, strio)
            
            msg[event.KEY_OBJECT] = strio.getvalue()
            
        except Exception, e:
            err_info = "Pickle object occurs exception: %s" % e
            log.debug_err(err_info)
            ResponseClientHandle.handle_except(parent_msg, conn, err_info)
            return
        

        # send response to user
        tmp_queuecheck_msg=ResponseClientHandle.switch_msg_stream_type_dict2str(msg)

        try:
            log.debug_info("Agent send queue check message to user!")

            connHandle.http_respose_write(conn,tmp_queuecheck_msg)
            
        except Exception,e:
            err_info = "Agent send queue check to user occurs exception: %s" % e
            log.debug_err(err_info)
    

    