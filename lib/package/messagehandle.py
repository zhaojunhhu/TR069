# -*- coding: utf-8 -*-

# /*************************************************************************
#  Copyright (C), 2013-2014, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: messagehandle
#  class Event:
#        function: 定义升级服务器与客户端交互的消息结构和消息类型
#
#  classSwitchMessageTypeHandle:
#        function: 定义string和dict数据类型的转换和数据类型检查
#
#  class ConstructMessageHandle:
#        function: 构造客户端发送到服务器需要的消息体
#
#  class ParseMessageHandle:
#        function: 解析服务器与返回的升级相关消息体
#            
#  Author: ATT development group
#  version: V1.0
#  date: 2013.06.26
#  change log:
#
#  wangjun  20130626    created
#  lana     20130718    添加机器码生成函数，在消息字段中添加一个新的字段，用于存放机器码
#
# ***************************************************************************

import md5
import copy
#import wmi  #导入wmi会导致 apache2.2 模式下，返回500错误 delete by jias 20140702

import hashlib

import time
import os

def debug_output(message):
    """
    输出打印信息
    """
    cur_path = os.path.dirname(__file__)
    log_path = os.path.join(cur_path, "log")
    if not os.path.exists(log_path):
        os.mkdir(log_path, 0777)
        
    log_file = os.path.join(log_path, "messagehandle_log.txt")
    
    string = time.strftime('%Y-%m-%d %H:%M:%S ') + message + '\n'
    if isinstance(string, unicode):
        string = string.encode('utf-8')
    
    with open(log_file,'a+') as item :
            item.seek(os.SEEK_END )
            item.write(string)
    # 仅在调试时开启
    #print string


#-------------------------------------------------------------------------------------
def log(log_message):
    #debug_output((u"%s") % log_message)
    pass
    
def build_machine_number():
    """
    使用cpu序列号和bios序列号组建可以唯一标识本机的机器码
    """
    return "machine_number"
    """
    encrypt_str = ""
    obj = wmi.WMI()
    
    try:
        for cpu_obj in obj.Win32_Processor():
            encrypt_str = encrypt_str + cpu_obj.ProcessorId.strip()
        
    except Exception, e:
        log(u"get cpu serialnumber error: %s \n" % e )
    
    try:    
        for bios_obj in obj.Win32_BIOS():
            encrypt_str = encrypt_str + bios_obj.SerialNumber.strip()
    except Exception, e:
        log(u"get bios serialnumber error: %s \n" % e )
        
    machine_number = hashlib.md5(encrypt_str).hexdigest().upper()
    return machine_number
    """


