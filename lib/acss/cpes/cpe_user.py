#coding:utf-8

# ***************************************************************************
#
#  nwf      2012-08-13      V1.0
#  nwf      2013-05-24      refactor(unify)
#  nwf      2013-06-20      cpe split to (property + soap + user)
# ***************************************************************************


# sys lib
import  sys
import  os


# user lib
from    TR069.lib.common.event      import  *
import  TR069.lib.common.logs.log   as      log 


# ----------------------------------------------------------------------

class CpeUser(object):
    """

    """     
    
    def __init__(self, cpe):
        """
        
        """        
        #  one user one cpe       
        self.cpe                = cpe
        
        self.user_event         = None  # user cmd send event 
        self.user_request       = None  # http request
        self.user_rpc           = None  # rpc obj  
        self.user_rpc_next      = None  
        

    @staticmethod
    def set_user_dictmsg(request, user_dictmsg):
        # nwf 2013-03-13 cpe's property upgrade to request's
        request.user_dictmsg = user_dictmsg
    
    @staticmethod
    def get_user_dictmsg(request):
        return request.user_dictmsg   
        
        
    def set_user_event(self, user_event):
        old = self.get_user_event()
        if (user_event != old):
            self.user_event = user_event
            log.app_info("cpe(sn=%s), user event update(%s->%s)" 
                            %(self.cpe.get_sn(), 
                            get_event_desc(old), get_event_desc(user_event)))                                                              
    def get_user_event(self):
        return self.user_event 

    def set_user_request(self, user_request):
        old = self.get_user_request()
        self.user_request = user_request                                                            
    def get_user_request(self):
        return self.user_request 

                
    def get_next_user_rpc(self):
        return self.user_rpc_next
    def set_next_user_rpc(self, user_rpc_next):
        old = self.get_next_user_rpc()
        if (user_rpc_next != old):
            self.user_rpc_next = user_rpc_next
        

    def set_user_rpc(self, user_rpc):
        old = self.get_user_rpc()
        if (user_rpc != old):
            self.user_rpc = user_rpc
            try:
                log.app_info("cpe(sn=%s),user rpc update(rpc name:%s->%s; rpc args:%s->%s)" 
                            %(self.cpe.get_sn(), 
                            old and old.rpc_name, user_rpc and user_rpc.rpc_name, 
                            old and old.rpc_args, user_rpc and user_rpc.rpc_args))                
            except Exception,e:
                log.app_err("user rpc object error(%s)" %e)  
    def get_user_rpc(self):
        return self.user_rpc              

    def set_user_timer_60s(self, timer):
        """
        get url wait stage1
        """
        self.user_timer_60s = timer                                                            
    def get_user_timer_60s(self):
        return self.user_timer_60s 
        
    def set_user_timer_180s(self, timer):
        """
        get url wait stage2
        """    
        self.user_timer_180s = timer                                                            
    def get_user_timer_180s(self):
        return self.user_timer_180s                   


if __name__ == '__main__':
    pass
 
