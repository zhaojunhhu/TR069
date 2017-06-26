#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: MessageSequenceManagement
#  function: management MessageSequence object
#  Author: ATT development group
#  version: V1.0
#  date: 2013.4.15
#  change log:
#  wangjun  20130716     create
#  wangjun 20130725      修改消息ID节点失效时间太短的问题。现改为60分钟。
#  wangjun 20130726      修改消息ID节点失效时间太长的问题。现改为20分钟。
#  wangjun 20130823      修改中文打印消息为英文，因为在CMD窗口模式中文显示无乱码，不方便浏览。
# ***************************************************************************

import time
import random
import datetime
import threading

DEBUG=False

if not DEBUG:
    import responseclient
    import TR069.lib.common.logs.log as log
    import TR069.lib.common.event as event


dict_sequence_object = {}                        # {in_sequence: MessageSequence object}
dict_sequence_object_lock = threading.Lock()     # used to lock dict_sequence_object
thread_sequence_object_dict_management_handle=None  #管理MessageSequence对象时间有效性线程句柄



def log_out(string):
    if DEBUG:
        print ("%s" % string)
    else:
       log.debug_info(string)


class MessageSequence(object):
    
    #定义消息标示3种状态
    MSG_SEQUENCE_INIT="MSG_SEQUENCE_INIT"
    MSG_SEQUENCE_TRY="MSG_SEQUENCE_TRY"
    MSG_SEQUENCE_FINISH="MSG_SEQUENCE_FINISH"
    MSG_SEQUENCE_CONN_LOSE="MSG_SEQUENCE_CONN_LOSE"
    
    #定义失效时间长度
    SEQUENCE_NODE_INVALID_TIME_LENGTH=60*20
    
    def __init__(self, in_sequence, in_conn):
        """
        初始化消息令牌
        """
        self.sequence=in_sequence
        
        self.conn_list=[]
        self.conn_list.append(in_conn)

        self.status=MessageSequence.MSG_SEQUENCE_INIT
        self.response_data=None
        
        #self.init_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S' )
        self.init_time_object=datetime.datetime.now()
       
        
    def get_sequence_init_time_object(self):
        """
        返回初始化对象时间
        """
        return self.init_time_object

    
    def set_sequence_status_to_try(self,in_conn):
        """
        修改消息状态
        """
        self.status=MessageSequence.MSG_SEQUENCE_TRY
        self.conn_list.append(in_conn)
       
       
    def get_sequence_status(self):
        """
        返回消息状态
        """
        return self.status
        
        
    def get_sequence_id(self):
        """
        返回消息sequence id
        """
        return self.sequence
    
    
    
    def get_conn_handle_list(self):
        """
        返回消息client连接句柄列表
        """
        return self.conn_list
        
        
    def clear_conn_handle_list(self):
        """
        清空消息client连接句柄列表
        """
        self.conn_list=[]
    
    
    def set_sequence_response_data(self, in_response_data, in_send_suc_flag):
        """
        保存消息处理结果数据
        """
        if True == in_send_suc_flag:
            self.status=MessageSequence.MSG_SEQUENCE_FINISH
        else:
            self.status=MessageSequence.MSG_SEQUENCE_CONN_LOSE
            
        self.response_data=in_response_data
        
        
    def get_sequence_response_data(self):
        """
        返回消息处理结果数据
        """
        return self.response_data



