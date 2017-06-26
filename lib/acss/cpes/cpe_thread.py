#coding:utf-8


# sys lib
import  sys
import  os
from    datetime                    import  datetime, timedelta
from    functools                   import  partial
import  re
import  time
from    threading                   import  Timer
from    twisted.internet            import  reactor, threads

# user lib
from    TR069.lib.common.error          import  *
from    TR069.lib.common.event          import  *
import  TR069.lib.common.logs.log       as      log 
from    TR069.lib.common.httpclient     import  HttpClient
from    TR069.lib.common.function       import  print_trace, get_id, UsersMsgSeq
import  TR069.lib.acss.acs.webservercfg         as      webservercfg
from    cpe_db                          import  *



class AcsCpeThread(object):
    """

    """    

    m_timer_check_cpes_online           = None    
    m_timer_check_worklist_status       = None 
    
    
    def __init__(self, cpe):
        """
        
        """
        self.cpe                        = cpe
        
        self.thread_check_online        = None      # auto check
        self.thread_userrpc_get_url     = None      # user rpc get_url
        self.thread_inform_eventcode    = None      # inform 
        

 
    @staticmethod
    def get_timer_check_cpes_online():
        return AcsCpeThread.m_timer_check_cpes_online
    @staticmethod
    def set_timer_check_cpes_online(timer):
        AcsCpeThread.m_timer_check_cpes_online = timer
    @staticmethod
    def cancel_timer_check_cpes_online():
        timer = AcsCpeThread.get_timer_check_cpes_online()
        if (timer):
            try:
                timer.cancel()
            except Exception,e:
                pass

    @staticmethod
    def get_timer_check_worklist_status():
        return AcsCpeThread.m_timer_check_worklist_status
    @staticmethod
    def set_timer_check_worklist_status(timer):
        AcsCpeThread.m_timer_check_worklist_status = timer
    @staticmethod
    def cancel_timer_check_worklist_status():
        timer = AcsCpeThread.get_timer_check_worklist_status()
        if (timer):
            try:
                timer.cancel()
            except Exception,e:
                pass
                
     
    def get_thread_check_online(self):
        return self.thread_check_online      
    def set_thread_check_online(self, thread):
        self.thread_check_online = thread

    def get_thread_userrpc_get_url(self):
        return self.thread_userrpc_get_url      
    def set_thread_userrpc_get_url(self, thread):
        self.thread_userrpc_get_url = thread
    def cancel_thread_userrpc_get_url(self):
        d = self.get_thread_userrpc_get_url()        
        try:
            if (not d.called):            
                d.cancel()
        except Exception,e:
            pass                    
            
    def get_thread_inform_eventcode(self):
        return self.thread_inform_eventcode      
    def set_thread_inform_eventcode(self, thread):
        self.thread_inform_eventcode = thread
    def cancel_thread_inform_eventcode(self):
        d = self.get_thread_inform_eventcode()        
        try:
            if (not d.called):            
                d.cancel()
        except Exception,e:
            pass 


    @staticmethod
    def on_exit_tr069_acs():
        """
        """
        from cpe import CPE

        # 1
        for sn,cpe in CPE.m_dict_sn2cpe.items():        

            cpe.cpe_thread.cancel_thread_inform_eventcode()


# --------------------------------------  

def process_cpe_online_geturl(cpe):
    """
    in thread 
    acs active send, not user send
    """    
    from cpe import CPE
    
    ret, err_message =CPE.process_user_rpc_geturl(cpe)
    
    return ret, err_message


def process_cpe_online_callback(args, cpe):

    ret, err_message = args
    if (ret != ERR_SUCCESS):  
        cpe.cpe_property.set_cpe_status("offline")
    else:
        cpe.cpe_property.set_cpe_status("online")
    
    return None   
    

def on_check_cpe_online(interval):
    """
    """
    from cpe import CPE
    
    ret = None

    on_check    = partial(on_check_cpe_online, interval)
    t           = Timer(interval, on_check)
    t.start()  
    AcsCpeThread.set_timer_check_cpes_online(t)  # save

    log.app_info("~~~~~~~~~~%s~~~~~~~~~~" %(interval))

    #copy
    for sn,cpe in CPE.m_dict_sn2cpe.items():

        t1 = cpe.cpe_property.get_onlinetime()

        if (datetime.now()-t1 >= timedelta(seconds=interval)):

            d = threads.deferToThread(process_cpe_online_geturl, cpe)            
            d.addCallback(process_cpe_online_callback, cpe)    

            cpe.cpe_thread.set_thread_check_online(d)  # save


def on_check_cpe_worklist_status(interval):
    """
    """
    
    ret = None

    on_check    = partial(on_check_cpe_worklist_status, interval)
    t           = Timer(interval, on_check)
    t.start()  
    AcsCpeThread.set_timer_check_worklist_status(t)  # save

    log.app_info("~~~~~~~~~~%s~~~~~~~~~~" %(interval))
  
    check_worklist_status()


if __name__ == '__main__':
    pass
 
