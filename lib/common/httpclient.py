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
from    time        import      sleep
import  TR069.vendor.httplib2   as httplib2

from    function    import      print_trace
from    event       import      *
from    error       import      *
from    TR069.lib.common.releasecfg   import *   # for tr069 self or RF?


# --------------------------------------------------------------

class HttpClient(object):
    
    def __init__(self, url, timeout):                
        self.url        = url
        self.timeout    = timeout 

    def send_message(self, msg):
        """
        msg is from build_rpc_msg
        return is success, alse need parse the content, is event rsp or fail?
        return is fail, mean timeout or agent unrecognize
        """
        
        ret         = ERR_FAIL    
        str_data    = ""
        content     = ""

        for i in [1, 2, 3]:   
        
            try:

                connection = httplib2.Http(timeout=self.timeout)
                response, content = connection.request(self.url, method="POST", body=msg)
                # client close
                connection.close()
            except Exception, e:
            
                print_trace(e)  
                
                # friendly tip
                str_data = "connect to http server url(%s) fail" %self.url
                                
                try:
                    # retry 
                    if ((e.errno == 10060) or (e.errno == 10065)):
                        log.app_err("errno = 10060 or 10065, retry")
                        
                        continue
                except Exception:
                    pass                

                # other error, skip                                          
                break
            else:
                
                log.debug_info("response=%s" %content)
                
                status = response.get('status')
                # status=200 =ok
                if (status == "200"):
                    
                    ret = ERR_SUCCESS 
                    str_data = content
                else:
                    
                    ret = ERR_FAIL
                    str_data = "http post fail."

                # success
                break
                
        return ret, str_data  