class Event():
    
    #[client to server signal]
    # 定义消息类型
    MSG_TYPE_UPLOAD_INIT = "MSG_TYPE_UPLOAD_INIT"
    MSG_TYPE_UPLOAD_FILE = "MSG_TYPE_UPLOAD_FILE"
    MSG_TYPE_DOWNLOAD_FILE = "MSG_TYPE_DOWNLOAD_FILE"
    MSG_TYPE_UPGRADE_INFO_QUERY = "MSG_TYPE_UPGRADE_INFO_QUERY"
    
    # 定义事件类型
    # 请求
    MSG_EVENT_RQST = "MSG_EVENT_RQST"
    # 成功回应
    MSG_EVENT_SUC  = "MSG_EVENT_SUC"
    # 失败回应
    MSG_EVNET_FAIL = "MSG_EVNET_FAIL"

    # 消息结构字段
    KEY_MSG_TYPE = "KEY_MSG_TYPE"
    KEY_MSG_EVENT = "KEY_MSG_EVENT"
    KEY_MSG_PROPERTIES = "KEY_MSG_PROPERTIES"
    KEY_MSG_DATA = "KEY_MSG_DATA"
    KEY_MSG_MACHINE_NUM = "KEY_MSG_MACHINE_NUM"
    
    # 消息属性字段子项，根据消息类型选择需要的字段组建成字典
    TESTLIB_NAME = "TESTLIB_NAME"
    TESTLIB_VERSION = "TESTLIB_VERSION"
    BASED_ATTROBOT_VERSION = "BASED_ATTROBOT_VERSION"
    DATA_LEN = "DATA_LEN"
    ZIP_FILE_MD5 = "ZIP_FILE_MD5"
    TRANSFER_SERIAL = "TRANSFER_SERIAL"
    ERROR_INFO = "ERROR_INFO"
    #该标示用来标示库是否支持remote。#add by wangjun 20130702
    TESTLIB_REMOTE_FLAG="TESTLIB_REMOTE_FLAG"
    
    #添加基础测试库别名数据 #add by wangjun 20130813
    TESTLIB_ALIAS="TESTLIB_ALIAS"
    
    #[client check]
    #定义升级服务器IP,PORT,RUL,TIMEOUT LENGTH
    UPGRADE_SERVER_HTTP_IP='172.24.6.7'
    UPGRADE_SERVER_HTTP_PORT=8002
    
    UPGRADE_SERVER_HTTP_QUERT_URL='/upgrade'
    UPGRADE_SERVER_HTTP_QUERT_TIMEOUT=60
    
    UPGRADE_SERVER_HTTP_UPLOAD_URL='/upload'
    UPGRADE_SERVER_HTTP_UPLOAD_TIMEOUT=60
    
    UPGRADE_SERVER_HTTP_DOWNLOAD_URL='/download'
    UPGRADE_SERVER_HTTP_DOWNLOAD_TIMEOUT=60
    
     
    #定义客户端上传或下载文件时消息头的长度
    UPLOAD_OR_DOWNLOAD_MESSAGE_HEADER_FORMAT_LEN=512
    
    #定义客户端发送文件时一次读取文件数据的长度
    HTTP_SEND_MAX_LENGTH=1024*100
    
    #定义客户端成功和错误字典
    CLIENT_REQUEST_SUC="CLIENT_REQUEST_SUC"
    CLIENT_REQUEST_FAIL="CLIENT_REQUEST_FAIL"
    CLIENT_REQUEST_EXCEPT="CLIENT_REQUEST_EXCEPT"
#-------------------------------------------------------------------------------------



#-------------------------------------------------------------------------------------
class SwitchMessageTypeHandle(object):
    
    @staticmethod
    def check_msg_stream_type_is_dict(message):
        """
        check message data is dict instance
        """
        if (isinstance(message, dict)):
            return True
        
        return False
    
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
#-------------------------------------------------------------------------------------



