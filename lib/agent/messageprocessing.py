#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: messageprocessing
#  function: provide API build message by user input, and handle response msg
#  Author: ATT development group
#  version: V1.0
#  date: 2012.11.14
#  change log:
#  lana     20121114     created
#  wangjun  20130718     消息体添加KEY_SEQUENCE属性
# ***************************************************************************


import pickle
from cStringIO import StringIO
import random
import datetime

import TR069.lib.common.logs.log as log
import TR069.lib.common.event as event


MSG_PROCESS_SUC = 0
MSG_PROCESS_FAIL = -1


class MessageProcessing(object):
    """
    build message by user input, and handle response msg
    """
    
    def __init__(self):
        """
        initial
        """
        self.key_msg_type = None       # KEY_MESSAGE_TYPE value
        self.key_obj = None            # KEY_OBJECT value
        self.key_queue = None          # KEY_QUEUE value 
        self.key_sn = None             # KEY_SN value
        self.key_event = None          # KEY_MESSAGE value
        
        #add by wangjun 2013-04-16
        self.key_priority_level = None  # KEY_PRIORITY_LEVEL value
        
        #add by wangjun 20130525
        self.key_sender = None  # KEY_SENDER value
        
        #add by wangjun 20130715
        self.key_sequence=None # KEY_SEQUENCE value
        
        self.message = None            # message
        

    #add by wangjun 20130716
    @staticmethod
    def construct_sequence_id(in_sender):
        """
        构建sequence id
        """
        sequence_id=""
        
        dt_obj=datetime.datetime.now()
        random_number= random.randrange(10000000,100000000) 
        sequence_id=("%s_SEQUENCE_%s_%s_%s" % (in_sender,dt_obj.date(),dt_obj.time(),random_number))
        
        return sequence_id.upper()#.lower()
    
    
    def build_message(self):
        """
        build message
        """
        ret = MSG_PROCESS_SUC
        
        if self.key_msg_type == None or self.key_obj == None or self.key_event == None:
            err_info = "Message must including msg_type, key_obj, and msg_event!"
            log.run_err(err_info)
            return MSG_PROCESS_FAIL, err_info
        
        # if don't set KEY_QUEUE value, set default value "WAIT" 
        if self.key_queue == None:
            self.key_queue = event.QUEUE_WAIT
        
        # build dict structure    
        tmp_dict = {}
        
        tmp_dict[event.KEY_MESSAGE_TYPE] =  self.key_msg_type
        tmp_dict[event.KEY_MESSAGE] =  self.key_event
        tmp_dict[event.KEY_QUEUE] =  self.key_queue
        tmp_dict[event.KEY_SN] =  self.key_sn
        
        #add by wangjun-2013-04-16
        if self.key_priority_level == None:
            self.key_priority_level = event.PRIORITY_NORMAL

        tmp_dict[event.KEY_PRIORITY_LEVEL] =  self.key_priority_level

        #add by wangjun-20130525
        if self.key_sender == None:
            self.key_sender = event.KEY_SENDER_AGENT
            
        tmp_dict[event.KEY_SENDER] =  self.key_sender

        #add by wangjun 20130715
        tmp_dict[event.KEY_SEQUENCE] =  MessageProcessing.construct_sequence_id(self.key_sender)
        
        # pickle KEY_OBJECT value
        try:
            strio = StringIO()
            pickle.dump(self.key_obj, strio)
            tmp_dict[event.KEY_OBJECT] =  strio.getvalue()
            
        except Exception,e:
            err_info = "pickle event.KEY_OBJECT occurs error:%s" % e
            log.run_err(err_info)
            return MSG_PROCESS_FAIL, err_info
        
        self.message = str(tmp_dict)
        
        ret_info = "build message success"
        
        return ret, ret_info
        

    def parse_message(self):
        """
        parse message
        """
        
        ret = MSG_PROCESS_SUC
        
        if not self.message:
            err_info = "The message is empty, don't need to parse!"
            log.run_err(err_info)
            return MSG_PROCESS_FAIL, err_info
            
        
        # convert type of message, from string to dict
        try:
            dict_msg = eval(self.message)
        except Exception,e:
            err_info = "eval message occurs error:%s" % e
            log.run_err(err_info)
            return MSG_PROCESS_FAIL, err_info
        
        # parse dict items
        self.key_event = dict_msg.get(event.KEY_MESSAGE)
        self.key_msg_type = dict_msg.get(event.KEY_MESSAGE_TYPE)
        self.key_sn = dict_msg.get(event.KEY_SN)
        self.key_queue = dict_msg.get(event.KEY_QUEUE)
        
        #add by wangjun-2013-04-16
        self.key_priority_level=dict_msg.get(event.KEY_PRIORITY_LEVEL) 
        
        #add by wangjun-20130525
        self.key_sender=dict_msg.get(event.KEY_SENDER)
        
        #add by wangjun 20130715
        self.key_sequence=dict_msg.get(event.KEY_SEQUENCE)
        
        # unpickle KEY_OBJECT value
        try:
            tmp_obj = dict_msg.get(event.KEY_OBJECT)
            strio = StringIO(tmp_obj)
            self.key_obj = pickle.load(strio)
            
        except Exception,e:
            err_info = "Unpickle event.KEY_OBJECT occurs error:%s" % e
            log.run_err(err_info)
            return MSG_PROCESS_FAIL, err_info
        
        ret_info = "parse message success" 
        return ret, ret_info