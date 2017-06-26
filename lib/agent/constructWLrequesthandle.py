#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: ConstructWLRequestHandle
#  function: construct worklist reserve/execute start/execute/execute finish request message data
#  Author: ATT development group
#  version: V1.0
#  date: 2013.4.15
#  change log:
#  wangjun     20130415    created
#
# ***************************************************************************

import pickle
from cStringIO import StringIO
import messageprocessing

import TR069.lib.common.logs.log as log
import TR069.lib.common.event as event


class ConstructWLRequestHandle(object):
    """
    construct worklist reserve/execute start/execute/execute finish request message data
    """
    CONSTRUCT_WLREQUEST_SUC            = 0
    CONSTRUCT_WLREQUEST_FAIL           = -1
    
    @staticmethod
    def construct_WLreserve_request(message):
        """
        function description:
                            construct worklist reserve request message data
        parameters:
                  message
        return:
                success--build_obj.message
                localFail--None
        """
        # parse input message key_obj data
        tmp_obj = message.get(event.KEY_OBJECT)
        strio = StringIO(tmp_obj)
        msg_key_obj = pickle.load(strio)

        tmp_worklistid=msg_key_obj.id_

        # build message
        ret, build_obj = ConstructWLRequestHandle.build_WLreserve_msg(tmp_worklistid)
        if ret == ConstructWLRequestHandle.CONSTRUCT_WLREQUEST_FAIL:
            return None
        
        return build_obj.message


    @staticmethod
    def construct_WLexec_start_request(message):
        """
        function description:
                            construct worklist execute start request message data
        parameters:
                  message
        return:
                success--build_obj.message
                localFail--None
        """
        # parse input message key_obj data
        tmp_obj = message.get(event.KEY_OBJECT)
        strio = StringIO(tmp_obj)
        msg_key_obj = pickle.load(strio)

        tmp_worklistid=msg_key_obj.id_
        tmp_wlbind_sn=msg_key_obj.sn
        
        # build message
        ret, build_obj = ConstructWLRequestHandle.build_WLexec_start_msg(tmp_worklistid,tmp_wlbind_sn)
        if ret == ConstructWLRequestHandle.CONSTRUCT_WLREQUEST_FAIL:
            return None
        
        return build_obj.message
    
    
    @staticmethod
    def construct_WLexec_request(message):
        """
        function description:
                             construct worklist execute request message data
        parameters:
                  message
        return:
                success--build_obj.message
                localFail--None
        """
        # parse input message key_obj data
        tmp_obj = message.get(event.KEY_OBJECT)
        strio = StringIO(tmp_obj)
        msg_key_obj = pickle.load(strio)

        # build message
        ret, build_obj = ConstructWLRequestHandle.build_WLexec_msg(msg_key_obj)
        if ret == ConstructWLRequestHandle.CONSTRUCT_WLREQUEST_FAIL:
            return None

        return build_obj.message

    
    @staticmethod
    def construct_WLexec_finish_request(message):
        """
        function description:
                             construct worklist execute finish request message data
        parameters:
                  message
        return:
                success--build_obj.message
                localFail--None
        """
        # parse input message key_obj data
        tmp_obj = message.get(event.KEY_OBJECT)
        strio = StringIO(tmp_obj)
        msg_key_obj = pickle.load(strio)

        tmp_worklistid=msg_key_obj.id_
        tmp_execute_status=msg_key_obj.execute_status #EV_WORKLIST_EXECUTE_FAIL or EV_WORKLIST_EXECUTE_PSP #changed by 20130530
        tmp_dict_ret=msg_key_obj.dict_ret
        
        # build message
        ret, build_obj = ConstructWLRequestHandle.build_WLexec_finish_msg(tmp_worklistid,
                                                       tmp_execute_status,
                                                       tmp_dict_ret)
        
        if ret == ConstructWLRequestHandle.CONSTRUCT_WLREQUEST_FAIL:
            return None

        return build_obj.message
    
    
    #add by wangjun 20130525
    @staticmethod
    def construct_WLexec_request_except(wl_id,except_info):
        """
        function description:
                             construct worklist execute request except message data
        parameters:
                  message, except_info
        return:
                success--build_obj.message
                localFail--None
        """

        tmp_worklistid=wl_id
        tmp_execute_status=event.EV_WORKLIST_EXECUTE_FAIL #event.EV_WORKLIST_EXECUTE_PSP
        tmp_dict_ret=except_info
        
        # build message
        ret, build_obj = ConstructWLRequestHandle.build_WLexec_finish_msg(tmp_worklistid,
                                                       tmp_execute_status,
                                                       tmp_dict_ret)
                                                       
        if ret == ConstructWLRequestHandle.CONSTRUCT_WLREQUEST_FAIL:
            return None

        return build_obj.message
    
    
    @staticmethod   
    def build_WLreserve_msg(wroklistid):
        """
        function description:
                             build worklist reserve message
        parameters:
                   wroklistid
        return:
                success--(CONSTRUCT_WLREQUEST_SUC,build_obj)
                localFail--(CONSTRUCT_WLREQUEST_FAIL,err_info)
        """
        
        # create MessageProcessing object to build message
        build_obj = messageprocessing.MessageProcessing()
        
        build_obj.key_msg_type = event.EVENT_WORKLIST_GROUP
        build_obj.key_queue = event.QUEUE_WAIT
        build_obj.key_event =  event.EV_WORKLIST_RESERVE_RQST
        build_obj.key_priority_level =  event.PRIORITY_NORMAL
        
        # build key_object 
        tmp_obj = event.MsgWorklistReserve(wroklistid)
        
        build_obj.key_obj = tmp_obj
        
        ret, ret_info = build_obj.build_message()
        if ret == messageprocessing.MSG_PROCESS_FAIL:
            err_info = ret_info
            log.run_err(err_info)
            return ConstructWLRequestHandle.CONSTRUCT_WLREQUEST_FAIL, err_info
        
        return ConstructWLRequestHandle.CONSTRUCT_WLREQUEST_SUC, build_obj

    
    @staticmethod   
    def build_WLexec_start_msg(wroklistid,wlbind_sn):
        """
        function description:
                             build worklist exec start request message
        parameters:
                   worklistid
        return:
                success--(CONSTRUCT_WLREQUEST_SUC,build_obj)
                localFail--(CONSTRUCT_WLREQUEST_FAIL,err_info)
        """
        # create MessageProcessing object to build message
        build_obj = messageprocessing.MessageProcessing()
        
        build_obj.key_msg_type = event.EVENT_WORKLIST_GROUP
        build_obj.key_queue = event.QUEUE_WAIT
        build_obj.key_event =  event.EV_WORKLIST_EXEC_START_RQST
        build_obj.key_priority_level =  event.PRIORITY_HIGH #PRIORITY_NORMAL

        # added by wangjun 2014-4-19
        build_obj.key_sn=wlbind_sn
        
        # build key_object 
        tmp_obj = event.MsgWorklistExecStart(wroklistid)

        build_obj.key_obj = tmp_obj
        
        ret, ret_info = build_obj.build_message()
        if ret == messageprocessing.MSG_PROCESS_FAIL:
            err_info = ret_info
            log.run_err(err_info)
            return ConstructWLRequestHandle.CONSTRUCT_WLREQUEST_FAIL, err_info
        
        return ConstructWLRequestHandle.CONSTRUCT_WLREQUEST_SUC, build_obj
    
    
    @staticmethod   
    def build_WLexec_msg(worklistdataobject):
        """
        function description:
                             build worklist exec message
        parameters:
                   worklistdataobject
        return:
                success--(CONSTRUCT_WLREQUEST_SUC, build_obj)
                localFail--(CONSTRUCT_WLREQUEST_FAIL, err_info)
        """
        # create MessageProcessing object to build message
        build_obj = messageprocessing.MessageProcessing()
        
        build_obj.key_msg_type = event.EVENT_WORKLIST_GROUP
        build_obj.key_queue = event.QUEUE_WAIT
        build_obj.key_event =  event.EV_WORKLIST_EXECUTE_RQST
        build_obj.key_priority_level =  event.PRIORITY_NORMAL
        
        # build key_object 
        build_obj.key_obj = worklistdataobject
        
        ret, ret_info = build_obj.build_message()
        if ret == messageprocessing.MSG_PROCESS_FAIL:
            err_info = ret_info
            log.run_err(err_info)
            return ConstructWLRequestHandle.CONSTRUCT_WLREQUEST_FAIL, err_info
        
        return ConstructWLRequestHandle.CONSTRUCT_WLREQUEST_SUC, build_obj
    
    
    @staticmethod   
    def build_WLexec_finish_msg(wroklistid, rsp_event, dict_ret):
        """
        function description:
                             build worklist exec finish message
        parameters:
                    wroklistid, rsp_event
        return:
                success--(CONSTRUCT_WLREQUEST_SUC,build_obj)
                localFail--(CONSTRUCT_WLREQUEST_FAIL,err_info)
        """
        # create MessageProcessing object to build message
        build_obj = messageprocessing.MessageProcessing()
        
        build_obj.key_msg_type = event.EVENT_WORKLIST_GROUP
        build_obj.key_queue = event.QUEUE_WAIT
        build_obj.key_event =  event.EV_WORKLIST_EXEC_FINISH_RQST
        build_obj.key_priority_level =  event.PRIORITY_NORMAL

        # build key_object 
        tmp_obj = event.MsgWorklistExecFinish(wroklistid, rsp_event,dict_ret)

        build_obj.key_obj = tmp_obj
        
        ret, ret_info = build_obj.build_message()
        if ret == messageprocessing.MSG_PROCESS_FAIL:
            err_info = ret_info
            log.run_err(err_info)
            return ConstructWLRequestHandle.CONSTRUCT_WLREQUEST_FAIL, err_info
        
        return ConstructWLRequestHandle.CONSTRUCT_WLREQUEST_SUC, build_obj
    
    
    @staticmethod  
    def get_WL_type(message):
        """
        get worklist type
        """
        
        # parse input message key_obj data
        tmp_obj = message.get(event.KEY_OBJECT)
        strio = StringIO(tmp_obj)
        msg_key_obj = pickle.load(strio)

        tmp_wlbind_type=msg_key_obj.type_
        
        return tmp_wlbind_type
        
        