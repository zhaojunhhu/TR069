#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: HttClientHandle
#  function: send http request to ACS Server or WorkList Server, and relay the response to client
#            
#  Author: ATT development group
#  version: V1.0
#  date: 2012.10.27
#  change log:
#  wangjun  20130529     created
# ***************************************************************************

import httplib2
import time

import TR069.lib.common.logs.log as log


class HttClientHandle(object):
    """
    send http request
    """
 

                    
    @staticmethod
    def send_http_msg(in_message,in_timeout=300,in_try_count=0,in_url="127.0.0.1",in_method="POST"):
        """
        send http request to WorkList Server Server or Worklist Server, and wait for response, if timeout, return time out,
        if response is not 200 OK, return errorno.
        """
        
        tmp_try_count=0
        if in_try_count>=0:
            tmp_try_count=in_try_count
            
        while 1:#in_try_count>0:
            
            conn=None
            
            try:
                conn = httplib2.Http(timeout=in_timeout)
                res, content = conn.request(in_url, method=in_method, body=in_message)
                
            except Exception, e:

                if e.message == "timed out":
                    log.debug_info("Wait for HTTP server's response timeout!")
                    
                    if tmp_try_count>0:
                        log.debug_info("Try(try_count=%d) send HTTP request event" % tmp_try_count)
                        tmp_try_count-=1
                        continue
                    
                    else:
                        return ("error", "time out")
                else:
                    err_info = "Send HTTP request occurs exception:%s" % e
                    log.debug_err(err_info)
                    return ("error", err_info)
            else:
                
                #交互正常结束，客户端主动断开连接 #add by wangjun 20130726
                if conn:
                    conn.close()
                    log.debug_info("Close agent created to ACS Server's or WorkList Server's HTTP client connect")
                    
                status = res.get('status')
                if status == "200":
                    return ("response", content)
                else:
                    return ("fail", status)
                
            
    @staticmethod
    def send_http_msg_notry(in_message,in_timeout=300,in_try_count=0,in_url="127.0.0.1",in_method="POST"):
        """
        send http request to WorkList Server Server or Worklist Server, and wait for response, if timeout, return time out,
        if response is not 200 OK, return errorno.
        """
        try:
            conn = httplib2.Http(timeout=in_timeout)
            res, content = conn.request(in_url, method=in_method, body=in_message)
            
        except Exception, e:
            if e.message == "timed out":
                log.debug_info("Wait for HTTP server's response timeout!")
                return ("error", "time out")
            else:
                err_info = "Send HTTP request occurs exception:%s" % e
                log.debug_err(err_info)
                return ("error", err_info)
        else:
            status = res.get('status')
            if status == "200":
                return ("response", content)
            else:
                return ("fail", status)