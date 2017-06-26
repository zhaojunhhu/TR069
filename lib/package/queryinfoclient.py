# -*- coding: utf-8 -*-

# /*************************************************************************
#  Copyright (C), 2013-2014, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: queryinfoclient
#  function: 实现向升级服务器查询版本相关信息
#  Author: ATT development group
#  version: V1.0
#  date: 2013.06.26
#  change log:
#
#  wangjun  20130626    created
#  wangjun  20130715    修改版本号匹配规则
#  lana     20130716    去掉多余的导入模块,优化代码结构
# 
# ***************************************************************************

import threading
import httplib
import copy

import package.messagehandle  as messagehandle

#包含解析查询回来的数据，返回版本数据
from parsequeryvesioninfo import ParseQueryVesionInfo


#定义全局变量来保存从服务器上查询到的版本数据
#存储数据结构说明
#====================================================================================
#{"库名"：{"BASE_ATTROBOT版本号":[{'TESTLIB_VERSION': 'v1.3.0'}, ]}, {'TESTLIB_VERSION': 'v1.1.0'}, ]}}
#====================================================================================


#定义一个单例模式方法
class Singleton(object):
    """
    并在将一个类的实例绑定到类变量_instance上,   
    如果cls._instance为None说明该类还没有实例化过,实例化该类,并返回   
    如果cls._instance不为None,直接返回cls._instance
    """
    def __new__(cls, *args, **kw):  
        if not hasattr(cls, '_instance'):  
            orig = super(Singleton, cls)  
            cls._instance = orig.__new__(cls, *args, **kw)  
        return cls._instance  


#继承了Singleton, ParseQueryVesionInfo两个基类
class QueryInfoClient(Singleton, ParseQueryVesionInfo):
    
    def handle_query_info(self):
        """
        发送查询消息
        """
        ParseQueryVesionInfo.__init__(self)

        #construct query message
        new_message = messagehandle.ConstructMessageHandle.construct_update_info_query_post()
        
        #发送query消息到升级服务器
        return self.handle_request_query_info(new_message)
    
    
    def get_query_info_data(self):
        """
        返回查询信息
        """
        new_dict_data = self.get_query_result_version_data()
        return new_dict_data
    
    
    def set_query_info_data(self, in_data):
        """
        将数据保存更新到ParseQueryVesionInfo基类对象中
        """
        self.set_query_result_version_data(in_data)
    
    
    def handle_request_query_info(self, in_message):
        """
        发送查询消息给升级服务器
        """
        
        try:
            _dict_input_data={}
            
            _dict_input_data['HTTP_IP'] = messagehandle.Event.UPGRADE_SERVER_HTTP_IP
            _dict_input_data['HTTP_PORT'] = messagehandle.Event.UPGRADE_SERVER_HTTP_PORT
            _dict_input_data['HTTP_URL'] = messagehandle.Event.UPGRADE_SERVER_HTTP_QUERT_URL
            _dict_input_data['HTTP_TIMEOUT'] = messagehandle.Event.UPGRADE_SERVER_HTTP_QUERT_TIMEOUT
            
            _dict_input_data['MESSAGE'] = in_message
            
            _dict_input_data['CALLBACK_HANDLE'] = self
            
            return QueryInfoHttpClient.request_query_info(_dict_input_data)
            
        except Exception, e:
            err_info = "Start http client to upgrade server occurs exception:%s" % e
            messagehandle.log(u"%s" % err_info)
            return self.request_fail(err_info)
    
    
    def handle_response(self, in_from_event, in_status, in_response):
        """
        回应消息的数据处理
        """
        
        out_response = in_response
        
        if (in_status == "timeout" or
            in_status == "except" or
            in_status == "fail"):
            
            messagehandle.log(u"%s" % out_response)
            
            #请求失败
            return self.request_fail(out_response)
        
        elif in_status == "response":
            
            #请求成功
            return self.request_suc(in_from_event, out_response)
    
    
    def request_suc(self, in_from_event, in_response):
        """
        请求成功
        """
        
        #读取服务器返回的数据
        rc_content = in_response.read()
        
        #获取消息类型
        message_event = messagehandle.ParseMessageHandle.get_response_event(rc_content)
        
        #检查服务器返回类型与等待返回请求消息类型是否匹配
        if in_from_event != message_event:
            erro_info = "HTTP server's response event type error, response event=%s" % message_event
            return self.request_fail(erro_info)
        
        #query返回消息处理
        if messagehandle.Event.MSG_TYPE_UPGRADE_INFO_QUERY == message_event:
            
            #解析服务器返回查询消息数据
            rc_flag, out_property_dict = messagehandle.ParseMessageHandle.parse_update_info_query_response(rc_content)
            if (True == rc_flag and
                None != out_property_dict and
                out_property_dict.keys()):
                
                self.set_query_info_data(out_property_dict)
                
                return messagehandle.Event.CLIENT_REQUEST_SUC
            
            else:
                self.set_query_info_data(None)
                return messagehandle.Event.CLIENT_REQUEST_FAIL
        
        return messagehandle.Event.CLIENT_REQUEST_FAIL
    
    
    def request_fail(self, in_erro):
        """
        处理失败信息
        """
        
        messagehandle.log(u"%s" % in_erro)
        return messagehandle.Event.CLIENT_REQUEST_FAIL
    
    