#-------------------------------------------------------------------------------------
class ConstructMessageHandle():

    m_machine_num = ""

    @staticmethod
    def _construct_message_dict(in_msg_type,in_msg,in_msg_property,in_msg_data):
        """
        构造消息字典
        """
        msg_dict={}
        
        if not ConstructMessageHandle.m_machine_num:
            ConstructMessageHandle.m_machine_num = build_machine_number()
        
        msg_dict[Event.KEY_MSG_TYPE]=in_msg_type
        msg_dict[Event.KEY_MSG_EVENT]=in_msg
        msg_dict[Event.KEY_MSG_PROPERTIES]=in_msg_property
        msg_dict[Event.KEY_MSG_DATA]=in_msg_data
        msg_dict[Event.KEY_MSG_MACHINE_NUM]=ConstructMessageHandle.m_machine_num
    
        return msg_dict


    @staticmethod
    def _format_message_header(in_message):
        """
        格式化上传或下载文件消息头
        """
        new_message=SwitchMessageTypeHandle.switch_msg_stream_type_dict2str(in_message)
        
        out_message=new_message.ljust(Event.UPLOAD_OR_DOWNLOAD_MESSAGE_HEADER_FORMAT_LEN,'\0')
        return out_message
    
    
    @staticmethod
    def construct_update_info_query_post():
        """
        构造查询服务器配置消息
        """
        msg_dict=ConstructMessageHandle._construct_message_dict(Event.MSG_TYPE_UPGRADE_INFO_QUERY,
                                                            Event.MSG_EVENT_RQST,
                                                            None,
                                                            None)
                
        msg_str=str(msg_dict)

        return msg_str
        

    @staticmethod
    def construct_upload_init_post(in_testlib_name,in_testlib_ver,in_base_attrobot_ver,in_remote_flag,in_testlib_alias):
        """
        构造上传文件初始化消息
        """
        property_dict = {
            Event.TESTLIB_NAME:in_testlib_name,
            Event.TESTLIB_VERSION:in_testlib_ver,
            Event.BASED_ATTROBOT_VERSION:in_base_attrobot_ver,
            Event.TESTLIB_REMOTE_FLAG:in_remote_flag,
            
            #添加基础测试库别名数据 #add by wangjun 20130810 
            Event.TESTLIB_ALIAS:in_testlib_alias
        }

        msg_dict=ConstructMessageHandle._construct_message_dict(Event.MSG_TYPE_UPLOAD_INIT,
                                                            Event.MSG_EVENT_RQST,
                                                            property_dict,
                                                            None)
        
        msg_str=str(msg_dict)

        return msg_str
    
    
    @staticmethod
    def construct_upload_zipfile_post(in_transfer_serial,in_file_md5):
        """
        构造上传ZIP文件流消息
        """
        property_dict = {
            Event.TRANSFER_SERIAL:in_transfer_serial,
            Event.ZIP_FILE_MD5:in_file_md5
        }

        msg_dict=ConstructMessageHandle._construct_message_dict(Event.MSG_TYPE_UPLOAD_FILE,
                                                            Event.MSG_EVENT_RQST,
                                                            property_dict,
                                                            None)

        msg_str=ConstructMessageHandle._format_message_header(str(msg_dict))

        return msg_str
    

    @staticmethod
    def construct_download_post(in_testlib_name,in_testlib_ver):
        """
        构造下载文件消息
        """
        property_dict = {
            Event.TESTLIB_NAME:in_testlib_name,
            Event.TESTLIB_VERSION:in_testlib_ver
        }
        
        msg_dict=ConstructMessageHandle._construct_message_dict(Event.MSG_TYPE_DOWNLOAD_FILE,
                                                            Event.MSG_EVENT_RQST,
                                                            property_dict,
                                                            None)
        
        msg_str=str(msg_dict)
        
        return msg_str


    @staticmethod
    def construct_zipfile_md5(in_file_path):
        """
        获取文件的MD5
        """
        
        strMd5=''
        try:
            m = md5.md5()
            with open(in_file_path, 'rb') as fp:
                data = fp.read(Event.HTTP_SEND_MAX_LENGTH)
                while len(data)>0:
                    #log(u"%d" % len(data))
                    m.update(data)
                    data = fp.read(Event.HTTP_SEND_MAX_LENGTH)
            
            bet = True
            strMd5 = m.hexdigest()
            
            #转换成大写
            strMd5=strMd5.upper()
        except:
            bet = False
    
        return [bet, strMd5]
#-------------------------------------------------------------------------------------
    


