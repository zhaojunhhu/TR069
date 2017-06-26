#coding:utf-8

# sys
import os
import sys

from    twisted.internet           import   reactor, threads
from    twisted.internet.defer     import   Deferred, DeferredList, succeed
from    twisted.web                import   http
from    twisted.web.http           import   Request
from    twisted.web.resource       import   Resource
from    twisted.web.server         import   Site
from    twisted.web.server         import   NOT_DONE_YET

# user
from    TR069.lib.common.error      import  *
from    TR069.lib.common.function   import  print_trace, UsersMsgSeq
import  TR069.lib.common.logs.log   as      log 
import  TR069.lib.worklists.worklistcfg      as      worklistcfg
from    worklist                    import  Worklist

# ------------------------------------------------------------
def handle_agent(request):
    """
    request = http.Request
    """    

    try:
        Worklist.dispatch_agent(request)        
    
    except Exception,e:
        print_trace(e)


class WorklistHandleRequest(http.Request):    
    """
    
    """
    # page
    dict_page_handlers={
        worklistcfg.AGENT2WORKLIST_PAGE: handle_agent,
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
        

class WorklistHttpChannel(http.HTTPChannel):
    requestFactory = WorklistHandleRequest
    
    def connectionLost(self, reason):
        ip = self.transport.client[0]
        port = self.transport.client[1]    
        sessionno = self.transport.sessionno 

        desc = "connection lost(ip=%s, port=%s, sessionno=%s)" %(ip, port, sessionno)
        log.app_info(desc)
        
    
class WorklistHttpFactory(http.HTTPFactory):
    protocol = WorklistHttpChannel    


class WorklistServer(object):
    """
    """
    def __init__(self, port=None):
        self.http_port = port                        
    
    def start(self):        

        UsersMsgSeq.on_check_acs_message_seq()
    
        reactor.listenTCP(self.http_port, WorklistHttpFactory())
        reactor.run()

        self.on_acs_exit()        


    def on_acs_exit(self):
        log.app_info("worklist server exit.")      

        UsersMsgSeq.cancel_timer_check()        
        sys.exit()

        
# --------------------------------------global ----------------

def test():

    try:                
        ip = worklistcfg.HTTP_IP
        port = worklistcfg.HTTP_PORT
        
        g_webserver=WorklistServer(port)

        log.app_info("worklist (ip=%s, port=%s) start." %(ip, port))        
        g_webserver.start()
        
    except Exception,e:
        print_trace(e)


if __name__ == '__main__':
    test()