class MessageSequenceManagement(object):
    
    @staticmethod    
    def insert_message_sequence_obj(in_sequence, in_conn):
        """
        添加对消息唯一标示进行处理
        """
        
        #启动MessageSequence节点时效性管理线程
        start_message_sequence_object_management_thread()
        
        if DEBUG:
            log_out("\n")
        
        #查找in_sequence是否纯正处理对象
        sequence_obj_handle=MessageSequenceManagement.get_message_sequence_obj_handle(in_sequence)
        if None != sequence_obj_handle:
            
            log_out("Sequence ID：%s" % in_sequence)
            
            #获取消息的状态
            sequence_obj_status=sequence_obj_handle.get_sequence_status()
            
            if (MessageSequence.MSG_SEQUENCE_INIT == sequence_obj_status or
                MessageSequence.MSG_SEQUENCE_TRY == sequence_obj_status):
                
                log_out("Sequence object(%s) is exist, method status is METHOD_SEQUENCE_INIT or METHOD_SEQUENCE_TRY" % in_sequence)
                
                #更新消息的状态为TRY，INIT之后并没有得到处理结果
                sequence_obj_handle.set_sequence_status_to_try(in_conn)
            
                #不再向下传递消息请求
                return False
            
            elif (MessageSequence.MSG_SEQUENCE_FINISH == sequence_obj_status or
                  MessageSequence.MSG_SEQUENCE_CONN_LOSE == sequence_obj_status):
                
                log_out("Sequence object(%s) is exist, method status is MSG_SEQUENCE_FINISH, response buf finish data to client" % in_sequence)
                
                #直接回复客户端消息处理结果
                sequence_obj_reponse_data=sequence_obj_handle.get_sequence_response_data()
                
                if not DEBUG:
                    responseclient.ResponseClientHandle.handle_send_response(sequence_obj_reponse_data,in_conn)
                
                #不再向下传递消息请求
                return False
        else:
            log_out("Create sequence object, sequence=%s" % in_sequence)
            
            #创建新的消息对象，并保存到列表中
            sequence_obj_handle=MessageSequenceManagement.new_message_sequence_obj(in_sequence, in_conn)
        
        #继续向下分发消息处理
        return True

      
    @staticmethod  
    def finish_message_sequence_obj(in_conn, in_response_data, in_send_suc_flag):
        """
        更新处理结果到in_conn对应的对象中
        """
        #查找in_conn是否存在正在处理对象
        if not in_conn:
            #错误
            log_out("Save method response data input in_conn is None")
            return False
        
        #获取conn连接句柄获取该句柄对应的MessageSequence对象句柄
        sequence_obj_handle=MessageSequenceManagement.get_message_sequence_obj_handle_from_conn_handle(in_conn)
        if None != sequence_obj_handle:
            
            #获取消息ID
            in_sequence=sequence_obj_handle.get_sequence_id()
            log_out("Save method response data to sequence(%s) object" % in_sequence)
            
            #将处理结果数据保存到in_conn对应的对象中
            sequence_obj_handle.set_sequence_response_data(in_response_data, in_send_suc_flag)
            
            #add by wangjun 20130729
            #将响应结果发送给消息ID的其他重复的连接
            out_conn_list=sequence_obj_handle.get_conn_handle_list()
            out_conn_list.remove(in_conn)
            MessageSequenceManagement.send_response_data_to_sequence_obj_other_conn_handle(out_conn_list,in_response_data)
            
            #清空消息client连接句柄列表
            sequence_obj_handle.clear_conn_handle_list()
            
            return True
        
        else:
            #错误
            log_out("Not find in_conn link sequence object")
            return False
        


    @staticmethod    
    def send_response_data_to_sequence_obj_other_conn_handle(in_conn_list,in_response_data):
        """
        将响应结果发送给消息ID的其他重复的连接
        """

        log_out("send_response_data_to_sequence_obj_other_conn_handle start, in_conn_list count=%d" % len(in_conn_list))
        
        for conn in in_conn_list:   
        
            #检查当前系统中有效的连接接句柄总数
            if not DEBUG:
                if 0 == responseclient.g_http_client_count:
                    log_out("client connected handle not found, responseclient.g_http_client_count=%d" % responseclient.g_http_client_count)
                    return
            
            if conn:
                
                if not DEBUG:
                    send_message_event_string=responseclient.ResponseClientHandle.get_msg_event_number_string(in_response_data)
                    log_out("Agent send message(%s) to client ipaddress=%s" % (send_message_event_string, responseclient.ResponseClientHandle.get_client_ipaddress(conn)) )
                
                try:
                    #发送消息到client
                    conn.write(str(in_response_data))
                    conn.finish()
                    
                    #断开连接
                    if conn.transport:
                        conn.transport.loseConnection()
                
                except Exception, e:
                    err_info = "Agent send message occurs exception: %s" % e
                    log_out(err_info)
                    
                    
                #更新连接接句柄总数，成功send一次，接接句柄总数减一
                if not DEBUG:
                    if responseclient.g_http_client_count>0:
                        responseclient.g_http_client_count-=1
                        log_out("loseConnection: Agent HTTP connected client count: %d" % responseclient.g_http_client_count)
                
        log_out("send_response_data_to_sequence_obj_other_conn_handle end")
        
        
        
    @staticmethod    
    def new_message_sequence_obj(in_sequence, in_conn):
        """
        创建对象
        """
        global dict_sequence_object
        global dict_sequence_object_lock
        
        sequence_obj_handle = MessageSequence(in_sequence, in_conn)

        dict_sequence_object_lock.acquire()
        dict_sequence_object[in_sequence] = sequence_obj_handle
        dict_sequence_object_lock.release()
        
        return sequence_obj_handle


    @staticmethod    
    def get_message_sequence_obj_handle(in_sequence):
        """
        获取对象句柄
        """
        global dict_sequence_object
        global dict_sequence_object_lock
        
        dict_sequence_object_lock.acquire()

        sequence_obj_handle=None
        if in_sequence in dict_sequence_object:
            sequence_obj_handle = dict_sequence_object[in_sequence]    # get this in_sequence's MessageSequence object

        dict_sequence_object_lock.release()

        return sequence_obj_handle


    @staticmethod    
    def get_message_sequence_obj_handle_from_conn_handle(in_conn):
        """
        通过HTTP连接句柄获取该句柄对应的MessageSequence对象句柄
        """
        global dict_sequence_object
        global dict_sequence_object_lock
        
        dict_sequence_object_lock.acquire()

        sequence_obj_handle=None
        for in_sequence in dict_sequence_object:
            tmp_sequence_obj_handle = dict_sequence_object[in_sequence]    # get this in_sequence's MessageSequence object
            
            if in_conn in tmp_sequence_obj_handle.get_conn_handle_list():
                sequence_obj_handle=tmp_sequence_obj_handle
                break
            
        dict_sequence_object_lock.release()

        return sequence_obj_handle
    
    
    @staticmethod
    def delete_invalid_message_sequence_obj():
        """
        检查节点的时效，删除过期的MessageSequence对象
        """
        
        global dict_sequence_object
        global dict_sequence_object_lock
        
        while 1:
            
            #获取当前系统时间
            temp_current_time_object=datetime.datetime.now()
            
            if DEBUG:
                log_out("\n")
                
            #log_out("management thread: current: %s" % temp_current_time_object.strftime('%Y-%m-%d %H:%M:%S' ))
            
            #加锁
            dict_sequence_object_lock.acquire()
            
            #遍历MessageSequence对象
            dict_sequence_object_list = dict_sequence_object.keys()
            #log_out("management thread: sequence object count: %d" % len(dict_sequence_object_list))
            for in_sequence in dict_sequence_object_list:
                    
                    #获取MessageSequence对象句柄
                    sequence_obj_handle = dict_sequence_object[in_sequence]
                    
                    #获取MessageSequence对象初始化时间
                    temp_sequence_init_time_object=sequence_obj_handle.get_sequence_init_time_object()
                    #log_out("management thread: sequence init time: %s" % temp_sequence_init_time_object.strftime('%Y-%m-%d %H:%M:%S'))
                    
                    if not temp_sequence_init_time_object:
                        continue
                    
                    #获取MessageSequence对象存在的时长
                    time_difference_seconds=(temp_current_time_object - temp_sequence_init_time_object).seconds
                    if time_difference_seconds >= (int)(MessageSequence.SEQUENCE_NODE_INVALID_TIME_LENGTH):
                        #清楚过期的MessageSequence对象
                        dict_sequence_object.pop(in_sequence)
                        #log_out("management thread: delete sequence object,sequence=%s" % in_sequence)
                        
                    else:
                        continue
                    
            #解锁       
            dict_sequence_object_lock.release()
            
            #等待1分钟再重新检查
            time.sleep(60)
        
        
        #还原thread_sequence_object_dict_management_handle 句柄
        global thread_sequence_object_dict_management_handle
        thread_sequence_object_dict_management_handle=None
        


