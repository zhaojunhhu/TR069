# -*- coding: utf-8 -*-

# /*************************************************************************
#  Copyright (C), 2013-2014, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: queryinfoclient
#  function: 实现向升级服务器下载软件版本
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


class DownloadClient():
    
    def __init__(self):
        self._testlib_name=None
        self._testlib_ver=None
        #self._base_attrobot_ver=None
        self._testlib_file_folder_path=None
        
    def handle_download(self,
                        in_testlib_name,
                        in_testlib_ver,
                        in_save_testlib_file_folder_path):
        """
        发送下载消息
        """
        self._testlib_name=in_testlib_name
        self._testlib_ver=in_testlib_ver
        
        #创建存放下载文件的文件夹
        if os.path.isdir(in_save_testlib_file_folder_path):
            pass
        
        if not os.path.exists(in_save_testlib_file_folder_path):
            self.create_folder(in_save_testlib_file_folder_path)
            messagehandle.log(u"Create folder: %s" %(in_save_testlib_file_folder_path))

        self._testlib_file_folder_path=in_save_testlib_file_folder_path
        messagehandle.log(u"%s" % self._testlib_file_folder_path)
        
        #construct message
        new_message=messagehandle.ConstructMessageHandle.construct_download_post(in_testlib_name,
                                                                                    in_testlib_ver)

        #发送download消息到升级服务器
        return self.handle_request_download(new_message)


    def handle_request_download(self,in_message):
        """
        发送查询消息给升级服务器
        """
        try:
            _dict_input_data={}
            
            _dict_input_data['HTTP_IP']=messagehandle.Event.UPGRADE_SERVER_HTTP_IP
            _dict_input_data['HTTP_PORT']=messagehandle.Event.UPGRADE_SERVER_HTTP_PORT
            _dict_input_data['HTTP_URL']=messagehandle.Event.UPGRADE_SERVER_HTTP_DOWNLOAD_URL
            _dict_input_data['HTTP_TIMEOUT']=messagehandle.Event.UPGRADE_SERVER_HTTP_DOWNLOAD_TIMEOUT
            
            _dict_input_data['MESSAGE']=in_message
            
            _dict_input_data['CALLBACK_HANDLE']=self
            
            return DownloadHttpClient.request_download(_dict_input_data)

        except Exception, e:
            err_info = "Start http client to upgrade server occurs exception:%s" % e
            messagehandle.log(u"%s" % (err_info))
            
            return self.request_fail(err_info)
        

    def handle_response(self,in_from_event,in_status,in_response):
        """
        数据处理
        """
        out_response=in_response

        if (in_status == "timeout" or
            in_status == "except" or
            in_status == "fail"):

            #请求失败
            return self.request_fail(out_response)

        elif in_status == "response":
            
            #请求成功
            return self.request_suc(in_from_event,out_response)


    def create_folder(self,in_dir_path):

        if os.path.exists(in_dir_path):
            return True

        parent_dir=None
        parent_node_list=[]
        
        if not os.path.isfile(in_dir_path):
            parent_node_list.insert(0,in_dir_path)

        parent_dir=os.path.dirname(in_dir_path)
        while 1:        
            if os.path.exists(parent_dir):
                break
            else:
                parent_node_list.insert(0,parent_dir)
                parent_dir=os.path.dirname(parent_dir)

        for p_node in parent_node_list:
            os.mkdir(p_node,0777)
        
        if  len(parent_node_list):
            return True
        
        return True
    
    
    def request_suc(self,in_from_event,in_response):
        """
        请求成功
        """
        
        #读取服务器返回的数据
        
        #取消息头
        rc_message=in_response.read(messagehandle.Event.UPLOAD_OR_DOWNLOAD_MESSAGE_HEADER_FORMAT_LEN)
        data_end_index=rc_message.rfind('}') 
        rc_message=rc_message[0:data_end_index+1]
        #messagehandle.log(u"\n%s" % , rc_message)

        #获取消息类型
        message_event=messagehandle.ParseMessageHandle.get_response_event(rc_message)

        #检查服务器返回类型与等待返回请求消息类型是否匹配
        if in_from_event != message_event:
            erro_info=("HTTP server's response event type error, response event=%s" %message_event)
            return self.request_fail(erro_info)
        
        #download返回消息处理
        if messagehandle.Event.MSG_TYPE_DOWNLOAD_FILE==message_event:

            #解析服务器返回查询消息数据
            rc_flag,rc_data=messagehandle.ParseMessageHandle.parse_download_response(rc_message)
            if (True==rc_flag and
                None != rc_data and
                rc_data.keys()):
                
                out_property_dict=rc_data
                
                tmp_testlib_name=out_property_dict.get(messagehandle.Event.TESTLIB_NAME)
                tmp_testlib_ver=out_property_dict.get(messagehandle.Event.TESTLIB_VERSION)
                tmp_base_attrobot_ver=out_property_dict.get(messagehandle.Event.BASED_ATTROBOT_VERSION)
                tmp_download_file_md5=out_property_dict.get(messagehandle.Event.ZIP_FILE_MD5)
                
                messagehandle.log(u'------------------------------------------------------')
                messagehandle.log(u"%s" % tmp_testlib_name)
                messagehandle.log(u"%s" % tmp_testlib_ver)
                messagehandle.log(u"%s" % tmp_base_attrobot_ver)
                messagehandle.log(u"%s" % tmp_download_file_md5)
                messagehandle.log(u'------------------------------------------------------')
                
                #验证服务器返回的软件包信息
                if (tmp_testlib_name != self._testlib_name or
                    tmp_testlib_ver != self._testlib_ver):
                    error_info="Response test lib name or test lib version vs request data not match"
                    return self.request_fail(error_info)
        
                #创建存放下载文件的名字
                tmp_testlib_file_name=os.path.join(self._testlib_file_folder_path,(tmp_testlib_name + '_' + tmp_testlib_ver + '.zip'))

                #删除旧的下载包
                #修改删除包匹配规则，查找当前目录下是否存在已下载的包，不仅仅是同名的包 #changed by wangjun 20130709
                for exist_file in os.listdir(self._testlib_file_folder_path):
                    if exist_file.find(tmp_testlib_name) != -1:
                        tmp_exist_file_full_path=os.path.join(self._testlib_file_folder_path,exist_file)
                        messagehandle.log(u"Delete last zip file: %s" % tmp_exist_file_full_path)
                        os.remove(os.path.abspath(tmp_exist_file_full_path))

                messagehandle.log(u"Destination: %s" % tmp_testlib_file_name)

                #取文件流并将文件流写入到指定文件
                with open(tmp_testlib_file_name, 'wb+') as fp:
                    data = in_response.read(messagehandle.Event.HTTP_SEND_MAX_LENGTH)
                    while len(data)>0:
                        #messagehandle.log(u"%d" % len(data))
                        fp.write(data)
                        data = in_response.read(messagehandle.Event.HTTP_SEND_MAX_LENGTH)
                
                #MD5验证
                rc_flag,rm_md5=messagehandle.ConstructMessageHandle.construct_zipfile_md5(tmp_testlib_file_name)
                if False == rc_flag:
                    return self.request_fail("Construct file md5 fail")
                
                messagehandle.log(u"MD5：%s" % rm_md5.upper())
                
                if (tmp_download_file_md5.upper() != rm_md5.upper() ):
                    error_info="Response test lib file check md5 fail"
                    os.remove(tmp_testlib_file_name)
                    return self.request_fail(error_info)
                
                return messagehandle.Event.CLIENT_REQUEST_SUC
            else:
                return messagehandle.Event.CLIENT_REQUEST_FAIL

        return messagehandle.Event.CLIENT_REQUEST_FAIL

    
    def request_fail(self,in_erro):
        """
        处理失败信息
        """
        messagehandle.log(u"%s" % in_erro)
        return messagehandle.Event.CLIENT_REQUEST_FAIL
    
    
