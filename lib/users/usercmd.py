#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: requesthandler
#  function: handler user request including build message, send message,
#            recv response, parse response
#  Author: ATT development group
#  version: V1.0
#  date: 2012.11.16
#  change log:
#  lana     20121116        created
#  nwf      2013-05-25      refactor(unify)
#
# ***************************************************************************

import  os
import  sys
import  pickle
from    cStringIO   import      StringIO
import  types
from    datetime    import      datetime, timedelta
from    time        import      sleep
import  TR069.vendor.httplib2   as httplib2

from    TR069.lib.common.function   import  print_trace, get_id
from    TR069.lib.common.event      import  *
from    TR069.lib.common.error      import  *
import  TR069.lib.common.config     as      config
from    TR069.lib.common.httpclient import  HttpClient
import  TR069.lib.users.usercfg          as      usercfg 
from    TR069.lib.common.releasecfg       import  *   # for tr069 self or RF?

# --------------------------------------------------------------

class Usercmd(object):
    """
    handler user request
    """
    
    def __init__(self, ip="", port="", page="", sender="", worklist_id=""):
        """
        """
        # nwf 2013-06-03
        self.ip             = ip 
        self.port           = port
        self.page           = page
        
        self.sender         = sender
        self.worklist_id    = worklist_id
        
        #用来表示请求发起端来自TR069 GUI
        self.reqeust_from_gui_flag=False
        
        # 用来表示请求发起端来自TR069浏览器 zsj 2014/3/17
        self.request_from_bs_flag = False
        
    def set_request_source_from_tr069gui(self):
        self.reqeust_from_gui_flag=True
    
    def set_request_source_form_bs(self):
        self.request_from_bs_flag = True

    def build_alarm_inform_msg(self, event, obj):
        """
        """
        ret = ERR_FAIL  # default  
        msg = ""

        for nwf in [1]:
            try:         

                strio                   = StringIO()
                pickle.dump(obj, strio)  
                
                dict1                   = {}
                dict1[KEY_MESSAGE]      = event 
                dict1[KEY_OBJECT]       = strio.getvalue()
                dict1[KEY_SN]           = obj.sn                                
                dict1[KEY_MESSAGE_TYPE] = EVENT_CONFIGURE_GROUP
                dict1[KEY_QUEUE]        = QUEUE_WAIT
                dict1[KEY_SENDER]       = KEY_SENDER_USER  
                dict1[KEY_SEQUENCE]     = get_id("Seq")
                
                msg                 = str(dict1)
        
            except Exception,e:
                msg = e
                print_trace(e)
                
                break
            
            ret = ERR_SUCCESS

        return ret, msg


    def build_monitor_inform_msg(self, event, obj):
        """
        """
        ret = ERR_FAIL  # default  
        msg = ""

        for nwf in [1]:
            try:         

                strio                   = StringIO()
                pickle.dump(obj, strio)  
                
                dict1                   = {}
                dict1[KEY_MESSAGE]      = event 
                dict1[KEY_OBJECT]       = strio.getvalue()
                dict1[KEY_SN]           = obj.sn                                
                dict1[KEY_MESSAGE_TYPE] = EVENT_CONFIGURE_GROUP
                dict1[KEY_QUEUE]        = QUEUE_WAIT
                dict1[KEY_SENDER]       = KEY_SENDER_USER  
                dict1[KEY_SEQUENCE]     = get_id("Seq")
                
                msg                 = str(dict1)
        
            except Exception,e:
                msg = e
                print_trace(e)
                
                break
            
            ret = ERR_SUCCESS

        return ret, msg
        
        

    def build_query_cpe_info(self, sn):
        """
        """
        ret = ERR_FAIL  # default  
        msg = ""

        for nwf in [1]:
            try:         

                obj                 = MsgQueryCPEInfo(sn)
                strio               = StringIO()
                pickle.dump(obj, strio)  
                
                dict1                   = {}
                dict1[KEY_MESSAGE]      = EV_QUERY_CPE_INFO_RQST        
                dict1[KEY_OBJECT]       = strio.getvalue()
                dict1[KEY_SN]           = sn                                
                dict1[KEY_MESSAGE_TYPE] = EVENT_QUERY_GROUP
                dict1[KEY_QUEUE]        = QUEUE_WAIT
                dict1[KEY_SENDER]       = KEY_SENDER_USER
                dict1[KEY_SEQUENCE]     = get_id("Seq")
                
                msg                     = str(dict1)
        
            except Exception,e:
                msg = e
                print_trace(e)
                
                break
            
            ret = ERR_SUCCESS

        return ret, msg
  

    def build_rpc_msg(self, sn, rpc_name, dict_args, queue_wait=QUEUE_WAIT):
        """
        obj_user_rpc = MsgUserRpc
        """
        # 新加参数queue_wait是否等待执行结束 zsj 2013/8/23
        
        ret = ERR_FAIL  # default  
        msg = ""

        for nwf in [1]:
            try: 
            
                obj_user_rpc            = MsgUserRpc(sn, rpc_name, dict_args)
                obj_user_rpc.worklist_id = self.worklist_id
                strio                   = StringIO()
                pickle.dump(obj_user_rpc, strio)  
                
                dict1 = {}
                dict1[KEY_MESSAGE]      = dict_rpc_event[obj_user_rpc.rpc_name]            
                dict1[KEY_OBJECT]       = strio.getvalue()
                dict1[KEY_SN]           = sn                                
                dict1[KEY_MESSAGE_TYPE] = EVENT_RPC_GROUP                
                
                dict1[KEY_QUEUE]        = queue_wait
                    
                if (self.sender):
                    dict1[KEY_SENDER]   = self.sender
                else:
                    dict1[KEY_SENDER]   = KEY_SENDER_USER
                    
                dict1[KEY_SEQUENCE]     = get_id("Seq")
                
                msg                     = str(dict1)
        
            except Exception,e:
                msg = e
                print_trace(e)
                
                break
            
            ret = ERR_SUCCESS

        return ret, msg


    def build_update_cpe_info(self, sn, modify_items):
        """
        """
        ret = ERR_FAIL  # default  
        msg = ""

        for nwf in [1]:
            try:         

                obj                     = MsgModifyCPEInfo(sn)
                obj.dict_modify_items   = modify_items
                strio                   = StringIO()
                pickle.dump(obj, strio)  
                
                dict1                   = {}
                dict1[KEY_MESSAGE]      = EV_MODIFY_CPE_INFO_RQST         
                dict1[KEY_OBJECT]       = strio.getvalue()
                dict1[KEY_SN]           = sn                                
                dict1[KEY_MESSAGE_TYPE] = EVENT_QUERY_GROUP
                dict1[KEY_QUEUE]        = QUEUE_WAIT
                dict1[KEY_SENDER]       = KEY_SENDER_USER    
                dict1[KEY_SEQUENCE]     = get_id("Seq")
                
                msg                     = str(dict1)
        
            except Exception,e:
                msg = e
                print_trace(e)
                
                break
            
            ret = ERR_SUCCESS

        return ret, msg


    def build_alarm_query(self, event, obj):
        """
        """
        ret = ERR_FAIL  # default  
        msg = ""

        for nwf in [1]:
            try:         

                strio                   = StringIO()
                pickle.dump(obj, strio)  
                
                dict1                   = {}
                dict1[KEY_MESSAGE]      = EV_QUERY_ALARM_RQST            
                dict1[KEY_OBJECT]       = strio.getvalue()
                dict1[KEY_SN]           = obj.sn                                
                dict1[KEY_MESSAGE_TYPE] = EVENT_CONFIGURE_GROUP
                dict1[KEY_QUEUE]        = QUEUE_WAIT
                dict1[KEY_SENDER]       = KEY_SENDER_USER  
                dict1[KEY_SEQUENCE]     = get_id("Seq")
                
                msg                     = str(dict1)
        
            except Exception,e:
                msg = e
                print_trace(e)
                
                break
            
            ret = ERR_SUCCESS

        return ret, msg


    def build_monitor_query(self, event, obj):
        """
        """
        ret = ERR_FAIL  # default  
        msg = ""

        for nwf in [1]:
            try:         

                strio                   = StringIO()
                pickle.dump(obj, strio)  
                
                dict1                   = {}
                dict1[KEY_MESSAGE]      = EV_QUERY_MONITOR_RQST            
                dict1[KEY_OBJECT]       = strio.getvalue()
                dict1[KEY_SN]           = obj.sn                                
                dict1[KEY_MESSAGE_TYPE] = EVENT_CONFIGURE_GROUP
                dict1[KEY_QUEUE]        = QUEUE_WAIT
                dict1[KEY_SENDER]       = KEY_SENDER_USER  
                dict1[KEY_SEQUENCE]     = get_id("Seq")
                
                msg                     = str(dict1)
        
            except Exception,e:
                msg = e
                print_trace(e)
                
                break
            
            ret = ERR_SUCCESS

        return ret, msg


    def build_init_wait_eventcode(self, sn, include_eventcodes, exclude_eventcodes):
        """
        """
        ret = ERR_FAIL  # default  
        msg = ""

        for nwf in [1]:
            try:         

                obj                     = MsgWaitEventCode(sn)
                obj.include_eventcodes  = include_eventcodes
                obj.exclude_eventcodes  = exclude_eventcodes
                strio                   = StringIO()
                pickle.dump(obj, strio)  
                
                dict1                   = {}
                dict1[KEY_MESSAGE]      = EV_WAIT_EVENTCODE_INIT_RQST            
                dict1[KEY_OBJECT]       = strio.getvalue()
                dict1[KEY_SN]           = sn                                
                dict1[KEY_MESSAGE_TYPE] = EVENT_CONFIGURE_GROUP
                dict1[KEY_QUEUE]        = QUEUE_WAIT
                dict1[KEY_SENDER]       = KEY_SENDER_USER  
                dict1[KEY_SEQUENCE]     = get_id("Seq")
                
                msg                 = str(dict1)
        
            except Exception,e:
                msg = e
                print_trace(e)
                
                break
            
            ret = ERR_SUCCESS

        return ret, msg


    def build_start_wait_eventcode(self, sn, wait_eventcode_id):
        """
        """
        ret = ERR_FAIL  # default  
        msg = ""

        for nwf in [1]:
            try:         

                obj                     = MsgWaitEventCode(sn)
                obj.id_                 = wait_eventcode_id
                strio                   = StringIO()
                pickle.dump(obj, strio)  
                
                dict1                   = {}
                dict1[KEY_MESSAGE]      = EV_WAIT_EVENTCODE_START_RQST            
                dict1[KEY_OBJECT]       = strio.getvalue()
                dict1[KEY_SN]           = sn                                
                dict1[KEY_MESSAGE_TYPE] = EVENT_CONFIGURE_GROUP
                dict1[KEY_QUEUE]        = QUEUE_WAIT
                dict1[KEY_SENDER]       = KEY_SENDER_USER  
                dict1[KEY_SEQUENCE]     = get_id("Seq")
                
                msg                 = str(dict1)
        
            except Exception,e:
                msg = e
                print_trace(e)
                
                break
            
            ret = ERR_SUCCESS

        return ret, msg        


    def build_stop_wait_eventcode(self, sn, wait_eventcode_id):
        """
        """
        ret = ERR_FAIL  # default  
        msg = ""

        for nwf in [1]:
            try:         

                obj                     = MsgWaitEventCode(sn)
                obj.id_                 = wait_eventcode_id
                strio                   = StringIO()
                pickle.dump(obj, strio)  
                
                dict1                   = {}
                dict1[KEY_MESSAGE]      = EV_WAIT_EVENTCODE_STOP_RQST            
                dict1[KEY_OBJECT]       = strio.getvalue()
                dict1[KEY_SN]           = sn                                
                dict1[KEY_MESSAGE_TYPE] = EVENT_CONFIGURE_GROUP
                dict1[KEY_QUEUE]        = QUEUE_WAIT
                dict1[KEY_SENDER]       = KEY_SENDER_USER  
                dict1[KEY_SEQUENCE]     = get_id("Seq")
                
                msg                 = str(dict1)
        
            except Exception,e:
                msg = e
                print_trace(e)
                
                break
            
            ret = ERR_SUCCESS

        return ret, msg


    def build_query_wait_eventcode(self, sn, wait_eventcode_id):
        """
        """
        ret = ERR_FAIL  # default  
        msg = ""

        for nwf in [1]:
            try:         

                obj                     = MsgWaitEventCode(sn)
                obj.id_                 = wait_eventcode_id
                strio                   = StringIO()
                pickle.dump(obj, strio)  
                
                dict1                   = {}
                dict1[KEY_MESSAGE]      = EV_WAIT_EVENTCODE_QUERY_RQST            
                dict1[KEY_OBJECT]       = strio.getvalue()
                dict1[KEY_SN]           = sn                                
                dict1[KEY_MESSAGE_TYPE] = EVENT_CONFIGURE_GROUP
                dict1[KEY_QUEUE]        = QUEUE_WAIT
                dict1[KEY_SENDER]       = KEY_SENDER_USER  
                dict1[KEY_SEQUENCE]     = get_id("Seq")
                
                msg                     = str(dict1)
        
            except Exception,e:
                msg = e
                print_trace(e)
                
                break
            
            ret = ERR_SUCCESS

        return ret, msg        
        

    def build_worklist_msg(self, cmd, args):
        """
        """
        ret = ERR_FAIL  # default  
        msg = ""

        for nwf in [1]:
            try:         

                cls1                    = dict_workprocess_obj[cmd]
                obj                     = cls1(**args)                                        
                strio                   = StringIO()
                pickle.dump(obj, strio)  
                
                dict1                   = {}
                dict1[KEY_MESSAGE]      = dict_workprocess_event[cmd]            
                dict1[KEY_OBJECT]       = strio.getvalue()
                dict1[KEY_SN]           = None                
                dict1[KEY_SENDER]       = KEY_SENDER_USER
                dict1[KEY_MESSAGE_TYPE] = EVENT_WORKLIST_GROUP
                dict1[KEY_QUEUE]        = QUEUE_WAIT      
                dict1[KEY_SEQUENCE]     = get_id("Seq")
                
                msg                     = str(dict1)
        
            except Exception,e:
                msg = e
                print_trace(e)
                
                break
            
            ret = ERR_SUCCESS

        return ret, msg

    def build_get_online_cpe(self, sn):
        """
        """
        ret = ERR_FAIL  # default  
        msg = ""

        for nwf in [1]:
            try:         

                obj                 = MsgQueryCPEOnline(sn)
                strio               = StringIO()
                pickle.dump(obj, strio)  
                
                dict1                   = {}
                dict1[KEY_MESSAGE]      = EV_QUERY_ALL_ONLINE_CPE_RQST        
                dict1[KEY_OBJECT]       = strio.getvalue()
                dict1[KEY_SN]           = sn                                
                dict1[KEY_MESSAGE_TYPE] = EVENT_QUERY_GROUP
                dict1[KEY_QUEUE]        = QUEUE_INIT
                dict1[KEY_SENDER]       = KEY_SENDER_USER
                dict1[KEY_SEQUENCE]     = get_id("Seq")
                
                msg                     = str(dict1)
        
            except Exception,e:
                msg = e
                print_trace(e)
                
                break
            
            ret = ERR_SUCCESS

        return ret, msg


    def build_close_tr069_acs(self):
        """
        """
        ret = ERR_FAIL  # default  
        msg = ""

        for nwf in [1]:
            try:         

                obj                     = MsgTR069Close()                                        
                strio                   = StringIO()
                pickle.dump(obj, strio)  
                
                dict1                   = {}
                dict1[KEY_MESSAGE]      = EV_TR069_ACS_EXIT_RQST            
                dict1[KEY_OBJECT]       = strio.getvalue()
                dict1[KEY_SN]           = "nwf"                
                dict1[KEY_SENDER]       = KEY_SENDER_USER
                dict1[KEY_MESSAGE_TYPE] = EVENT_CONFIGURE_GROUP
                dict1[KEY_QUEUE]        = QUEUE_WAIT      
                dict1[KEY_SEQUENCE]     = get_id("Seq")
                
                msg                     = str(dict1)
        
            except Exception,e:
                msg = e
                print_trace(e)
                
                break
            
            ret = ERR_SUCCESS

        return ret, msg


    def build_query_version_is_ok(self, version):
        """
        """
        ret = ERR_FAIL  # default  
        msg = ""

        for nwf in [1]:
            try:         

                obj                     = MsgQueryVersionIsOk() 
                obj.version             = version
                strio                   = StringIO()
                pickle.dump(obj, strio)  
                
                dict1                   = {}
                dict1[KEY_MESSAGE]      = EV_QUERY_VERSION_IS_OK_RQST            
                dict1[KEY_OBJECT]       = strio.getvalue()
                dict1[KEY_SN]           = "nwf"                
                dict1[KEY_SENDER]       = KEY_SENDER_USER
                dict1[KEY_MESSAGE_TYPE] = EVENT_QUERY_GROUP
                dict1[KEY_QUEUE]        = QUEUE_WAIT      
                dict1[KEY_SEQUENCE]     = get_id("Seq")
                
                msg                     = str(dict1)
        
            except Exception,e:
                msg = e
                print_trace(e)
                
                break
            
            ret = ERR_SUCCESS

        return ret, msg        


    def build_query_cpe_last_faults(self, sn):
        """
        """
        ret = ERR_FAIL  # default  
        msg = ""

        for nwf in [1]:
            try:         

                obj                     = MsgQueryCpeLastFaults(sn) 
                strio                   = StringIO()
                pickle.dump(obj, strio)  
                
                dict1                   = {}
                dict1[KEY_MESSAGE]      = EV_QUERY_CPE_LAST_FAULTS_RQST            
                dict1[KEY_OBJECT]       = strio.getvalue()
                dict1[KEY_SN]           = sn                
                dict1[KEY_SENDER]       = KEY_SENDER_USER
                dict1[KEY_MESSAGE_TYPE] = EVENT_QUERY_GROUP
                dict1[KEY_QUEUE]        = QUEUE_WAIT      
                dict1[KEY_SEQUENCE]     = get_id("Seq")
                
                msg                     = str(dict1)
        
            except Exception,e:
                msg = e
                print_trace(e)
                
                break
            
            ret = ERR_SUCCESS

        return ret, msg  


    def build_query_last_session_soap(self, sn):
        """
        """
        ret = ERR_FAIL  # default  
        msg = ""

        for nwf in [1]:
            try:         

                obj                     = MsgQueryLastSessionSoap(sn) 
                strio                   = StringIO()
                pickle.dump(obj, strio)  
                
                dict1                   = {}
                dict1[KEY_MESSAGE]      = EV_QUERY_LAST_SESSION_SOAP_RQST            
                dict1[KEY_OBJECT]       = strio.getvalue()
                dict1[KEY_SN]           = sn                
                dict1[KEY_SENDER]       = KEY_SENDER_USER
                dict1[KEY_MESSAGE_TYPE] = EVENT_QUERY_GROUP
                dict1[KEY_QUEUE]        = QUEUE_WAIT      
                dict1[KEY_SEQUENCE]     = get_id("Seq")
                
                msg                     = str(dict1)
        
            except Exception,e:
                msg = e
                print_trace(e)
                
                break
            
            ret = ERR_SUCCESS

        return ret, msg 


    def build_query_cpe_interface_version(self, sn):
        """
        """
        ret = ERR_FAIL  # default  
        msg = ""

        for nwf in [1]:
            try:         

                obj                     = MsgQueryCPEInterfaceVersion(sn) 
                strio                   = StringIO()
                pickle.dump(obj, strio)  
                
                dict1                   = {}
                dict1[KEY_MESSAGE]      = EV_QUERY_CPE_INTERFACE_VERSION_RQST            
                dict1[KEY_OBJECT]       = strio.getvalue()
                dict1[KEY_SN]           = sn                
                dict1[KEY_SENDER]       = KEY_SENDER_USER
                dict1[KEY_MESSAGE_TYPE] = EVENT_QUERY_GROUP
                dict1[KEY_QUEUE]        = QUEUE_WAIT      
                dict1[KEY_SEQUENCE]     = get_id("Seq")
                
                msg                     = str(dict1)
        
            except Exception,e:
                msg = e
                print_trace(e)
                
                break
            
            ret = ERR_SUCCESS

        return ret, msg         



    # --------------------------------------------------------------
    def process_rpc(self, sn, rpc_name, dict_args, queue_wait=QUEUE_WAIT):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None
        
        for nwf in [1]:
                
            try:
                
                # step1 build msg
                ret, msg = self.build_rpc_msg(sn, rpc_name, dict_args, queue_wait)
                if (ret != ERR_SUCCESS):
                    str_data = msg
                    
                    break
            
                # step2 send msg                
                ret, str_data = self.send_message(msg, usercfg.RPC_TIMEOUT)  # 没有沿用如果前面有排队动态增加超时机制 zsj
                if (ret != ERR_SUCCESS):                    
                    break                
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break
                
                # return code
                event_rsp    = data[0]                    
                obj          = data[1]
                key_msg_type = data[2]
     
                event_rqst = dict_rpc_event[rpc_name]
                if isinstance(key_msg_type, str) and key_msg_type == "MSG_TYPE_QUEUE_CHECK":
                    ret     = ERR_SUCCESS
                    self.reqeust_from_gui_flag = False
                elif(event_rsp - event_rqst == 1):
                    ret     = ERR_SUCCESS
                else:
                    ret     = ERR_FAIL
                
                # return value(dict_data is detail)
                dict_ret    = obj.dict_ret
                
                # 返回gui需要的数据 zsj 2013/8/21
                if self.reqeust_from_gui_flag:
                    if ("str_result" in dict_ret):
                        str_data = dict_ret.get("str_result")
                    return ret, str_data
                
                # 返回来自浏览器的rpc请求 zsj 2014/3/17
                if self.request_from_bs_flag:
                    return ret, dict_ret
                
                # dict_data is concrete, str_result is abstract
                if ("dict_data" in dict_ret):
                    str_data = dict_ret.get("dict_data")                    
                elif ("str_result" in dict_ret):
                    str_data = dict_ret.get("str_result")                    
                        
            except Exception, e:
                ret         = ERR_FAIL
                str_data    = e
                print_trace(e)  
        
        return ret, str_data     


    def process_worklist(self, cmd, args):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None
        
        for nwf in [1]:
                
            try:
                
                # step1 build msg
                ret, msg = self.build_worklist_msg(cmd, args)
                if (ret != ERR_SUCCESS):
                    str_data = msg
                    
                    break
            
                # step2 send msg                
                ret, str_data = self.send_message(msg)
                if (ret != ERR_SUCCESS):                    
                    break                
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break

                # return code
                event_rsp   = data[0]  
                obj         = data[1]
                event_rqst  = dict_workprocess_event[cmd]                
                if (event_rsp - event_rqst == 1):
                    str_data    = obj
                    ret         = ERR_SUCCESS
                else:
                    ret         = ERR_FAIL                                    
                    str_data    = obj.dict_ret["str_result"]
                
            except Exception, e:
                ret         = ERR_FAIL
                str_data    = e
                print_trace(e)  
        
        return ret, str_data     


    def process_worklist_exec(self, cmd, args):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None
        
        for nwf in [1]:
                
            try:
                
                # step1 build msg
                ret, msg = self.build_worklist_msg(cmd, args)
                if (ret != ERR_SUCCESS):
                    str_data = msg
                    
                    break
            
                # step2 send msg                
                ret, str_data = self.send_message(msg)
                if (ret != ERR_SUCCESS):                    
                    break                
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break                
                            
                event_rsp   = data[0]   
                obj         = data[1]                    
                event_rqst  = dict_workprocess_event[cmd]                
                if (event_rsp - event_rqst == 1):

                    # stage2 query
                    ret, str_data = self.process_worklist_exec_query(obj.id_)                    
                    break
                else:
                    ret         = ERR_FAIL                
                    str_data    = obj.dict_ret["str_result"]
                
            except Exception, e:
                ret         = ERR_FAIL
                str_data    = e
                print_trace(e)  
        
        return ret, str_data          


    def process_worklist_exec_query(self, id_):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None
        
                
        try:
            cmd             = "MsgWorklistQuery"
            dict1           = {}
            dict1["id_"]    = id_       
            args            = dict1
            
            start_time  = datetime.now()
            while(1):
                
                ret, str_data = self.process_worklist(cmd, args)
                if (ret != ERR_SUCCESS):
                    break

                # exec finish?
                obj = str_data
                if (obj.status == WORK_LIST_STATUS_SUCCESS):
                    break
                elif (obj.status == WORK_LIST_STATUS_FAIL):

                    # convert 2 str
                    str_data = obj.dict_ret["str_result"]
                    
                    ret = ERR_FAIL
                    break
                            
                if (datetime.now() - start_time > timedelta(seconds=usercfg.WORKLIST_TIMEOUT)):
                    # timeout
                    ret         = ERR_FAIL
                    str_data    = "timeout(>%s seconds)" %usercfg.WORKLIST_TIMEOUT
                    log.app_err(str_data)
                    
                    break                

                # wait
                sleep(usercfg.WORKLIST_EXEC_QUERY_SLEEP)
            
        except Exception, e:
            ret         = ERR_FAIL
            str_data    = e
            print_trace(e)  
        
        return ret, str_data                         


    def process_alarm_inform_start(self, event, obj):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None
        
        for nwf in [1]:
                
            try:
                
                # step1 build msg
                ret, msg = self.build_alarm_inform_msg(event, obj)
                if (ret != ERR_SUCCESS):
                    str_data = msg
                    
                    break
            
                # step2 send msg
                ret, str_data = self.send_message(msg)
                if (ret != ERR_SUCCESS):                    
                    break              
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break                
                               
                event_rsp   = data[0] 
                obj         = data[1]                 
                event_rqst  = event
                if (event_rsp - event_rqst == 1):

                    # stage2 query
                    ret, str_data = self.process_alarm_inform_query(
                                            EV_QUERY_ALARM_RQST, obj, 
                                            MONITOR_INFORM_STATUS_START_SUCCESS, 
                                            MONITOR_INFORM_STATUS_START_FAIL)                    
                    break
                else:
                    ret         = ERR_FAIL                    
                    str_data    = obj.dict_ret["str_result"]
                        
            except Exception, e:
                ret         = ERR_FAIL
                str_data    = e
                print_trace(e)  
        
        return ret, str_data      


    def process_monitor_inform_start(self, event, obj):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None
        
        for nwf in [1]:
                
            try:
                
                # step1 build msg
                ret, msg = self.build_monitor_inform_msg(event, obj)
                if (ret != ERR_SUCCESS):
                    str_data = msg
                    
                    break
            
                # step2 send msg
                ret, str_data = self.send_message(msg)
                if (ret != ERR_SUCCESS):                    
                    break              
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break                
                               
                event_rsp   = data[0] 
                obj         = data[1]                 
                event_rqst  = event
                if (event_rsp - event_rqst == 1):

                    # stage2 query
                    ret, str_data = self.process_monitor_inform_query(
                                            EV_QUERY_MONITOR_RQST, obj, 
                                            MONITOR_INFORM_STATUS_START_SUCCESS, 
                                            MONITOR_INFORM_STATUS_START_FAIL)                    
                    break
                else:
                    ret         = ERR_FAIL                    
                    str_data    = obj.dict_ret["str_result"]
                        
            except Exception, e:
                ret         = ERR_FAIL
                str_data    = e
                print_trace(e)  
        
        return ret, str_data           
            

    def process_alarm_inform_stop(self, event, obj):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None
        
        for nwf in [1]:
                
            try:
                
                # step1 build msg
                ret, msg = self.build_alarm_inform_msg(event, obj)
                if (ret != ERR_SUCCESS):
                    str_data = msg
                    
                    break
            
                # step2 send msg
                ret, str_data = self.send_message(msg)
                if (ret != ERR_SUCCESS):                    
                    break              
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break                
                                
                event_rsp   = data[0] 
                obj         = data[1]                
                event_rqst  = event
                if (event_rsp - event_rqst == 1):

                    # stage2 query
                    ret, str_data = self.process_alarm_inform_query(
                                            EV_QUERY_ALARM_RQST, obj, 
                                            MONITOR_INFORM_STATUS_STOP_SUCCESS, 
                                            MONITOR_INFORM_STATUS_STOP_FAIL)   
                    
                    break
                else:
                    ret         = ERR_FAIL                    
                    str_data    = obj.dict_ret["str_result"]
                        
            except Exception, e:
                ret         = ERR_FAIL
                str_data    = e
                print_trace(e)  
        
        return ret, str_data    


    def process_monitor_inform_stop(self, event, obj):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None
        
        for nwf in [1]:
                
            try:
                
                # step1 build msg
                ret, msg = self.build_monitor_inform_msg(event, obj)
                if (ret != ERR_SUCCESS):
                    str_data = msg
                    
                    break
            
                # step2 send msg
                ret, str_data = self.send_message(msg)
                if (ret != ERR_SUCCESS):                    
                    break              
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break                
                                
                event_rsp   = data[0] 
                obj         = data[1]                
                event_rqst  = event
                if (event_rsp - event_rqst == 1):

                    # stage2 query
                    ret, str_data = self.process_monitor_inform_query(
                                            EV_QUERY_MONITOR_RQST, obj, 
                                            MONITOR_INFORM_STATUS_STOP_SUCCESS, 
                                            MONITOR_INFORM_STATUS_STOP_FAIL)   
                    
                    break
                else:
                    ret         = ERR_FAIL                    
                    str_data    = obj.dict_ret["str_result"]
                        
            except Exception, e:
                ret         = ERR_FAIL
                str_data    = e
                print_trace(e)  
        
        return ret, str_data          
        

    def process_alarm_inform_query(self, event, obj, status_success, status_fail):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None


        try:
            
            start_time  = datetime.now()
            
            while(1):

                # step1 build msg
                ret, msg = self.build_alarm_query(event, obj)
                if (ret != ERR_SUCCESS):
                    str_data = msg   
                    break
                            
                # step2 send msg                
                ret, str_data = self.send_message(msg)
                if (ret != ERR_SUCCESS):                    
                    break                
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break                                  
                
                event_rsp   = data[0]   
                obj         = data[1]
                event_rqst  = event                
                if (event_rsp - event_rqst != 1):
                    str_data    = obj.dict_ret["str_result"]
                    ret         = ERR_FAIL                    
                    break

                # status ok?
                if (obj.status == status_success):
                    str_data    = obj
                    ret         = ERR_SUCCESS
                    
                    break
                elif (obj.status == status_fail):
                
                    str_data = obj.dict_ret["str_result"]   # fail convert to str                    
                    ret = ERR_FAIL
                    break                
                            
                if (datetime.now() - start_time > timedelta(seconds=usercfg.WORKLIST_TIMEOUT)):
                    # timeout                    
                    str_data    = "timeout(>%s seconds)" %timeout
                    log.app_err(str_data)

                    ret         = ERR_FAIL
                    break                

                # wait
                sleep(usercfg.WORKLIST_EXEC_QUERY_SLEEP)
            
        except Exception, e:
            ret         = ERR_FAIL
            str_data    = e
            print_trace(e)         
        
        return ret, str_data  


    def process_monitor_inform_query(self, event, obj, status_success, status_fail):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None


        try:
            
            start_time  = datetime.now()
            
            while(1):

                # step1 build msg
                ret, msg = self.build_monitor_query(event, obj)
                if (ret != ERR_SUCCESS):
                    str_data = msg           
                    break
                            
                # step2 send msg                
                ret, str_data = self.send_message(msg)
                if (ret != ERR_SUCCESS):                    
                    break                
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break                                  
                
                event_rsp   = data[0]   
                obj         = data[1]
                event_rqst  = event                
                if (event_rsp - event_rqst != 1):
                    str_data    = obj.dict_ret["str_result"]
                    ret         = ERR_FAIL                    
                    break

                # status ok?
                if (obj.status == status_success):
                    str_data    = obj
                    ret         = ERR_SUCCESS
                    
                    break
                elif (obj.status == status_fail):
                
                    str_data = obj.dict_ret["str_result"]   # fail convert to str                    
                    ret = ERR_FAIL
                    break                
                            
                if (datetime.now() - start_time > timedelta(seconds=usercfg.WORKLIST_TIMEOUT)):
                    # timeout                    
                    str_data    = "timeout(>%s seconds)" %timeout
                    log.app_err(str_data)

                    ret         = ERR_FAIL
                    break                

                # wait
                sleep(usercfg.WORKLIST_EXEC_QUERY_SLEEP)
            
        except Exception, e:
            ret         = ERR_FAIL
            str_data    = e
            print_trace(e)         
        
        return ret, str_data         


    def process_alarm_inform(self, event, obj):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None
        
        for nwf in [1]:
                
            try:
                
                # step1 build msg
                ret, msg = self.build_alarm_inform_msg(event, obj)
                if (ret != ERR_SUCCESS):
                    str_data = msg
                    
                    break
            
                # step2 send msg
                ret, str_data = self.send_message(msg)
                if (ret != ERR_SUCCESS):                    
                    break              
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break
                
                # return code
                event_rsp   = data[0]     
                obj         = data[1] 
                event_rqst  = event               
                if (event_rsp - event_rqst == 1):
                    str_data    = obj
                    ret         = ERR_SUCCESS
                else:
                    ret         = ERR_FAIL                    
                    str_data    = obj.dict_ret["str_result"]
                        
            except Exception, e:
                ret         = ERR_FAIL
                str_data    = e
                print_trace(e)  
        
        return ret, str_data  


    def process_monitor_inform(self, event, obj):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None
        
        for nwf in [1]:
                
            try:
                
                # step1 build msg
                ret, msg = self.build_monitor_inform_msg(event, obj)
                if (ret != ERR_SUCCESS):
                    str_data = msg
                    
                    break
            
                # step2 send msg
                ret, str_data = self.send_message(msg)
                if (ret != ERR_SUCCESS):                    
                    break              
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break
                
                # return code
                event_rsp   = data[0]     
                obj         = data[1] 
                event_rqst  = event               
                if (event_rsp - event_rqst == 1):
                    str_data    = obj
                    ret         = ERR_SUCCESS
                else:
                    ret         = ERR_FAIL                    
                    str_data    = obj.dict_ret["str_result"]
                        
            except Exception, e:
                ret         = ERR_FAIL
                str_data    = e
                print_trace(e)  
        
        return ret, str_data  


          
    def process_query_cpe_info(self, sn=""):
        """

        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None
        
        for nwf in [1]:
                
            try:
                
                # step1 build msg
                ret, msg = self.build_query_cpe_info(sn)
                if (ret != ERR_SUCCESS):
                    str_data = msg
                    
                    break
            
                # step2 send msg                
                ret, str_data = self.send_message(msg)
                if (ret != ERR_SUCCESS):                    
                    break                
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break
                
                # return code
                event_rsp   = data[0]    
                obj         = data[1]   
                event_rqst  = EV_QUERY_CPE_INFO_RQST                
                if (event_rsp - event_rqst == 1):
                    # 对gui或者rf调用做区分
                    if self.reqeust_from_gui_flag:
                        str_data    = self._pares_gui_data(obj)
                    else:
                        str_data    = obj
                    ret         = ERR_SUCCESS
                else:
                    ret         = ERR_FAIL  
                    str_data    = obj.dict_ret["str_result"]
                
            except Exception, e:
                ret         = ERR_FAIL
                str_data    = e
                print_trace(e)  
        
        return ret, str_data    


    def process_update_cpe_info(self, sn="", modify_items={}):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None
        
        for nwf in [1]:
                
            try:
                
                # step1 build msg
                ret, msg = self.build_update_cpe_info(sn, modify_items)
                if (ret != ERR_SUCCESS):
                    str_data = msg
                    
                    break
            
                # step2 send msg                
                ret, str_data = self.send_message(msg)
                if (ret != ERR_SUCCESS):                    
                    break                
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break
                
                # return code
                event_rsp   = data[0]   
                obj         = data[1]
                event_rqst  = EV_MODIFY_CPE_INFO_RQST                
                if (event_rsp - event_rqst == 1):
                    
                    str_data    = obj
                    ret         = ERR_SUCCESS
                else:
                    ret         = ERR_FAIL  
                    str_data    = obj.dict_ret["str_result"]
                
            except Exception, e:
                ret         = ERR_FAIL
                str_data    = e
                print_trace(e)  
        
        return ret, str_data            
  

    def process_init_wait_eventcode(self, sn, include_eventcodes, exclude_eventcodes):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None
        
        for nwf in [1]:
                
            try:
                
                # step1 build msg
                ret, msg = self.build_init_wait_eventcode(sn, include_eventcodes, exclude_eventcodes)
                if (ret != ERR_SUCCESS):
                    str_data = msg
                    
                    break
            
                # step2 send msg                
                ret, str_data = self.send_message(msg)
                if (ret != ERR_SUCCESS):                    
                    break                
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break
                
                # return code
                event_rsp   = data[0]     
                obj         = data[1]
                event_rqst  = EV_WAIT_EVENTCODE_INIT_RQST                
                if (event_rsp - event_rqst == 1):
                
                    str_data    = obj 
                    ret         = ERR_SUCCESS
                    break  
                else:
                    ret         = ERR_FAIL  
                    str_data    = obj.dict_ret["str_result"]
                
            except Exception, e:
                ret         = ERR_FAIL
                str_data    = e
                print_trace(e)  
        
        return ret, str_data  


    def process_start_wait_eventcode(self, sn, wait_eventcode_id):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None
        
        for nwf in [1]:
                
            try:
                
                # step1 build msg
                ret, msg = self.build_start_wait_eventcode(sn, wait_eventcode_id)
                if (ret != ERR_SUCCESS):
                    str_data = msg
                    
                    break
            
                # step2 send msg                
                ret, str_data = self.send_message(msg)
                if (ret != ERR_SUCCESS):                    
                    break                
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break
                
                # return code
                event_rsp   = data[0]     
                obj         = data[1]
                event_rqst  = EV_WAIT_EVENTCODE_START_RQST                
                if (event_rsp - event_rqst == 1):
                
                    str_data    = obj 
                    ret         = ERR_SUCCESS
                    break  
                else:
                    ret         = ERR_FAIL  
                    str_data    = obj.dict_ret["str_result"]
                
            except Exception, e:
                ret         = ERR_FAIL
                str_data    = e
                print_trace(e)  
        
        return ret, str_data  


    def process_stop_wait_eventcode(self, sn, wait_eventcode_id):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None
        
        for nwf in [1]:
                
            try:
                
                # step1 build msg
                ret, msg = self.build_stop_wait_eventcode(sn, wait_eventcode_id)
                if (ret != ERR_SUCCESS):
                    str_data = msg
                    
                    break
            
                # step2 send msg                
                ret, str_data = self.send_message(msg)
                if (ret != ERR_SUCCESS):                    
                    break                
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break
                
                # return code
                event_rsp   = data[0]     
                obj         = data[1]
                event_rqst  = EV_WAIT_EVENTCODE_STOP_RQST                
                if (event_rsp - event_rqst == 1):
                    str_data    = obj 
                    ret         = ERR_SUCCESS
                    break 
                else:
                    ret         = ERR_FAIL  
                    str_data    = obj.dict_ret["str_result"]
                
            except Exception, e:
                ret         = ERR_FAIL
                str_data    = e
                print_trace(e)  
        
        return ret, str_data          


    def process_query_wait_eventcode(self, sn, wait_eventcode_id, timeout):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None


        try:
            
            start_time  = datetime.now()
            
            while(1):

                # step1 build msg
                ret, msg = self.build_query_wait_eventcode(sn, wait_eventcode_id)
                if (ret != ERR_SUCCESS):
                    str_data = msg
                    break
                            
                # step2 send msg                
                ret, str_data = self.send_message(msg)
                if (ret != ERR_SUCCESS):                    
                    break                
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break
                                                  
                event_rsp   = data[0]   
                obj         = data[1]                 
                event_rqst  = EV_WAIT_EVENTCODE_QUERY_RQST                
                if (event_rsp - event_rqst == 1):                    

                    str_data    = obj 
                    ret         = ERR_SUCCESS
                    break                                                 
                            
                if (datetime.now() - start_time > timedelta(seconds=timeout)):
                    # timeout
                    ret         = ERR_FAIL
                    str_data    = "timeout(>%s seconds)" %timeout
                    log.app_err(str_data)
                    
                    break                

                # wait
                sleep(usercfg.WAIT_EVENTCODE_QUERY_SLEEP)
            
        except Exception, e:
            ret         = ERR_FAIL
            str_data    = e
            print_trace(e)         
        
        return ret, str_data   


    def process_get_online_cpe(self, sn):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None
        
        for zsj in [1]:
                
            try:
                
                # step1 build msg
                ret, msg = self.build_get_online_cpe(sn)
                if (ret != ERR_SUCCESS):
                    str_data = msg
                    
                    break
            
                # step2 send msg                
                ret, str_data = self.send_message(msg)
                if (ret != ERR_SUCCESS):                    
                    break                
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break
                
                # return code
                event_rsp   = data[0]    
                obj         = data[1]   
                event_rqst  = EV_QUERY_ALL_ONLINE_CPE_RQST                
                if (event_rsp - event_rqst == 1):
                    
                    str_data    = obj.online_status
                    ret         = ERR_SUCCESS
                else:
                    ret         = ERR_FAIL  
                    str_data    = obj.dict_ret["str_result"]
                
            except Exception, e:
                ret         = ERR_FAIL
                str_data    = e
                print_trace(e)  
        
        return ret, str_data


    def process_close_tr069_acs(self):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None
        
        for nwf in [1]:
                
            try:
                
                # step1 build msg
                ret, msg = self.build_close_tr069_acs()
                if (ret != ERR_SUCCESS):
                    str_data = msg
                    
                    break
            
                # step2 send msg                
                ret, str_data = self.send_message(msg)
                if (ret != ERR_SUCCESS):                    
                    break                
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break
                
                # return code
                event_rsp   = data[0]     
                obj         = data[1]
                event_rqst  = EV_TR069_ACS_EXIT_RQST                
                if (event_rsp - event_rqst == 1):
                    str_data    = obj 
                    ret         = ERR_SUCCESS
                    break 
                else:
                    ret         = ERR_FAIL  
                    str_data    = obj.dict_ret["str_result"]
                
            except Exception, e:
                ret         = ERR_FAIL
                str_data    = e
                print_trace(e)  
        
        return ret, str_data   


    def process_query_version_is_ok(self, version):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None
        
        for nwf in [1]:
                
            try:
                
                # step1 build msg
                ret, msg = self.build_query_version_is_ok(version)
                if (ret != ERR_SUCCESS):
                    str_data = msg
                    
                    break
            
                # step2 send msg                
                ret, str_data = self.send_message(msg)
                if (ret != ERR_SUCCESS):                    
                    break                
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break
                
                # return code
                event_rsp   = data[0]     
                obj         = data[1]
                event_rqst  = EV_QUERY_VERSION_IS_OK_RQST                
                if (event_rsp - event_rqst == 1):
                    str_data    = obj 
                    ret         = ERR_SUCCESS
                    break 
                else:
                    ret         = ERR_FAIL  
                    str_data    = obj.dict_ret["str_result"]
                
            except Exception, e:
                ret         = ERR_FAIL
                str_data    = e
                print_trace(e)  
        
        return ret, str_data 


    def process_query_cpe_last_faults(self, sn):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None
        
        for nwf in [1]:
                
            try:
                
                # step1 build msg
                ret, msg = self.build_query_cpe_last_faults(sn)
                if (ret != ERR_SUCCESS):
                    str_data = msg
                    
                    break
            
                # step2 send msg                
                ret, str_data = self.send_message(msg)
                if (ret != ERR_SUCCESS):                    
                    break                
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break
                
                # return code
                event_rsp   = data[0]     
                obj         = data[1]
                event_rqst  = EV_QUERY_CPE_LAST_FAULTS_RQST                
                if (event_rsp - event_rqst == 1):
                    str_data    = obj 
                    ret         = ERR_SUCCESS
                    break 
                else:
                    ret         = ERR_FAIL  
                    str_data    = obj.dict_ret["str_result"]
                
            except Exception, e:
                ret         = ERR_FAIL
                str_data    = e
                print_trace(e)  
        
        return ret, str_data 
        

    def process_query_last_session_soap(self, sn):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None
        
        for nwf in [1]:
                
            try:
                
                # step1 build msg
                ret, msg = self.build_query_last_session_soap(sn)
                if (ret != ERR_SUCCESS):
                    str_data = msg
                    
                    break
            
                # step2 send msg                
                ret, str_data = self.send_message(msg)
                if (ret != ERR_SUCCESS):                    
                    break                
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break
                
                # return code
                event_rsp   = data[0]     
                obj         = data[1]
                event_rqst  = EV_QUERY_LAST_SESSION_SOAP_RQST                
                if (event_rsp - event_rqst == 1):
                    str_data    = obj 
                    ret         = ERR_SUCCESS
                    break 
                else:
                    ret         = ERR_FAIL  
                    str_data    = obj.dict_ret["str_result"]
                
            except Exception, e:
                ret         = ERR_FAIL
                str_data    = e
                print_trace(e)  
        
        return ret, str_data 


    def process_query_cpe_interface_version(self, sn):
        """
        """
        ret         = ERR_FAIL
        msg         = ""
        str_data    = ""
        data        = None
        
        for nwf in [1]:
                
            try:
                
                # step1 build msg
                ret, msg = self.build_query_cpe_interface_version(sn)
                if (ret != ERR_SUCCESS):
                    str_data = msg
                    
                    break
            
                # step2 send msg                
                ret, str_data = self.send_message(msg)
                if (ret != ERR_SUCCESS):                    
                    break                
                
                # step3 analyze msg
                ret, data = self.parse_msg(str_data)
                if (ret != ERR_SUCCESS):
                    str_data = data
                    
                    break
                
                # return code
                event_rsp   = data[0]     
                obj         = data[1]
                event_rqst  = EV_QUERY_CPE_INTERFACE_VERSION_RQST                
                if (event_rsp - event_rqst == 1):
                    str_data    = obj 
                    ret         = ERR_SUCCESS
                    break 
                else:
                    ret         = ERR_FAIL  
                    str_data    = obj.dict_ret["str_result"]
                
            except Exception, e:
                ret         = ERR_FAIL
                str_data    = e
                print_trace(e)  
        
        return ret, str_data 


    
    def send_message(self, msg, timeout=usercfg.SHORT_CONNECTION_TIMEOUT):
        """
        """
        if (self.ip and self.page and self.page):
            url = "http://%s:%s%s" %(self.ip, self.port, self.page)
        else:
            url = "http://%s:%s%s" %(usercfg.AGENT_HTTP_IP, usercfg.AGENT_HTTP_PORT, usercfg.USER_PAGE)


        httpclient1 = HttpClient(url, timeout)
        
        ret, str_data = httpclient1.send_message(msg)    

        return ret, str_data     


    def parse_msg(self, msg):
        """
        msg is from build_rpc_msg
        """
        ret         = ERR_FAIL
        data        = None
        event       = ""
        obj         = None
        
        for nwf in [1]:
        
            try:
                
                dict1   = eval(msg)
                event   = int(dict1[KEY_MESSAGE])
                
                key_msg_type = dict1[KEY_MESSAGE_TYPE]
                
                obj     = dict1[KEY_OBJECT]
                strio   = StringIO(obj)
                obj     = pickle.load(strio)            
                
                data    = (event, obj, key_msg_type)
            except Exception,e:
                data = e
                print_trace(e)        
            
            ret = ERR_SUCCESS
        
        return ret, data

    
    # 对服务器返回的cpe信息做解析，构建gui需要的数据
    def _pares_gui_data(self, obj):
        """
        """
        tmp_result = {}     
        
        soft_ver = obj.software_version
        hard_ver = obj.hardware_version
        con_url = obj.connection_request_url
        
        cwmp_version = obj.cwmp_version
        cpe_loginname = obj.cpe2acs_loginname
        cpe_loginpassword = obj.cpe2acs_loginpassword
        acs_loginname = obj.acs2cpe_loginname
        acs_loginpassword = obj.acs2cpe_loginpassword
        acs_url = obj.cpe2acs_url
        
        auth_type = obj.auth_type
        worklist_domains = obj.worklist_domain
        
        tmp_result["software_version"] = soft_ver
        tmp_result["hardware_version"] = hard_ver
        tmp_result["connection_request_url"] = con_url
        tmp_result["cwmp_version"] = cwmp_version
        tmp_result["acs_auth_cpe_username"] = cpe_loginname
        tmp_result["acs_auth_cpe_password"] = cpe_loginpassword
        tmp_result["cpe_auth_acs_username"] = acs_loginname
        tmp_result["cpe_auth_acs_password"] = acs_loginpassword
        tmp_result["acs_url"] = acs_url
        tmp_result["cpe_authtype"] = auth_type
        tmp_result["cwmp_version"] = cwmp_version
        tmp_result["worklist_domain"] = worklist_domains
        
        return tmp_result

