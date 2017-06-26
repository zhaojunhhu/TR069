#coding:utf-8

"""
    nwf 2013-02-26  V2.0

"""

# sys lib
import  sys
import  os
import  threading
from    twisted.internet import threads
from    cStringIO import StringIO
import  pickle
import  time

# user lib
from    TR069.lib.common.error      import  *
from    TR069.lib.common.event      import  *
import  TR069.lib.common.logs.log   as      log 
from    TR069.lib.common.httpclient import  HttpClient
from    TR069.lib.common.function   import  print_trace, get_id
import  TR069.lib.acss.acs.webservercfg     as      webservercfg

from    cpe_user_worklist           import  *
from    cpe_db                      import  *
from    cpe_thread                  import  AcsCpeThread


class EventCode(object):
    """
    """

    def __init__(self):
        """     
        """   
        pass

    @staticmethod    
    def auto_build_bind_physic_worklist(cpe, obj):    
        """

        """  

        ret = ERR_FAIL           
        msg = None
        msg_rsp = None
        obj_database = None

        sn = cpe.get_sn()
        
        # auto build         
        msg = EV_WORKLIST_BUILD_RQST
        obj.group = "SYS"
        ret, msg_rsp, obj_database = on_rx_worklist_build(msg, obj)           

        # auto bind
        msg = EV_WORKLIST_BIND_PHISIC_RQST
        obj = MsgWorklistBindPhysical(obj_database.id_, sn)            
        ret, msg_rsp, obj_database = on_rx_worklist_bind_physic(msg, obj)                 
      
        return obj_database        


    def sort_inform_eventcodes(self, events):

        eventcodes = []

        # get eventcodes
        for event in events:
            eventcodes.append(event.EventCode)

        # sort eventcodes
        eventcodes2 = []
        for eventcode in eventcodes:
            if ("0 BOOTSTRAP" in eventcode):
                eventcodes2.insert(0, eventcode)
            else:
                eventcodes2.append(eventcode)
            
        return eventcodes2


    def process_inform_events(self, events, cpe):
        """
        """
        from auto_process import process_operator_eventcodes
        
        ret = ERR_SUCCESS        

        eventcodes = self.sort_inform_eventcodes(events)
                    
        d=threads.deferToThread(process_operator_eventcodes, eventcodes, cpe)  
        cpe.cpe_thread.set_thread_inform_eventcode(d)  
                              
        return ret
       
        
    @staticmethod    
    def tx_worklist_exec(obj_database, timeout=webservercfg.ACS_WAIT_AGENT_WORKLIST_EXEC_RSP_TIMEOUT):    
        """
        in thread 
        obj is MsgWorklist
        """                        

        ret         = ERR_FAIL
        err_message = ""    


        try:                                  

            cls1= obj_database
            strio = StringIO()
            pickle.dump(cls1, strio)    
            v_msg = EV_WORKLIST_EXECUTE_RQST
            
            dict1                   ={}
            dict1[KEY_MESSAGE]      = int(v_msg) 
            dict1[KEY_OBJECT]       = strio.getvalue()    
            dict1[KEY_SN]           = obj_database.sn                                
            dict1[KEY_MESSAGE_TYPE] = EVENT_WORKLIST_GROUP
            dict1[KEY_QUEUE]        = QUEUE_WAIT
            dict1[KEY_SENDER]       = KEY_SENDER_ACS  
            dict1[KEY_SEQUENCE]     = get_id("Seq")

            msg = str(dict1)
            
            url = "http://%s:%s%s" %(webservercfg.AGENT_HTTP_IP, webservercfg.AGENT_HTTP_PORT, webservercfg.ACS2AGENT_PAGE)
            httpclient1 = HttpClient(url, timeout)             

            ret, err_message = httpclient1.send_message(msg)  
                    
        except Exception, e:
            print_trace(e) 
            err_message = e
        
        return ret, err_message


    @staticmethod    
    def rx_worklist_exec(ret, err_message):    
        """
        ret =ERR_SUCCESS mean tcp echo back
        """
        ret_worklist = ERR_FAIL  # worklist ret
                
        # agent echo ok?
        if (ret != ERR_SUCCESS):
            return ret_worklist    

        for nwf in [1]:        
        
            # dict in?
            try:
                body = err_message
                dict1 = eval(body)
            except Exception,e:
                log.app_err("isn't a dict(%s)." %(e))
                break
                
            # have message ?
            msg = dict1.get(KEY_MESSAGE)
            if (not msg):
                log.app_err("dict KEY_MESSAGE missing(%s)." %(KEY_MESSAGE))
                break                
            log.app_info("receive user message=%s" %(get_event_desc(msg))) 

            # have obj?
            v_obj = dict1.get(KEY_OBJECT)
            if (not v_obj):
                log.app_err("dict KEY_OBJECT missing(%s)." %(KEY_OBJECT))
                break
                
            try:
                strio = StringIO(v_obj)  
                obj_reserve = pickle.load(strio)
            except Exception,e:
                log.app_err("dict KEY_OBJECT pick load fail.")
                break  


            # match status
            obj_database = restore_acs_part_worklist(obj_reserve.id_)
            if (not obj_database):
                log.app_err("worklist id(%s) not in acs" %obj_reserve.id_)
                break
                    
        if (int(msg) - EV_WORKLIST_EXECUTE_RQST == 1):
            ret_worklist = ERR_SUCCESS
        
        return ret_worklist     


    @staticmethod    
    def wait_worklist_exec_finish(obj_database):    
        """
        """          
        ret = ERR_FAIL
        err_message = ""
        
        event1 = threading.Event() 
        save_worklist_event(obj_database.id_, event1)
        
        timeout = webservercfg.ACS_WAIT_AGENT_WORKLIST_EXEC_RSP_TIMEOUT + \
                    webservercfg.ACS_WAIT_WORKLIST_EXEC_FINISH_TIMEOUT
                    
        log.app_info("worklist(id=%s) begin wait finish." %obj_database.id_)
        event1.wait(timeout)
        log.app_info("worklist(id=%s) end wait finish." %obj_database.id_)
                
        if (event1.isSet()):  

            # update obj_database
            obj_database = restore_acs_part_worklist(obj_database.id_)
            
            if (obj_database.status == WORK_LIST_STATUS_SUCCESS):
                ret = ERR_SUCCESS
            else:
                err_message = "worklist(id=%s) status is not success(%s)" %(obj_database.id_, obj_database.status)
        else:
            err_message = "worklist(id=%s) timeout(%s seconds)" %(obj_database.id_, timeout)

        del event1
        pop_worklist_event(obj_database.id_)
        
        return ret, err_message        