def start_message_sequence_object_management_thread():
    """
    启动管理MessageSequence对象时间有效性线程
    """
    global thread_sequence_object_dict_management_handle
    if not thread_sequence_object_dict_management_handle:
        thread_sequence_object_dict_management_handle = threading.Thread(target=MessageSequenceManagement.delete_invalid_message_sequence_obj)
        thread_sequence_object_dict_management_handle.setDaemon(True)
        thread_sequence_object_dict_management_handle.start()

    return



    

def test():
    """
    测试
    """
    
    def construct_sequence_id(in_sender):
        """
        构建sequence id
        """
        sequence_id=""
            
        dt_obj=datetime.datetime.now()
        random_number= random.randrange(10000000,100000000) 
        sequence_id=("%s_SEQUENCE_%s_%s_%s" % (in_sender,dt_obj.date(),dt_obj.time(),random_number))
            
        return sequence_id.upper()#.lower()

    in_sequence=construct_sequence_id("AGENT")
    in_conn=None
    MessageSequenceManagement.insert_message_sequence_obj(in_sequence,in_conn)
    
    time.sleep(30)
    in_sequence=construct_sequence_id("AGENT")
    MessageSequenceManagement.insert_message_sequence_obj(in_sequence,in_conn)
    
    insert_count=2
    while 1:
        time.sleep(60)
        
        if insert_count<10:
            in_sequence=construct_sequence_id("AGENT")
            MessageSequenceManagement.insert_message_sequence_obj(in_sequence,in_conn)
            insert_count +=1

    nID = raw_input("Press any key to end...")
    
    
if __name__ == '__main__':
    test()

