#coding:utf-8

from twisted.internet import reactor, threads
from twisted.internet.defer import Deferred, DeferredList, succeed
from twisted.web import http
from twisted.web.http import Request
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.web.server import NOT_DONE_YET

import os
import sys
import agentcfg
import DUTqueuemanagement
from responseclient import ResponseClientHandle
import responseclient
import threading

import TR069.lib.common.logs.log as log
import TR069.lib.common.event as event


def root_dispath_evetn(msg,conn):
    """
    调用接口，分发消息
    """
    #dispath message to dutqueue object
    DUTqueuemanagement.DUTQueueManagement.insert_dut_obj([msg, conn])
     
        
def handle_dispath_request(request):
    """
    处理所有消息入口
    """    
    try:
        msg = request.content.read()
        conn=request
        
        if msg:
            try:
                log.app_info("(Request from client %s)agent httserver recv message.\n" % ResponseClientHandle.get_client_ipaddress(conn))
                
                """
                log.debug_info("-------httserver handle_dispath_request----------")
                log.debug_info(msg)
                log.debug_info("-------------------------------------------------")
                """
                msg=eval(msg)
            except Exception, e:
                err_info = "The structure of recv message is invalid!"
                log.debug_err(err_info)
                return

        responseclient.g_http_client_count+=1
        log.app_info("acceptConnection: Agent HTTP connected client count: %d" % responseclient.g_http_client_count)
        
        t = threading.Thread(target=root_dispath_evetn, args=(msg, conn))
        t.setDaemon(True)
        t.start()
        
    except Exception,e:
        err_info = "DUTQueueManagement dispath request event occurs exception:%s" % e
        log.debug_info(err_info)
        ResponseClientHandle.handle_except(msg, conn, err_info)



class AgentHandleRequest(http.Request):    
    """
    """
    # 定义了路径映射功能
    dict_page_handlers={
        agentcfg.AGENT_HTTP_SERVER_PATH: handle_dispath_request,
    }
    
    def process(self):        
        """
        """
        self.setHeader("Content-Type","text/html")
        
        #log.debug_info(self.path)
        
        if self.dict_page_handlers.has_key(self.path):
            handler=self.dict_page_handlers[self.path]
            handler(self)
        else:
            self.setResponseCode(http.NOT_FOUND)
            self.write("<h1>Not Found</h1>Sorry, no such page.")
            self.finish()
            self.transport.loseConnection()
    

class AgentHttpChannel(http.HTTPChannel):
    requestFactory=AgentHandleRequest
    
    def connectionLost(self, reason):
        sessionno = self.transport.sessionno        


class AgentHttpFactory(http.HTTPFactory):
    protocol=AgentHttpChannel
    

class AgentHttpServer(object):
    """
    """
    def __init__(self, port=None):
        self.http_port = port                        
    
    def start(self):        

        reactor.listenTCP(self.http_port, AgentHttpFactory())
        reactor.run()


def start_http_server():

    try: 
        ip = agentcfg.AGENT_HTTP_SERVER_IP
        port = agentcfg.AGENT_HTTP_SERVER_PORT
        
        g_webserver=AgentHttpServer(port)

        log.debug_info ("Agent (ip=%s, port=%s) start." %(ip, port))        
        g_webserver.start()
        
    except Exception,e:  
        err_info = "Agent http service occurs expection: %s" % e
        log.debug_info (err_info)



if __name__ == '__main__':
    start_http_server()
