#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: DUTManagement
#  function: management DUTQueue object and call DUTQueue.dispath_event() deal with message
#  Author: ATT development group
#  version: V1.0
#  date: 2013.4.15
#  change log:
#  wangjun  20130415     create
#  wangjun  20130715     更新接口里的功能说明
#  wangjun  20130718     添加将消息加入到MessageSequenceManagement管理队列中并根据节点的状态做处理，
#                        如果该消息已经处理过了，则直接向client发送处理结果，并返回False标志，否则，返回True，继续消息分发流程。
#  wangjun  20130718     优化LOG信息
#  wangjun  20131024     处理守护进程的心跳包数据
#
# ***************************************************************************

import threading
import pickle
from cStringIO import StringIO
import DUTqueue
from responseclient import ResponseClientHandle

import TR069.lib.common.logs.log as log
import TR069.lib.common.event as event

#add by wangjun 20130716
from  messagesequencemanagement import MessageSequenceManagement

dict_dutqueue_object = {}                        # {dut_id: DUTQueue object}
dict_dutqueue_object_lock = threading.Lock()     # used to lock dict_dutqueue_object

DUTQUEUE_OBJECT_DEFAULT_KEY="DUTQUEUE_OBJECT_DEFAULT_KEY"


class DUTQueueManagement(object):
    """
    管理DUTQueue对象
    """
    
    @staticmethod    
    def get_dut_id(message):
        """
        获取消息的可代表性SN或ID
        """
        global DUTQUEUE_OBJECT_DEFAULT_KEY
        
        tmp_dut_id=None
        
        msg_event = message.get(event.KEY_MESSAGE)
        msg_group = int(msg_event) & 0xFF00
        if (msg_group == event.EVENT_WORKLIST_GROUP):

            if (msg_event == event.EV_WORKLIST_BUILD_RQST or
                msg_event == event.EV_WORKLIST_DOWNLOAD_RQST):
                
                tmp_dut_id=DUTQUEUE_OBJECT_DEFAULT_KEY
                
            else:
                if (msg_event == event.EV_WORKLIST_EXEC_START_RQST or
                    msg_event == event.EV_WORKLIST_EXECUTE_RSP_RQST):
                        tmp_dut_id=DUTqueue.ResponseWLexecHandle.get_WLexec_worklist_sn(message)
                else:
                    tmp_dut_id=DUTqueue.ResponseWLexecHandle.get_WLexec_worklist_id(message)
                    

        elif (msg_group == event.EVENT_QUERY_GROUP or
                msg_group == event.EVENT_CONFIGURE_GROUP or
                msg_group == event.EVENT_RPC_GROUP):

            #set query all online cpe post default dut id  #add by wangjun 20130821
            if msg_event == event.EV_QUERY_ALL_ONLINE_CPE_RQST:
                tmp_dut_id=DUTQUEUE_OBJECT_DEFAULT_KEY
                
            if message.get(event.KEY_SN):
                tmp_dut_id= message.get(event.KEY_SN)
        else:
            pass
        
        return tmp_dut_id


    @staticmethod    
    def insert_dut_obj(request):
        """
        解析消息，根据消息类型，分发到DUT_ID对应的DUTQueue对象消息队列中
        """
        #检查消息的完整性
        tmp_msg_is_complete=ResponseClientHandle.check_message_complete(request[0])
        if False == tmp_msg_is_complete:
            err_info = "Recv client request event data incomplete"
            log.debug_err(err_info)
            ResponseClientHandle.handle_except(request[0],request[1], err_info)
            return
        
        DUTQueueManagement.delete_expired_dut_obj()

        message=request[0]
        message_type=message.get(event.KEY_MESSAGE)
        
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #add by wangjun 20131024
        #拦截守护进程的心跳包数据并发送响应结果
        if (message_type == event.EV_QUERY_IS_HANG_RQST):
            
            rc_status=DUTQueueManagement.keepalive_request_response(message,request[1])
            if True == rc_status:
                #消息不在往下分发
                return
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #add by wangjun 20130716
        #获取消息的sequence id
        message_sequence_id=message.get(event.KEY_SEQUENCE)
        
        #将消息加入到MessageSequenceManagement管理队列中,如果该消息已经处理过了，
        #则直接向client发送处理结果，并返回False标志，否则，返回True，继续消息分发流程
        insert_sequence_rc=MessageSequenceManagement.insert_message_sequence_obj(message_sequence_id,request[1])
        if False == insert_sequence_rc:
            return
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        log.app_info("(Request from client %s)Insert request(message==%s) to DUTQueue" %(ResponseClientHandle.get_client_ipaddress(request[1]),event.get_event_desc(message_type)))

        dut_id=DUTQueueManagement.get_dut_id(message)
        if None == dut_id:
            err_info = "Not found message request sn data"
            log.debug_err(err_info)
            if (message_type == event.EV_WORKLIST_EXECUTE_RSP_RQST): #add by wangjun 20130531
                DUTqueue.ResponseWLexecHandle.handle_WLexec_request_except(request[0],err_info)
            else:
                ResponseClientHandle.handle_except(request[0],request[1],err_info)
            return

        log_dut_id = "insert_dut_obj get_dut_id=" + dut_id
        log.debug_err(log_dut_id)
                
        dut_obj_handle=DUTQueueManagement.get_dut_obj_handle(dut_id)
        if None == dut_obj_handle:
            if (message_type == event.EV_WORKLIST_EXECUTE_RSP_RQST): #add by wangjun 20130531
                err_info = "Not found execute worklist DUTQueue running process"
                log.debug_err(err_info)
                DUTqueue.ResponseWLexecHandle.handle_WLexec_request_except(request[0],err_info)
            else:
                dut_obj_handle=DUTQueueManagement.new_dut_obj(dut_id)

        if None == dut_obj_handle:
            return
        
        conn=request[1]

        #add by wangjun 20130523
        message_key_sender=message.get(event.KEY_SENDER)
        if (None == message_key_sender):
            message_key_sender=event.KEY_SENDER_USER

        #open QUEUE_INIT key control to GUI #change by wangjun 20130826
        if (event.KEY_SENDER_USER == message_key_sender):
            
            dut_obj_request_queue_busy=DUTQueueManagement.handle_dutqueue_request_queue_status_check(dut_obj_handle,
                                                                                                 message,
                                                                                                 conn)
            if True==dut_obj_request_queue_busy:
                log.debug_err("DUTQueue request queue busy")
                return
        else:
            pass
        
        #log.debug_err("insert_dut_obj call dispath_event")
        message_priority_level=message.get(event.KEY_PRIORITY_LEVEL)
        dut_obj_handle.dispath_event(message_type,message_priority_level,request,message_key_sender)

    
    @staticmethod    
    def new_dut_obj(dut_id):
        """
        创建新的DUTQueue对象
        """
        global dict_dutqueue_object
        global dict_dutqueue_object_lock
        
        dut_obj_handle = DUTqueue.DUTQueue(dut_id)

        dict_dutqueue_object_lock.acquire()
        dict_dutqueue_object[dut_id] = dut_obj_handle
        dict_dutqueue_object_lock.release()
        
        return dut_obj_handle


    @staticmethod    
    def get_dut_obj_handle(dut_id):
        """
        获取dut_id对应的DUTQueue对象句柄
        """
        global dict_dutqueue_object
        global dict_dutqueue_object_lock
        
        dict_dutqueue_object_lock.acquire()

        dut_obj_handle=None
        if dut_id in dict_dutqueue_object:
            dut_obj_handle = dict_dutqueue_object[dut_id]    # get this dut_id's DUTQueue object

        dict_dutqueue_object_lock.release()

        return dut_obj_handle

            
    @staticmethod    
    def delete_expired_dut_obj():
        """
        清除过期的DUTQueue对象
        """
        global dict_dutqueue_object
        global dict_dutqueue_object_lock
        
        dict_dutqueue_object_lock.acquire()
        
        dict_dutqueue_object_list = dict_dutqueue_object.keys()
        for dut_id in dict_dutqueue_object_list:
            dut_obj_handle = dict_dutqueue_object[dut_id]
            if 1 == dut_obj_handle.get_dut_expire_property():
                dict_dutqueue_object.pop(dut_id)
        
        dict_dutqueue_object_lock.release()


    @staticmethod
    def handle_dutqueue_request_queue_status_check(dut_obj,parent_msg,conn):
        """
        检查当前是否有RPC方法正在执行，现在该方法已经停止使用。
        """
        message_type=parent_msg.get(event.KEY_MESSAGE)
        message_group = int(message_type) & 0xFF00
        
        message_queue= parent_msg.get(event.KEY_QUEUE)
        if message_queue == event.QUEUE_INIT:
            
            if (message_group == event.EVENT_RPC_GROUP):
                # check whether have request in request_queue
                if (len(dut_obj.request_queue_priority_high) > 0 or
                    len(dut_obj.request_queue_priority_normal) > 0 or
                    dut_obj.cur_handle_request != []):
                
                    #get DUTqueue request_queue busy node list
                    event_node_list=DUTQueueManagement.get_dutqueue_requestqueue_node_data(dut_obj,
                                                                                           parent_msg,
                                                                                           conn)
                
                    # send DUTqueue request_queue busy node list data to user
                    ResponseClientHandle.handle_send_response_dutqueue_requestqueue_busy(parent_msg,
                                                                                         conn,
                                                                                         event_node_list)

                    return True
            
            elif (message_group == event.EVENT_WORKLIST_GROUP and
                  message_type == event.EV_WORKLIST_EXEC_START_RQST):
                pass
            
            else:
                pass
            
        return False
        
    
    @staticmethod
    def get_dutqueue_requestqueue_node_data(dut_obj, parent_msg, conn):
        """
        如果当前有RPC正在执行，则将消息返回给USER，USER端自己做处理。现在该方法已经停止使用。
        """

        event_list = []
        
        tmp_request_queue=[]
        
        tmp_request_queue.extend(dut_obj.request_queue_priority_high)
        tmp_request_queue.extend(dut_obj.request_queue_priority_normal)
        
        if dut_obj.cur_handle_request != []:
            tmp_request_queue.insert(0, dut_obj.cur_handle_request)
        
        for element in tmp_request_queue:
            
            # get request message in queue
            # message=element[0], conn=element[1]
            reuqest_msg = element[0]
            
            msg_type =reuqest_msg.get(event.KEY_MESSAGE)
            msg_group = int(msg_type) & 0xFF00
            
            msg_obj = reuqest_msg.get(event.KEY_OBJECT)
            
            try:
                strio = StringIO(msg_obj)
                ret_obj = pickle.load(strio)
            except Exception,e:
                err_info = "Unpickle event.KEY_OBJECT occurs error:%s" % e
                ResponseClientHandle.handle_except(parent_msg, conn, err_info)
                return
            
            tmp_dict = {}
            if msg_group == event.EVENT_RPC_GROUP:
                tmp_dict[ret_obj.rpc_name] = ret_obj.rpc_args
            
            elif (msg_group == event.EVENT_WORKLIST_GROUP
                  and msg_type == event.EV_WORKLIST_EXEC_START_RQST):
                tmp_dict["MsgWorklistExecute"] = ret_obj.id_

            event_list.append(tmp_dict)
        
        return event_list
    
    
    @staticmethod
    def keepalive_request_response(request_message, conn):
        """
        处理守护进程的心跳包数据
        """
        message_type=request_message.get(event.KEY_MESSAGE)
        if message_type != event.EV_QUERY_IS_HANG_RQST:
            return False
        
        try:
            msg_obj = request_message.get(event.KEY_OBJECT)
            strio = StringIO(msg_obj)
            recv_data_obj = pickle.load(strio)
                
        except Exception,e:
            err_info = "keepalive_request_response: Unpickle event.KEY_OBJECT occurs error:%s" % e
            log.debug_err(err_info)
                
            request_message[event.KEY_MESSAGE] = message_type + 2
            #发送响应消息
            ResponseClientHandle.handle_send_response(request_message, conn)
            return True
            
        if not (isinstance(recv_data_obj,event.MsgQueryIsHang)):
                  
            #构造错误的返回消息
            error_info="keepalive_request_response: Request message obj is not MsgQueryIsHang"
            log.app_err(error_info)

            request_message[event.KEY_MESSAGE] = message_type + 2
                
        else:
            #构造正常响应消息
            request_message[event.KEY_MESSAGE] = message_type + 1
            
        #发送响应消息
        ResponseClientHandle.handle_send_response(request_message, conn)
        return True
    