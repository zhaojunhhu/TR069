#coding:utf-8

# sys
import  os
import  sys

from twisted.internet           import reactor, threads
from twisted.internet.defer     import Deferred, DeferredList, succeed
from twisted.web                import http
from twisted.web.http           import Request
from twisted.web.resource       import Resource
from twisted.web.server         import Site
from twisted.web.server         import NOT_DONE_YET


# user
from    TR069.lib.common.error          import  *
import  TR069.lib.common.logs.log       as      log 
from    TR069.lib.common.function       import  print_trace, UsersMsgSeq
import  TR069.lib.acss.acs.webservercfg         as      webservercfg
from    cpe                             import  CPE
import  cpe_thread
from    cpe_thread                      import  AcsCpeThread
from    cpe_db                          import  *

# ------------------------------------------------------------
def handle_soap(request):
    """
    request = http.Request
    cpe soap 
    """    
    
    try:
        CPE.dispatch_soap(request)        
    
    except Exception,e:
        print_trace(e)  


def handle_user(request):
    """
    request = http.Request
    user rpc
    """    

    try:
        CPE.dispatch_user(request)        
    
    except Exception,e:
        print_trace(e) 


class ACSHandleRequest(http.Request):    
    """
    
    """
    # page
    dict_page_handlers={
        webservercfg.USER_PAGE: handle_user,
        webservercfg.CPE2ACS_PAGE: handle_soap,
    }
    
    def process(self):        
        """
        url msg
        """
        
        self.setHeader("Content-Type","text/html")
        if self.dict_page_handlers.has_key(self.path):
            handler=self.dict_page_handlers[self.path]
            handler(self)
        else:
            self.setResponseCode(http.NOT_FOUND)
            self.write("<h1>Not Found</h1>Sorry, no such page.")
            self.finish()
            self.transport.loseConnection()
    
    
class ACSHttpChannel(http.HTTPChannel):
    requestFactory=ACSHandleRequest
    
    def connectionLost(self, reason):      
        CPE.on_connection_lost(self.transport)
    
class ACSHttpFactory(http.HTTPFactory):
    protocol=ACSHttpChannel    


class ACS(object):
    """    
    """
    def __init__(self, port=None):
        self.http_port = port                        

    
    def start(self):        
        
        cpe_thread.on_check_cpe_online(webservercfg.CHECK_CPE_ONLINE_TIMEINTERVAL)
        cpe_thread.on_check_cpe_worklist_status(webservercfg.CHECK_ACS_LOGIC_WORKLIST_STATUS_TIMEINTERVAL)
        UsersMsgSeq.on_check_acs_message_seq()

        CPE.init()
        
        reactor.listenTCP(self.http_port, ACSHttpFactory())
        reactor.run()

        self.on_acs_exit()
        

    def on_acs_exit(self):
        log.app_info("acs server exit.")

        exit_acs_db()
        
        UsersMsgSeq.cancel_timer_check()  
        AcsCpeThread.cancel_timer_check_cpes_online()
        AcsCpeThread.cancel_timer_check_worklist_status()
        
        sys.exit()

         
# --------------------------------------global ----------------

def test():

    try:                
        ip = webservercfg.HTTP_IP
        port = webservercfg.HTTP_PORT
        
        g_webserver=ACS(port)

        log.app_info("ACS (ip=%s, port=%s) start." %(ip, port))        
        g_webserver.start()
        
    except Exception,e:
        print_trace(e)    


if __name__ == '__main__':
    test()
