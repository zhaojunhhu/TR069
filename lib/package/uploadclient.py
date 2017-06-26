# -*- coding: utf-8 -*-

# /*************************************************************************
#  Copyright (C), 2013-2014, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: queryinfoclient
#  function: 实现向升级服务器上传软件版本
#  Author: ATT development group
#  version: V1.0
#  date: 2013.06.26
#  change log:
#
#  wangjun  20130626    created
#  
# ***************************************************************************

import os
import sys
import threading
import httplib
import time
import copy

import package.messagehandle  as messagehandle


class UploadClient():
    
    def __init__(self):
        self._transfer_serial=None
    
    def handle_upload(self,
                      in_testlib_name,
                      in_testlib_ver,
                      in_base_attrobot_ver,
                      in_remote_flag,
                      in_testlib_alias,
                      in_upload_file_path):
        """
        上传ZIP软件包到服务器
        """
        #[step-0]check input upload file
        #检查文件是否存在
        if not os.path.exists(in_upload_file_path):
            error_info="input upload file is not exist"
            return self.request_fail(error_info)

        if not (os.path.split(in_upload_file_path)[1].find(".zip") != -1):
            error_info="input upload file is not zip file"
            return self.request_fail(error_info) 
        
        messagehandle.log(u"Source: %s\n" % in_upload_file_path)
        
        #[step-1] init
        rc_request_status=self.handle_upload_init(in_testlib_name,
                                                  in_testlib_ver,
                                                  in_base_attrobot_ver,
                                                  in_remote_flag,
                                                  in_testlib_alias)
        if messagehandle.Event.CLIENT_REQUEST_FAIL==rc_request_status:
            messagehandle.log(u"handle_upload fail")
            return rc_request_status
        
        messagehandle.log(u"handle_upload init suc\n")
        
        #[step-2] upload
        in_transfer_serial=self._transfer_serial
        
        rc_flag,rm_md5=messagehandle.ConstructMessageHandle.construct_zipfile_md5(in_upload_file_path)
        if False == rc_flag:
            messagehandle.log(u"handle_upload construct file md5 fail")
            messagehandle.log(u"handle_upload fail")
            return rc_request_status
        
        in_file_md5=rm_md5
        
        rc_request_status=self.handle_upload_file(in_transfer_serial,
                                                  in_file_md5,
                                                  in_upload_file_path)
        if messagehandle.Event.CLIENT_REQUEST_FAIL==rc_request_status:
            messagehandle.log(u"handle_upload fail")
            return rc_request_status

        messagehandle.log(u"handle_upload suc")
        return messagehandle.Event.CLIENT_REQUEST_SUC
        
    
    def handle_upload_init(self,in_testlib_name,in_testlib_ver,in_base_attrobot_ver,in_remote_flag,in_testlib_alias):
        """
        发送上传初始化消息
        """

        #construct message
        new_message=messagehandle.ConstructMessageHandle.construct_upload_init_post(in_testlib_name,
                                                                                        in_testlib_ver,
                                                                                        in_base_attrobot_ver,
                                                                                        in_remote_flag,
                                                                                        in_testlib_alias)
        #发送init消息到升级服务器
        return self.handle_request_upload_init(new_message)
        
        
    def handle_upload_file(self,in_transfer_serial,in_file_md5,in_upload_file_path):
        """
        发送上传文件消息
        """
        
        #construct message
        new_message=messagehandle.ConstructMessageHandle.construct_upload_zipfile_post(in_transfer_serial,
                                                                                           in_file_md5)
        #发送upload消息到升级服务器
        return self.handle_request_upload_file(new_message,in_upload_file_path)


    def set_transfer_serial_value(self,in_transfer_serial):
        """
        保存上传文件需要的令牌
        """
        self._transfer_serial=in_transfer_serial
        
        if self._transfer_serial:
            messagehandle.log(u"transfer serial: %s" % self._transfer_serial)
        
        return

    
    def handle_request_upload_init(self,in_message):
        """
        发送请求消息给升级服务器
        """
        try:
            _dict_input_data={}
            
            _dict_input_data['HTTP_IP']=messagehandle.Event.UPGRADE_SERVER_HTTP_IP
            _dict_input_data['HTTP_PORT']=messagehandle.Event.UPGRADE_SERVER_HTTP_PORT
            _dict_input_data['HTTP_URL']=messagehandle.Event.UPGRADE_SERVER_HTTP_QUERT_URL
            _dict_input_data['HTTP_TIMEOUT']=messagehandle.Event.UPGRADE_SERVER_HTTP_QUERT_TIMEOUT
            
            _dict_input_data['MESSAGE']=in_message
            
            _dict_input_data['CALLBACK_HANDLE']=self
            
            return UploadHttpClient.request_upload_init(_dict_input_data)
            
        except Exception, e:
            err_info = "Start http client to upgrade server occurs exception:%s" % e
            #messagehandle.log(u"%s" % err_info)
            return self.request_fail(err_info)


    def handle_request_upload_file(self,in_message,in_upload_file_path):
        """
        发送请求消息给升级服务器
        """
        try:
            _dict_input_data={}
            
            _dict_input_data['HTTP_IP']=messagehandle.Event.UPGRADE_SERVER_HTTP_IP
            _dict_input_data['HTTP_PORT']=messagehandle.Event.UPGRADE_SERVER_HTTP_PORT
            _dict_input_data['HTTP_URL']=messagehandle.Event.UPGRADE_SERVER_HTTP_UPLOAD_URL
            _dict_input_data['HTTP_TIMEOUT']=messagehandle.Event.UPGRADE_SERVER_HTTP_UPLOAD_TIMEOUT
            
            _dict_input_data['MESSAGE']=in_message
            _dict_input_data['LOAD_FILE_PATH']=in_upload_file_path
            
            _dict_input_data['CALLBACK_HANDLE']=self
                    
            return UploadHttpClient.request_upload_file(_dict_input_data)

        except Exception, e:
            err_info = "Start http client to upgrade server occurs exception:%s" % e
            #messagehandle.log(u"%s" % err_info)
            return self.request_fail(err_info)
        

    def handle_response(self,in_from_event,in_status,in_response):
        """
        数据处理
        """
        out_response=in_response
        
        if (in_status == "timeout" or
            in_status == "except" or
            in_status == "fail"):
            
            #messagehandle.log(u"%s" % out_response)
            
            #请求失败
            return self.request_fail(out_response)

        elif in_status == "response":
            
            #请求成功
            return self.request_suc(in_from_event,out_response)
            

    def request_suc(self,in_from_event,in_response):
        """
        请求成功
        """
        
        #读取服务器返回的数据
        rc_content=in_response.read()
        
        #获取消息类型
        message_event=messagehandle.ParseMessageHandle.get_response_event(rc_content)

        #检查服务器返回类型与等待返回请求消息类型是否匹配
        if in_from_event != message_event:
            erro_info=("HTTP server's response event type error, response event=%s" %message_event)
            return self.request_fail(erro_info)
        
        #int 返回消息处理
        if messagehandle.Event.MSG_TYPE_UPLOAD_INIT==message_event:
                
            #解析服务器返回上传文件初始化消息数据
            rc_flag,rc_data=messagehandle.ParseMessageHandle.parse_upload_init_response(rc_content)
            
            if (True == rc_flag and None != rc_data):
                
                #保存请求上传文件返回的令牌数据
                rc_transfer_serial_value=rc_data
                self.set_transfer_serial_value(rc_transfer_serial_value)
                return messagehandle.Event.CLIENT_REQUEST_SUC
                
            else:
                self.set_transfer_serial_value(None)
                rc_erro=rc_data
                return self.request_fail(rc_erro)
 
        #upload 返回消息处理
  
        elif messagehandle.Event.MSG_TYPE_UPLOAD_FILE==message_event:
            
            #解析服务器返回上传文件消息数据
            #messagehandle.log(u"%s" % rc_content)
            rc_flag,rc_data=messagehandle.ParseMessageHandle.parse_upload_zipfile_response(rc_content)
            
            if (True == rc_flag):
                return messagehandle.Event.CLIENT_REQUEST_SUC
                
            else:
                rc_erro=rc_data
                return self.request_fail(rc_data)
            
        else:
            pass

        return messagehandle.Event.CLIENT_REQUEST_FAIL
    
    
    def request_fail(self,in_erro):
        """
        处理失败信息
        """
        messagehandle.log(u"%s" % in_erro)
        return messagehandle.Event.CLIENT_REQUEST_FAIL
        
        