class DownloadHttpClient():

    @staticmethod
    def request_download(in_data_dict):
        """
        构造下载请求
        """
        
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
        messagehandle.log(u"Send request(message=%s) to Upgrade server's" %(messagehandle.Event.MSG_TYPE_DOWNLOAD_FILE))

        rc_status,rc_response = DownloadHttpClient.send_download_message(in_ip=_ip,
                                                                        in_port=_port,
                                                                        in_url_path=_url_path,
                                                                        in_timeout=_timeout,
                                                                        in_message=_message)
        

        messagehandle.log(u"Recv Upgrade server's response(request message=%s)" %(messagehandle.Event.MSG_TYPE_DOWNLOAD_FILE))
                
        #[setp-4]数据处理
        if _request_handle:
            in_from_event=messagehandle.Event.MSG_TYPE_DOWNLOAD_FILE
            return _request_handle.handle_response(in_from_event,rc_status,rc_response)
        else:
            return messagehandle.Event.CLIENT_REQUEST_FAIL
    
    
    @staticmethod        
    def send_download_message(in_ip="127.0.0.1",in_port=0,in_url_path='/',in_timeout=6000,
                          in_message=''):
        """
        发送下载请求
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
            
            #发送数据结束符
            conn.send("0\r\n\r\n")
            
            #获取返回数据
            rc_response = conn.getresponse()

            #获取返回状态数据
            rc_status=rc_response.status  
            messagehandle.log(u"%s" % rc_status)
            
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

    download_obj=DownloadClient()
    
    tmp_testlib_name='Capture'
    tmp_testlib_ver='v1.0.debug_a'
    obj_path= os.path.dirname(sys.argv[0]) + '\download_folder'
    
    rc_request_status=download_obj.handle_download(in_testlib_name=tmp_testlib_name,
                                                in_testlib_ver=tmp_testlib_ver,
                                                in_save_testlib_file_folder_path=obj_path)

    if messagehandle.Event.CLIENT_REQUEST_FAIL==rc_request_status:
        messagehandle.log(u"%s" % ("handle_download fail"))

    messagehandle.log(u"%s" % ("handle_download suc"))
        
    nExit = raw_input("Press any key to end...")
#-------------------------------------------------------------------------------------