class QueryInfoHttpClient():

    @staticmethod
    def request_query_info(in_data_dict):
        """
        构建查询请求
        """
        
        #[setp-1]save input data
        _ip = in_data_dict.get('HTTP_IP')               # http server url
        _port = in_data_dict.get('HTTP_PORT')           # http port
        _url_path = in_data_dict.get('HTTP_URL')        #http url
        _timeout = in_data_dict.get('HTTP_TIMEOUT')     # http request timeout
        
        _request_handle = in_data_dict.get('CALLBACK_HANDLE') #request query info object
        
        _message = in_data_dict.get('MESSAGE')          # message be sent to Upgrade Server
        
        #[setp-2]check message data
        if not _message:
            err_info = "Input message data in None"
            if _request_handle:
                return _request_handle.request_fail(err_info)
            else:
                return messagehandle.Event.CLIENT_REQUEST_FAIL
            
        #[setp-3]send http request
        messagehandle.log(u"Send request(message=%s) to Upgrade server's" %(messagehandle.Event.MSG_TYPE_UPGRADE_INFO_QUERY))
        
        rc_status,rc_response = QueryInfoHttpClient.send_query_info_message(in_ip=_ip,
                                                                            in_port=_port,
                                                                            in_url_path=_url_path,
                                                                            in_timeout=_timeout,
                                                                            in_message=_message)
        
        messagehandle.log(u"Recv Upgrade server's response(request message=%s)" %(messagehandle.Event.MSG_TYPE_UPGRADE_INFO_QUERY))
        
        #[setp-4]数据处理
        if _request_handle:
            in_from_event = messagehandle.Event.MSG_TYPE_UPGRADE_INFO_QUERY
            return _request_handle.handle_response(in_from_event, rc_status, rc_response)
        else:
            return messagehandle.Event.CLIENT_REQUEST_FAIL
    
    
    @staticmethod
    def send_query_info_message(in_ip="127.0.0.1", in_port=0, in_url_path='/', in_timeout=60, in_message=''):
        """
        发送查询请求
        """
        
        try:
            #初始化连接
            conn = httplib.HTTPConnection(in_ip, in_port, True, in_timeout)
            
            #设置HTTP头
            conn.putrequest("POST", in_url_path) 
            conn.putheader("Transfer-Encoding", "chunked") 
            conn.endheaders()
            
            #发送数据
            conn.send("%x" % len(in_message) + "\r\n" + in_message + "\r\n")
            
            #发送数据结束符
            conn.send("0\r\n\r\n")
            
            #获取返回数据
            rc_response = conn.getresponse()
            
            #获取返回状态数据
            rc_status = rc_response.status  
            messagehandle.log(u"HTTP 请求的回应状态为：%d" % rc_status)
            
        except Exception, e:
            #异常
            if e.message == "timed out":
                out_status = "timeout"
                out_data = "Wait for HTTP server's response timeout!"
            else:
                out_status = "except"
                out_data = "Send HTTP request occurs exception:%s" % e
        else:
            #处理服务器返回的数据
            if httplib.OK == rc_status:
                out_status = "response"
                out_data = rc_response
            else:
                out_status = "fail"
                out_data = "HTTP server's response fail: %s" % rc_status
                
        finally:
            #数据处理
            return out_status, out_data
        
            
            
#-------------------------------------------------------------------------------------


if __name__ == '__main__':
    
    #dec_host=messagehandle.get_active_server_address()

    query_obj=QueryInfoClient()
    messagehandle.Event.UPGRADE_SERVER_HTTP_IP='172.16.28.59'
    
    rc_request_status=query_obj.handle_query_info()
    
    if messagehandle.Event.CLIENT_REQUEST_FAIL==rc_request_status:
        messagehandle.log(u"handle_query_info fail")

    messagehandle.log(u"handle_query_info suc")


    #v.debug131017.svn1721/v.beta131017.svn1721/v2.0.0
    #base_robot_gui_version="v.debug131017.svn1725"
    base_robot_gui_version="v.beta131017.svn1725"
    #base_robot_gui_version="v2.0.0"
    
    
    #保存需要下载的文件列表
    query_obj.get_application_total_package_vers(base_robot_gui_version)
    #query_obj.get_base_robot_gui_version_testlib_package_vers(base_robot_gui_version)
    #query_obj.get_auto_selected_testlib_latest_packages(base_robot_gui_version)

    nExit = raw_input("Press any key to end...")
#-------------------------------------------------------------------------------------