class UploadHttpClient():

    @staticmethod
    def request_upload_init(in_data_dict):
        
        #[setp-1]save input data
        _ip = in_data_dict.get('HTTP_IP')               # http server url
        _port = in_data_dict.get('HTTP_PORT')           # http port
        _url_path=in_data_dict.get('HTTP_URL')          #http url
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
        messagehandle.log(u"Send request(message=%s) to Upgrade server's" %(messagehandle.Event.MSG_TYPE_UPLOAD_INIT))
        
        rc_status,rc_response = UploadHttpClient.send_updata_init_message(in_ip=_ip,
                                                                                    in_port=_port,
                                                                                    in_url_path=_url_path,
                                                                                    in_timeout=_timeout,
                                                                                    in_message=_message)
        

        messagehandle.log(u"Recv Upgrade server's response(request message=%s)" %(messagehandle.Event.MSG_TYPE_UPLOAD_INIT))
        
        #[setp-4]数据处理
        if _request_handle:
            in_from_event=messagehandle.Event.MSG_TYPE_UPLOAD_INIT
            return _request_handle.handle_response(in_from_event,rc_status,rc_response)
        else:
            return messagehandle.Event.CLIENT_REQUEST_FAIL
        
        
    @staticmethod
    def request_upload_file(in_data_dict):

        #[setp-1]save input data
        _ip = in_data_dict.get('HTTP_IP')               # http server url
        _port = in_data_dict.get('HTTP_PORT')           # http port
        _url_path=in_data_dict.get('HTTP_URL')          #http url
        _timeout = in_data_dict.get('HTTP_TIMEOUT')     # http request timeout
        
        _request_handle = in_data_dict.get('CALLBACK_HANDLE') #request query info object
                
        _message = in_data_dict.get('MESSAGE')          # message be sent to Upgrade Server
        _file_path = in_data_dict.get('LOAD_FILE_PATH') # load file data be sent to Upgrade Server

        #[setp-2]check message data
        if not _message:
            err_info = "Input message data in None"
            if _request_handle:
                return _request_handle.request_fail(err_info)
            else:
                return messagehandle.Event.CLIENT_REQUEST_FAIL
        
        #[setp-3]send http request
        messagehandle.log(u"Send request(message=%s) to Upgrade server's" %(messagehandle.Event.MSG_TYPE_UPLOAD_FILE))
                                                               
        rc_status,rc_response = UploadHttpClient.send_updata_file_message(in_ip=_ip,
                                                                                    in_port=_port,
                                                                                    in_url_path=_url_path,
                                                                                    in_timeout=_timeout,
                                                                                    in_message=_message,
                                                                                    in_file_path=_file_path )

        messagehandle.log(u"Recv Upgrade server's response(request message=%s)" %(messagehandle.Event.MSG_TYPE_UPLOAD_FILE))
        
        #[setp-4]数据处理
        if _request_handle:
            in_from_event=messagehandle.Event.MSG_TYPE_UPLOAD_FILE
            return _request_handle.handle_response(in_from_event,rc_status,rc_response)
        else:
            return messagehandle.Event.CLIENT_REQUEST_FAIL
    
    
    @staticmethod
    def send_updata_init_message(in_ip="127.0.0.1",in_port=0,in_url_path='/',in_timeout=60,
                                in_message=''):
        """
        发送HTTP请求
        """
        try:
            #初始化连接
            conn = httplib.HTTPConnection(in_ip,in_port,True,in_timeout)
            
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
            rc_status=rc_response.status  
            messagehandle.log(u"HTTP server's response status: %d" % rc_status)
            
        except Exception, e:
            #异常
            if e.message == "timed out":
                out_status="timeout"
                out_data="Wait for HTTP server's response timeout!"
            else:
                out_status="except"
                out_data="Send HTTP request occurs exception:%s" % e
        else:
            #处理服务器返回的数据
            if httplib.OK == rc_status:
                out_status="response"
                out_data=rc_response
            else:
                out_status="fail"
                out_data="HTTP server's response fail: %s" % rc_status
                
        finally:
            #数据处理
            return out_status,out_data
                 

    @staticmethod
    def send_updata_file_message(in_ip="127.0.0.1",in_port=0,in_url_path='/',in_timeout=6000,
                                in_message='',in_file_path=''):
        """
        发送上传请求
        """
        try:
            #初始化连接
            conn = httplib.HTTPConnection(in_ip,in_port,True,in_timeout)  

            #设置HTTP头
            conn.putrequest("PUT", in_url_path) 
            conn.putheader("Transfer-Encoding", "chunked") 
            conn.endheaders()

            #发送数据
            conn.send("%x" % len(in_message) + "\r\n" + in_message + "\r\n")
            
            #发送文件
            with open(in_file_path, 'rb') as fp:
                data = fp.read(messagehandle.Event.HTTP_SEND_MAX_LENGTH)
                while len(data)>0:
                    #messagehandle.log(u"%d" % len(data))
                    conn.send("%x" % len(data) + "\r\n" + data + "\r\n") 
                    data = fp.read(messagehandle.Event.HTTP_SEND_MAX_LENGTH)
            
            #发送数据结束符
            conn.send("0\r\n\r\n")
            
            #获取返回数据
            rc_response = conn.getresponse()
            
             #获取返回状态数据
            rc_status=rc_response.status  
            messagehandle.log(u"HTTP server's response status: %d" % rc_status)
            
        except Exception, e:
            #异常
            if e.message == "timed out":
                out_status="timeout"
                out_data="Wait for HTTP server's response timeout!"
            else:
                out_status="except"
                out_data="Send HTTP request occurs exception:%s" % e
        else:
            #处理服务器返回的数据
            if httplib.OK == rc_status:
                out_status="response"
                out_data=rc_response
            else:
                out_status="fail"
                out_data="HTTP server's response fail: %s" % rc_status
                
        finally:
            #数据处理
            return out_status,out_data
                 


#-------------------------------------------------------------------------------------    
if __name__ == '__main__':

    upload_obj=UploadClient()

    tmp_testlib_name='TestCenter'
    tmp_testlib_ver='v1.5.3'
    tmp_base_attrobot_ver='v1.1.1'

    obj_path= os.path.dirname(sys.argv[0])
    tmp_upload_file_path=obj_path + '\upload_folder' + "\Chariot.zip"
    
    rc_request_status=upload_obj.handle_upload(in_testlib_name=tmp_testlib_name,
                                                in_testlib_ver=tmp_testlib_ver,
                                                in_base_attrobot_ver=tmp_base_attrobot_ver,
                                                in_remote_flag=False,
                                                in_upload_file_path=tmp_upload_file_path)
    
    if messagehandle.Event.CLIENT_REQUEST_FAIL==rc_request_status:
        print(u"handle_upload fail")
        #return rc_request_status
        
    print(u"handle_upload suc")
    #return messagehandle.Event.CLIENT_REQUEST_SUC
    
    nExit = raw_input("Press any key to end...")
#-------------------------------------------------------------------------------------