#-------------------------------------------------------------------------------------
class ParseMessageHandle():
    
    @staticmethod
    def parse_message_data(in_message):
        """
        解析服务器返回的数据并数据项的形式返回
        """
        
        #检查数据是否是字典类型
        new_message_data=SwitchMessageTypeHandle.switch_msg_stream_type_str2dict(in_message)
        check_flag=SwitchMessageTypeHandle.check_msg_stream_type_is_dict(new_message_data)
        if not check_flag:
            return False, None

        #获取数据
        message_type=new_message_data.get(Event.KEY_MSG_TYPE)
        message_event=new_message_data.get(Event.KEY_MSG_EVENT)
        message_property_dict=new_message_data.get(Event.KEY_MSG_PROPERTIES)
        message_data=new_message_data.get(Event.KEY_MSG_DATA)

        #log((u"\n\n%s\n%s\n%s\n%s\n") % (message_type,message_event,message_property_dict,message_data))
        
        #检查数据是否是字典类型
        out_property_data=SwitchMessageTypeHandle.switch_msg_stream_type_str2dict(message_property_dict)
        check_flag=SwitchMessageTypeHandle.check_msg_stream_type_is_dict(out_property_data)
        if not check_flag:
            message_property_dict=None
        
        #返回数据列表及标志
        return True, [message_type, message_event, message_property_dict, message_data]


    @staticmethod
    def parse_update_info_query_response(in_response):
        """
        解析服务器返回查询消息数据
        """

        #存储数据结构说明
        """
        {"库名"：{"BASE_ATTROBOT版本号":[{'ZIP_FILE_MD5': 'FBD7894B3CB89DD90E98F5FEADF805F6', \
                                                     'TESTLIB_VERSION': 'v1.3.0'}, ]}, }
        """
                    
        #保存解析出来的数据
        property_dict={}
        property_base_attrobot_dict={}

        #解析服务器返回的数据
        rc_flag,rc_list=ParseMessageHandle.parse_message_data(in_response)
        if not rc_flag:
            return None
        
        message_type=rc_list[0]
        message_event=rc_list[1]
        message_property_dict=rc_list[2]
        message_data=rc_list[3]
        
        #log((u"\n\n----%s\n----%s\n----%s\n----%s\n") % (message_type,message_event,message_property_dict,message_data))
        
        if ( None == message_event or
            None == message_event or
            None == message_property_dict):
            return False, None
        
        if Event.MSG_EVENT_SUC==message_event:
            
            #获取服务器返回的库列表
            testlib_node_list=message_property_dict.keys()
            #log(u"%s\n") % testlib_node_list
            
            for lib_node in testlib_node_list:
                
                #log(u("%s") % lib_node)
                #log(u("\n-------------------------------------------"))

                #获取库节点返回的属性列表
                pro_node_list=message_property_dict.get(lib_node)
                #log((u"%s") %pro_node_list)
                
                property_base_attrobot_dict={}
                
                #获取属性节点返回的属性数据
                for pro_node in pro_node_list:

                    pro_testlib_ver=pro_node.get(Event.TESTLIB_VERSION)
                    #pro_testlib_md5=pro_node.get(Event.ZIP_FILE_MD5)
                    pro_base_attrobot_ver=pro_node.get(Event.BASED_ATTROBOT_VERSION)
                    
                    pro_testlib_remote_flag=pro_node.get(Event.TESTLIB_REMOTE_FLAG)
                    #log((u"%s\n%s\n%s\n") % (pro_testlib_ver,pro_base_attrobot_ver,pro_testlib_md5))

                    pro_testlib_alias=pro_node.get(Event.TESTLIB_ALIAS)
                    
                    pro_node_dict={
                        Event.TESTLIB_VERSION:pro_testlib_ver,
                        #Event.ZIP_FILE_MD5:pro_testlib_md5 #不需要md5数据，下载时，由服务器响应下载消息时带MD5数据
                        Event.TESTLIB_REMOTE_FLAG:pro_testlib_remote_flag,
                        
                        #添加基础测试库别名数据 #add by wangjun 20130813
                        Event.TESTLIB_ALIAS:pro_testlib_alias
                    }

                    #保存解析出来的属性数据到以BASE的ATTROBOT版本号为KEY的字典中
                    if pro_base_attrobot_ver in property_base_attrobot_dict:
                        pro_node_list=property_base_attrobot_dict.get(pro_base_attrobot_ver)
                        pro_node_list.append(pro_node_dict)
                    else:
                        pro_node_list=[pro_node_dict]
                    property_base_attrobot_dict[pro_base_attrobot_ver]=pro_node_list
                    
                    #保存以BASE的ATTROBOT版本号为KEY的字典中数据到以库名为KEY的字典中
                    property_dict[lib_node]=property_base_attrobot_dict
                
                #log(u"-------------------------------------------\n")


            #打印查询到的数据
            if False:#True:
                for tmp_lib_node in property_dict:
                            
                    log(u"\n-------------------------------------------")
                    log((u"库名：%s") % tmp_lib_node)
            
                    tmp_base_attrobot_ver_dict=property_dict.get(tmp_lib_node)
                    for temp_pro_node in tmp_base_attrobot_ver_dict:
                        
                        log(u"基于ATTROBOT版本号：%s" % temp_pro_node)
                        tmp_pro_list=tmp_base_attrobot_ver_dict.get(temp_pro_node)
                        for tmp_pro_node in tmp_pro_list:
                            log(u"库版本号：%s" % tmp_pro_node.get(Event.TESTLIB_VERSION))
        
                    log(u"-------------------------------------------\n")

            return True, property_dict
  
        else:

            return False, new_property_data.get(Event.ERROR_INFO)

        return False, None
    
    
    @staticmethod
    def parse_upload_init_response(in_response):
        """
        解析服务器返回上传文件初始化消息数据
        """

        #解析服务器返回的数据
        rc_flag,rc_list=ParseMessageHandle.parse_message_data(in_response)
        if not rc_flag:
            return None
        
        message_type=rc_list[0]
        message_event=rc_list[1]
        message_property_dict=rc_list[2]
        message_data=rc_list[3]
        
        #log((u"\n\n----%s\n----%s\n----%s\n----%s\n") % (message_type,message_event,message_property_dict,message_data))
        
        if ( None == message_event or
            None == message_event or
            None == message_property_dict):
            return False, None
        
        if Event.MSG_EVENT_SUC==message_event:
            
            return True, message_property_dict.get(Event.TRANSFER_SERIAL)
      
        else:
            return False, message_property_dict.get(Event.ERROR_INFO)
        
        return False, None

    
    @staticmethod
    def parse_upload_zipfile_response(in_response):
        """
        解析服务器返回上传文件消息数据
        """

        #解析服务器返回的数据
        rc_flag,rc_list=ParseMessageHandle.parse_message_data(in_response)
        if not rc_flag:
            return None
        
        message_type=rc_list[0]
        message_event=rc_list[1]
        message_property_dict=rc_list[2]
        message_data=rc_list[3]
        
        #log((u"\n\n----%s\n----%s\n----%s\n----%s\n") % (message_type,message_event,message_property_dict,message_data))
        
        if ( None == message_event or
            None == message_event or
            None == message_property_dict):
            return False, None
        
        if Event.MSG_EVENT_SUC==message_event:
            return True, None

        else:
            return False, message_property_dict.get(Event.ERROR_INFO)
        
        return False, None
    

    
    @staticmethod
    def parse_download_response(in_response):
        """
        解析服务器返回下载文件消息数据
        """

        #解析服务器返回的数据
        rc_flag,rc_list=ParseMessageHandle.parse_message_data(in_response)
        if not rc_flag:
            return None
        
        message_type=rc_list[0]
        message_event=rc_list[1]
        message_property_dict=rc_list[2]
        message_data=rc_list[3]
        
        #log((u"\n\n----%s\n----%s\n----%s\n----%s\n") % (message_type,message_event,message_property_dict,message_data))
        
        if ( None == message_event or
            None == message_event or
            None == message_property_dict):
            return False, None
        
        if Event.MSG_EVENT_SUC==message_event:
            return True, message_property_dict

        else:
            return False, message_property_dict.get(Event.ERROR_INFO)
        
        return False, None


    @staticmethod
    def get_response_message_header(in_message):
        """
        获取上传或下载文件消息头
        """
        #解析上传或下载文件消息头
        new_message=SwitchMessageTypeHandle.switch_msg_stream_type_dict2str(in_message)
        
        data_end_index=new_message.rfind('}')
        if data_end_index:
            out_message=new_message[0:data_end_index+1]
            log(u"%s\n" % out_message)
            
            return out_message
        else:
            return None
        
        
    @staticmethod    
    def get_response_event(in_response):
        """
        返回消息的类型
        """
        #解析服务器返回的数据
        rc_flag,rc_list=ParseMessageHandle.parse_message_data(in_response)
        if not rc_flag:
            return None
        
        message_type=rc_list[0]
        #message_event=rc_list[1]
        #message_property_dict=rc_list[2]
        #message_data=rc_list[3]
        
        return message_type
    
#-------------------------------------------------------------------------------------
