#coding:utf-8

"""
    nwf 2013-05-09  create

"""

# sys lib
import  sys
import  os
import  random
import  time
from    datetime                    import datetime
from    datetime                    import timedelta
from    twisted.internet            import threads

# user lib
from    TR069.lib.common.error      import *
from    TR069.lib.common.event      import *
import  TR069.lib.common.logs.log   as log 
import  TR069.lib.acss.acs.webservercfg     as webservercfg
from    TR069.lib.common.function   import  print_trace, get_id
from    eventcode                   import  EventCode
from    cpe_db                      import  *
from    cpe_user_worklist           import  *


class InformMonitor(object):
    """
    """

    m_dict_id2worklistid   = {}       # alarm_id 2 worklistid(start)


    def __init__(self, cpe):
        """        
        """    
        self.cpe                            = cpe                              

    # basic; data---------------------------------------------------------------                      
    def wait_eventcode_init(self, obj):
        """
        """
        obj_database = obj

        id_     = get_id("ID_wait_eventcode")        
        obj.id_ = id_

        # log
        desc = "id = %s" %(id_)
        log.app_info(desc)    

        obj.status      = MONITOR_INFORM_STATUS_INIT  

        # MySQL
        insert_acs_monitor_rules(obj_database)

        return ERR_SUCCESS,obj_database


    def wait_eventcode_start(self, obj):
        """
        """
        obj_database = obj

        for nwf in [1]:          

           # 1 query exist?
            id_ = obj.id_
            obj_database = restore_acs_wait_eventcode(id_)
            if (obj_database is None):
                desc = "id(%s) is not exist." %id_
                log.app_err(desc) 

                break            

            # log
            desc = "id = %s" %(id_)
            log.app_info(desc)

            # MySQL
            time1 = datetime.now()            
            time2 = datetime(9999, 12, 31, 0, 0, 0, 1) # infinite, max 
            update_acs_monitor_rules(obj_database, "STATUS", MONITOR_INFORM_STATUS_START_SUCCESS)
            update_acs_monitor_rules(obj_database, "TIME_START", str(time1))
            update_acs_monitor_rules(obj_database, "TIME_STOP", str(time2))         
        
        return ERR_SUCCESS,obj_database


    def wait_eventcode_stop(self, obj):
        """
        """
        obj_database = obj
        
        for nwf in [1]:          

           # 1 query exist?
            id_ = obj.id_
            obj_database = restore_acs_wait_eventcode(id_)
            if (obj_database is None):
                desc = "id(%s) is not exist." %id_
                log.app_err(desc) 

                break            

            # log
            desc = "id = %s" %(id_)
            log.app_info(desc)

            # MySQL 
            time1 = datetime.now()                     
            update_acs_monitor_rules(obj_database, "STATUS", MONITOR_INFORM_STATUS_STOP_SUCCESS)            
            update_acs_monitor_rules(obj_database, "TIME_STOP", str(time1))              
        
        return ERR_SUCCESS,obj_database
        

    def wait_eventcode_query(self, obj):
        """
        """
        ret             = ERR_FAIL
        obj_database    = obj

        for nwf in [1]:

            sn = obj.sn
            cpe = get_cpe(sn)

            # 1 query exist?
            id_ = obj.id_
            obj_database = restore_acs_wait_eventcode(id_)
            if (obj_database is None):
                desc = "id(%s) is not exist." %id_
                log.app_err(desc) 

                break     

            ret = self.search_informs_for_query_wait_eventcode(obj_database)

        return ret,obj_database        


    def init_alarm(self, obj):
        """
        obj is MsgAlarmInform
        """
        obj_database = obj
          
        id_     = get_id("ID_alarm")        
        obj.id_ = id_

        # log
        desc = "id = %s" %(id_)
        log.app_info(desc)
        
        obj.eventcode   = "X CT-COM ALARM"
        obj.status      = MONITOR_INFORM_STATUS_INIT      
        # MySQL
        insert_acs_monitor_rules(obj_database)
        

        return ERR_SUCCESS,obj_database


    def start_alarm(self, obj):
        """
        obj is MsgAlarmInform
        """
        ret             = ERR_FAIL
        cpe             = None
        obj_database    = obj
        
        for nwf in [1]:          

           # 1 query exist?
            id_ = obj.id_
            obj_database = restore_acs_inform_alarm(id_)
            if (obj_database is None):
                desc = "id(%s) is not exist." %id_
                log.app_err(desc) 

                break            

            # log
            desc = "id = %s" %(id_)
            log.app_info(desc)

            # MySQL
            time1 = datetime.now()
            time2 = datetime(9999, 12, 31, 0, 0, 0, 1) # infinite, max 
            update_acs_monitor_rules(obj_database, "STATUS", MONITOR_INFORM_STATUS_START_BEGIN)
            update_acs_monitor_rules(obj_database, "TIME_START", str(time1))
            update_acs_monitor_rules(obj_database, "TIME_STOP", str(time2))

            # step2 worklist
            cpe = get_cpe(obj_database.sn)
            if (cpe.cpe_property.get_cpe_operator() == "CU"):
                update_acs_monitor_rules(obj_database, "STATUS", MONITOR_INFORM_STATUS_START_SUCCESS)
            else:
                d=threads.deferToThread(start_alarm_worklist, cpe, obj_database) 
                d.addCallback(start_alarm_worklist_callback, obj_database)  
                
            ret = ERR_SUCCESS

        return ret,obj_database


    def stop_alarm(self, obj):
        """
        """
        ret             = ERR_FAIL
        obj_database    = obj
        
        for nwf in [1]:      
        
            # 1 query exist?
            id_ = obj.id_
            obj_database = restore_acs_inform_alarm(id_)
            if (obj_database is None):
                desc = "id(%s) is not exist." %id_
                log.app_err(desc) 

                break            

            # log
            desc = "id = %s" %(id_)
            log.app_info(desc) 

            # MySQL
            time1 = datetime.now()
            update_acs_monitor_rules(obj_database, "STATUS", MONITOR_INFORM_STATUS_STOP_BEGIN)
            update_acs_monitor_rules(obj_database, "TIME_STOP", str(time1))

            # step2 worklist
            cpe = get_cpe(obj_database.sn)
            if (cpe.cpe_property.get_cpe_operator() == "CU"):
                update_acs_monitor_rules(obj_database, "STATUS", MONITOR_INFORM_STATUS_STOP_SUCCESS)
            else:
                d=threads.deferToThread(stop_alarm_worklist, cpe, obj_database) 
                d.addCallback(stop_alarm_worklist_callback, obj_database)            

            ret = ERR_SUCCESS

        return ret,obj_database


    def search_informs_for_query_wait_eventcode(self, obj_database):
        """
        """
        ret             = ERR_FAIL

        ids = get_monitor_result_informid(obj_database.id_)  
        if (ids):
            ret = ERR_SUCCESS

        return ret
        

    def search_informs_by_eventcodes_and_time(self, obj_database):
        """
        """
        ret             = ERR_SUCCESS
        ret_informs     = []
        ret_times       = []

        ret_informs,  ret_times = restore_acs_soap_inform(obj_database)

        return ret,ret_informs,ret_times        


    def get_informs_values(self, informs, times, obj_database):
        """
        """
        values = []
    
        for time1, inform in list(zip(times, informs)):
            
            value = self.get_parameter(inform, obj_database.parameterlist)
            if (value):
                values.append((time1, value)) 

        # save
        obj_database.parameter_values = values


    def get_alarm_parameter(self, obj):
        """
        obj is MsgAlarmInform
        """
        ret             = ERR_FAIL
        obj_database    = obj
        
        for nwf in [1]:      
        
            # 1 query exist?
            id_ = obj.id_
            obj_database = restore_acs_inform_alarm(id_)
            if (obj_database is None):
                desc = "id(%s) is not exist." %id_
                log.app_err(desc) 

                break            

            # log
            desc = "id = %s" %(id_)
            log.app_info(desc)

            cpe = self.cpe
            if (cpe.cpe_property.get_cpe_operator() == "CU"):
                ret = self.get_alarm_parameter_4cu(obj_database)
            else:
                ret, ret_informs, ret_times = \
                    self.search_informs_by_eventcodes_and_time(obj_database) 
                if (ret == ERR_SUCCESS):
                    self.get_informs_values(ret_informs, ret_times, obj_database)

        return ret,obj_database


    def get_alarm_parameter_4cu(self, obj_database):
        """
        obj is MsgAlarmInform
        """
        ret             = ERR_SUCCESS
        ret_informs     = []
        ret_times       = []
        values          = []

        ret_informs,  ret_times = restore_acs_soap_inform_str(obj_database)
            
        for time1, inform in list(zip(ret_times, ret_informs)):            
            values.append((time1, inform)) 

        # save
        obj_database.parameter_values = values       

        return ret


    def init_monitor(self, obj):
        """
        obj is MsgMonitorInform
        """
        obj_database = obj
        
        id_     = get_id("ID_monitor")         
        obj.id_ = id_

        # log
        desc = "id = %s" %(id_)
        log.app_info(desc)        
        
        obj.eventcode   = "X CT-COM MONITOR"
        obj.status      = MONITOR_INFORM_STATUS_INIT             
        # MySQL
        insert_acs_monitor_rules(obj_database)        

        return ERR_SUCCESS,obj_database
        

    def start_monitor(self, obj):
        """
        obj is MsgMonitorInform
        """
        ret             = ERR_FAIL
        obj_database    = obj
        
        for nwf in [1]:          

           # 1 query exist?
            id_ = obj.id_
            obj_database = restore_acs_inform_monitor(id_)
            if (obj_database is None):
                desc = "id(%s) is not exist." %id_
                log.app_err(desc) 

                break            

            # log
            desc = "id = %s" %(id_)
            log.app_info(desc)
 
            time1 = datetime.now() 
            time2 = datetime(9999, 12, 31, 0, 0, 0, 1) # infinite, max 
            # MySQL
            update_acs_monitor_rules(obj_database, "STATUS", MONITOR_INFORM_STATUS_START_BEGIN)
            update_acs_monitor_rules(obj_database, "TIME_START", str(time1))
            update_acs_monitor_rules(obj_database, "TIME_STOP", str(time2))


            # step2 worklist
            cpe = get_cpe(obj_database.sn)

            d=threads.deferToThread(start_monitor_worklist, cpe, obj_database) 
            d.addCallback(start_monitor_worklist_callback, obj_database)  
            ret = ERR_SUCCESS            
            
        return ret,obj_database


    def stop_monitor(self, obj):
        """
        """
        ret             = ERR_FAIL
        obj_database    = obj
        
        for nwf in [1]:      
        
            # 1 query exist?
            id_ = obj.id_
            obj_database = restore_acs_inform_monitor(id_)
            if (obj_database is None):
                desc = "id(%s) is not exist." %id_
                log.app_err(desc) 

                break            

            # log
            desc = "id = %s" %(id_)
            log.app_info(desc)
            
            time1 = datetime.now() 
            # MySQL
            update_acs_monitor_rules(obj_database, "STATUS", MONITOR_INFORM_STATUS_STOP_BEGIN)
            update_acs_monitor_rules(obj_database, "TIME_STOP", str(time1))
            
            # step2 worklist
            cpe = get_cpe(obj_database.sn)

            d=threads.deferToThread(stop_monitor_worklist, cpe, obj_database) 
            d.addCallback(stop_monitor_worklist_callback, obj_database)              

            ret = ERR_SUCCESS

        return ret,obj_database


    def get_monitor_parameter(self, obj):
        """
        obj is MsgAlarmInform
        """
        ret             = ERR_FAIL
        obj_database    = obj
        
        for nwf in [1]:      
        
            # 1 query exist?
            id_ = obj.id_
            obj_database = restore_acs_inform_monitor(id_)
            if (obj_database is None):
                desc = "id(%s) is not exist." %id_
                log.app_err(desc) 

                break            

            # log
            desc = "id = %s" %(id_)
            log.app_info(desc)

            ret, ret_informs, ret_times = \
                self.search_informs_by_eventcodes_and_time(obj_database) 
            if (ret == ERR_SUCCESS):
                self.get_informs_values(ret_informs, ret_times, obj_database)            

        return ret,obj_database


    def get_parameter(self, inform1, parameterlist):
        """
        """               
        ret_value = None
        
        for parameter in inform1.result.ParameterList:
            if (parameter.Name == parameterlist):
                ret_value = parameter.Value
                break

        return ret_value



    # msg --------------------------------------------------------------------
    @staticmethod    
    def process_config(msg, obj):    
        """
        request = user request 
        """  
        ret             = None
        cpe             = None     
        obj_database    = obj   # default
        msg_rsp         = msg + 2
        

        for nwf in [1]:
        
            if msg == EV_WAIT_EVENTCODE_INIT_RQST:
                ret, msg_rsp, obj_database = on_rx_user_wait_eventcode_init(msg, obj)
            elif msg == EV_WAIT_EVENTCODE_START_RQST:
                ret, msg_rsp, obj_database = on_rx_user_wait_eventcode_start(msg, obj)  
            elif msg == EV_WAIT_EVENTCODE_STOP_RQST:
                ret, msg_rsp, obj_database = on_rx_user_wait_eventcode_stop(msg, obj)
            elif msg == EV_WAIT_EVENTCODE_QUERY_RQST:
                ret, msg_rsp, obj_database = on_rx_user_wait_eventcode_query(msg, obj)                 


            elif msg == EV_INIT_ALARM_RQST:
                ret, msg_rsp, obj_database = on_rx_user_init_alarm(msg, obj)
                
            elif msg == EV_START_ALARM_RQST:
                ret, msg_rsp, obj_database = on_rx_user_start_alarm(msg, obj)

            elif msg == EV_STOP_ALARM_RQST:
                ret, msg_rsp, obj_database = on_rx_user_stop_alarm(msg, obj)

            elif msg == EV_GET_ALARM_PARAMETER_RQST:
                ret, msg_rsp, obj_database = on_rx_user_get_alarm_parameter(msg, obj)                


            elif msg == EV_INIT_MONITOR_RQST:
                ret, msg_rsp, obj_database = on_rx_user_init_monitor(msg, obj)

            elif msg == EV_START_MONITOR_RQST:
                ret, msg_rsp, obj_database = on_rx_user_start_monitor(msg, obj)

            elif msg == EV_STOP_MONITOR_RQST:
                ret, msg_rsp, obj_database = on_rx_user_stop_monitor(msg, obj)

            elif msg == EV_GET_MONITOR_PARAMETER_RQST:
                ret, msg_rsp, obj_database = on_rx_user_get_monitor_parameter(msg, obj) 

            elif msg == EV_QUERY_ALARM_RQST:
                ret, msg_rsp, obj_database = on_rx_query_alarm_status(msg, obj)  

            elif msg == EV_QUERY_MONITOR_RQST:
                ret, msg_rsp, obj_database = on_rx_query_monitor_status(msg, obj)                 
                                    
            else :
                ret = ERR_FATAL
                
                desc = "msg(%s) is not recognize" %msg
                log.app_err(desc)
                
                break                
        
        return ret, msg_rsp, obj_database


# msg --------------------------------------------------------------------          
def get_cpe(sn): 
    from cpe import CPE

    cpe = CPE.get_cpe(sn)            
    if (cpe is None):
        cpe = CPE.add(sn, None)
        
        desc = "cpe sn(%s) not online, user create." %(sn)
        log.app_info(desc)      

    return cpe


def on_rx_user_wait_eventcode_init(msg, obj):    
    """
    """
    ret             = ERR_FAIL  # default
    cpe             = None        
    msg_rsp         = msg + 2 # default
    
    #    
    for nwf in [1]:
        if (not isinstance(obj, MsgWaitEventCode)):
            log.app_err("obj is not MsgWaitEventCode")  
            ret = ERR_FATAL
            break

        sn = obj.sn
        cpe = get_cpe(sn)

        # obj do    
        ret, obj_database = cpe.inform_monitor.wait_eventcode_init(obj)
        if (ret == ERR_SUCCESS):
            msg_rsp = msg + 1            
                               
    return ret,msg_rsp,obj_database
    
       
def on_rx_user_wait_eventcode_start(msg, obj):    
    """
    """
    ret             = ERR_FAIL  # default
    cpe             = None        
    msg_rsp         = msg + 2 # default
    
    #    
    for nwf in [1]:
        if (not isinstance(obj, MsgWaitEventCode)):
            log.app_err("obj is not MsgWaitEventCode")  
            ret = ERR_FATAL
            break

        sn = obj.sn
        cpe = get_cpe(sn)

        # obj do    
        ret, obj_database = cpe.inform_monitor.wait_eventcode_start(obj)
        if (ret == ERR_SUCCESS):
            msg_rsp = msg + 1            
                               
    return ret,msg_rsp,obj_database


def on_rx_user_wait_eventcode_stop(msg, obj):    
    """
    """
    ret             = ERR_FAIL  # default
    cpe             = None        
    msg_rsp         = msg + 2 # default
    
    #    
    for nwf in [1]:
        if (not isinstance(obj, MsgWaitEventCode)):
            log.app_err("obj is not MsgWaitEventCode")  
            ret = ERR_FATAL
            break

        sn = obj.sn
        cpe = get_cpe(sn)

        # obj do    
        ret, obj_database = cpe.inform_monitor.wait_eventcode_stop(obj)
        if (ret == ERR_SUCCESS):
            msg_rsp = msg + 1            
                               
    return ret,msg_rsp,obj_database

  
def on_rx_user_wait_eventcode_query(msg, obj):    
    """
    """
    ret             = ERR_FAIL  # default
    cpe             = None        
    msg_rsp         = msg + 2 # default
    obj_database    = obj
    
    #    
    for nwf in [1]:
        if (not isinstance(obj, MsgWaitEventCode)):
            log.app_err("obj is not MsgWaitEventCode")  
            ret = ERR_FATAL
            break

        sn = obj.sn
        cpe = get_cpe(sn) 

        # obj do    
        ret, obj_database = cpe.inform_monitor.wait_eventcode_query(obj)
        if (ret == ERR_SUCCESS):
            msg_rsp = msg + 1            
                               
    return ret,msg_rsp,obj_database


def on_rx_user_init_alarm(msg, obj):    
    """
    """
    ret = ERR_FAIL  # default
    cpe = None        
    msg_rsp = msg + 2 # default
    
    #    
    for nwf in [1]:
        if (not isinstance(obj, MsgAlarmInform)):
            log.app_err("obj is not MsgAlarmInform")  
            ret = ERR_FATAL
            break

        sn = obj.sn
        cpe = get_cpe(sn) 

        # obj do    
        ret, obj_database = cpe.inform_monitor.init_alarm(obj)
        if (ret == ERR_SUCCESS):        
            msg_rsp = msg + 1
                   
    return ret,msg_rsp,obj_database

   
def on_rx_user_start_alarm(msg, obj):    
    """
    """
    ret = ERR_FAIL  # default
    cpe = None        
    msg_rsp = msg + 2 # default
    
    #    
    for nwf in [1]:
        if (not isinstance(obj, MsgAlarmInform)):
            log.app_err("obj is not MsgAlarmInform")  
            ret = ERR_FATAL
            break

        sn = obj.sn
        cpe = get_cpe(sn) 

        # obj do    
        ret, obj_database = cpe.inform_monitor.start_alarm(obj)
        if (ret == ERR_SUCCESS):        
            msg_rsp = msg + 1
                   
    return ret,msg_rsp,obj_database

   
def on_rx_user_stop_alarm(msg, obj):    
    """
    """
    ret = ERR_FAIL  # default
    cpe = None        
    msg_rsp = msg + 2 # default
    
    #    
    for nwf in [1]:
        if (not isinstance(obj, MsgAlarmInform)):
            log.app_err("obj is not MsgAlarmInform")  
            ret = ERR_FATAL
            break

        sn = obj.sn
        cpe = get_cpe(sn) 
            
        # obj do    
        ret, obj_database = cpe.inform_monitor.stop_alarm(obj)        
        if (ret == ERR_SUCCESS):
            msg_rsp = msg + 1
                   
    return ret,msg_rsp,obj_database

   
def on_rx_user_get_alarm_parameter(msg, obj):    
    """
    """
    ret = ERR_FAIL  # default
    cpe = None        
    msg_rsp = msg + 2 # default
    
    #    
    for nwf in [1]:
        if (not isinstance(obj, MsgAlarmInform)):
            log.app_err("obj is not MsgAlarmInform")  
            ret = ERR_FATAL
            break

        sn = obj.sn
        cpe = get_cpe(sn) 
            
        # obj do    
        ret, obj_database = cpe.inform_monitor.get_alarm_parameter(obj)        
        if (ret == ERR_SUCCESS):
            msg_rsp = msg + 1
                   
    return ret,msg_rsp,obj_database   


def on_rx_user_init_monitor(msg, obj):    
    """
    """
    ret = ERR_FAIL  # default
    cpe = None        
    msg_rsp = msg + 2 # default
    
    #    
    for nwf in [1]:
        if (not isinstance(obj, MsgMonitorInform)):
            log.app_err("obj is not MsgMonitorInform")  
            ret = ERR_FATAL
            break

        sn = obj.sn
        cpe = get_cpe(sn)
            
        # obj do    
        ret, obj_database = cpe.inform_monitor.init_monitor(obj)        
        if (ret == ERR_SUCCESS):
            msg_rsp = msg + 1
                   
    return ret,msg_rsp,obj_database

  
def on_rx_user_start_monitor(msg, obj):    
    """
    """
    ret = ERR_FAIL  # default
    cpe = None        
    msg_rsp = msg + 2 # default
    
    #    
    for nwf in [1]:
        if (not isinstance(obj, MsgMonitorInform)):
            log.app_err("obj is not MsgMonitorInform")  
            ret = ERR_FATAL
            break

        sn = obj.sn
        cpe = get_cpe(sn)
            
        # obj do    
        ret, obj_database = cpe.inform_monitor.start_monitor(obj)        
        if (ret == ERR_SUCCESS):
            msg_rsp = msg + 1
                   
    return ret,msg_rsp,obj_database

 
def on_rx_user_stop_monitor(msg, obj):    
    """
    """
    ret = ERR_FAIL  # default
    cpe = None        
    msg_rsp = msg + 2 # default
    
    #    
    for nwf in [1]:
        if (not isinstance(obj, MsgMonitorInform)):
            log.app_err("obj is not MsgMonitorInform")  
            ret = ERR_FATAL
            break

        sn = obj.sn
        cpe = get_cpe(sn) 
            
        # obj do    
        ret, obj_database = cpe.inform_monitor.stop_monitor(obj)        
        if (ret == ERR_SUCCESS):
            msg_rsp = msg + 1
                   
    return ret,msg_rsp,obj_database

   
def on_rx_user_get_monitor_parameter(msg, obj):    
    """
    """
    ret = ERR_FAIL  # default
    cpe = None        
    msg_rsp = msg + 2 # default
    
    #    
    for nwf in [1]:
        if (not isinstance(obj, MsgMonitorInform)):
            log.app_err("obj is not MsgMonitorInform")  
            ret = ERR_FATAL
            break

        sn = obj.sn
        cpe = get_cpe(sn)  
            
        # obj do    
        ret, obj_database = cpe.inform_monitor.get_monitor_parameter(obj)        
        if (ret == ERR_SUCCESS):
            msg_rsp = msg + 1
                   
    return ret,msg_rsp,obj_database 


def on_rx_query_alarm_status(msg, obj):
    """
    return obj database.status
    """
    
    ret             = ERR_FAIL
    msg_rsp         = msg + 2
    obj_database    = obj

    for nwf in [1]:

        sn = obj.sn
        cpe = get_cpe(sn)

        # 1 query exist?
        id_ = obj.id_
        obj_database = restore_acs_inform_alarm(id_)
        if (obj_database is None):
            desc = "id(%s) is not exist." %id_
            log.app_err(desc) 

            break     

        ret = ERR_SUCCESS
        msg_rsp = msg + 1

    return ret,msg_rsp,obj_database 

    
def on_rx_query_monitor_status(msg, obj):
    """
    
    """
    
    ret             = ERR_FAIL
    msg_rsp         = msg + 2
    obj_database    = obj

    for nwf in [1]:

        sn = obj.sn
        cpe = get_cpe(sn)

        # 1 query exist?
        id_ = obj.id_
        obj_database = restore_acs_inform_monitor(id_)
        if (obj_database is None):
            desc = "id(%s) is not exist." %id_
            log.app_err(desc) 

            break     

        ret = ERR_SUCCESS
        msg_rsp = msg + 1

    return ret,msg_rsp,obj_database 
    

def start_alarm_worklist(cpe, obj_alarm):
    """
    obj_alarm is MsgAlarmInform
    """
    
    ret         = ERR_FAIL
    err_message = ""        

    sn = cpe.get_sn()
    
    for nwf in [1]:
    
        # physic worklist ---------------        
        dict_data = {"parameterlist":   obj_alarm.parameterlist, 
                    "limit_max":        obj_alarm.limit_max,
                    "limit_min":        obj_alarm.limit_min, 
                    "timelist":         obj_alarm.timelist, 
                    "mode":             obj_alarm.mode}
        obj = MsgWorklistBuild("Inform_Monitor_Alarm_Start", dict_data)                 
        obj_database = EventCode.auto_build_bind_physic_worklist(cpe, obj) 

        # 
        save_id2worklistid(obj_alarm.id_, obj_database.id_)
        
        try:
            ret, err_message = EventCode.tx_worklist_exec(obj_database)        
            ret = EventCode.rx_worklist_exec(ret, err_message)      
            if (ret == ERR_SUCCESS):
            
                ret, err_message = EventCode.wait_worklist_exec_finish(obj_database)
                if ret == ERR_SUCCESS:                 
                    
                    desc = "start_alarm_worklist(id=%s) success." %(obj_database.id_)
                    log.app_info(desc) 

                    obj_alarm.dict_ret["str_result"] = desc
                                        
                else:
                    # worklist(id=worklist_2014-07-08_11:48:15.781_82424709) status is not success(fail)
                    # nwf 2014-07-08; +worklist fail
                    obj_db = restore_acs_worklist(obj_database.id_)
                    err_message = err_message + "\n" + obj_db.dict_ret["str_result"]
                    log.app_err(err_message)
 
                    obj_alarm.dict_ret["str_result"] = err_message
                    break
            else:
                log.app_err(err_message)

                obj_alarm.dict_ret["str_result"] = err_message
                break
                
        except Exception,e:
            print_trace(e) 	

            obj_alarm.dict_ret["str_result"] = e
            break

        ret = ERR_SUCCESS   
    # save to DB
    update_acs_monitor_rules(obj_alarm, "STATUS_DESC", obj_alarm.dict_ret["str_result"])

    return ret
    

def start_alarm_worklist_callback(args, obj):
    """
    obj is MsgAlarmInform
    """
    
    ret         = ERR_FAIL

    ret = args      
    if (ret == ERR_SUCCESS):
        obj.status = MONITOR_INFORM_STATUS_START_SUCCESS
    else:
        obj.status = MONITOR_INFORM_STATUS_START_FAIL

    update_acs_monitor_rules(obj, "STATUS", obj.status)

    return None


def stop_alarm_worklist(cpe, obj_alarm):
    """
    obj_alarm is MsgAlarmInform
    """
    
    ret         = ERR_FAIL
    err_message = ""        

    sn = cpe.get_sn()
    
    for nwf in [1]:
    
        # physic worklist ---------------
        start_worklist_id = get_id2worklistid(obj_alarm.id_)
        pop_id2worklistid(obj_alarm.id_)
        
        node_add_object = get_worklist_node_add_object(start_worklist_id)
        if (not node_add_object):
            desc = "node_add_object is None." 
            log.app_err(desc)             
        pop_worklist_node_add_object(obj_alarm.id_)
        
        dict_data = {"node_add_object":node_add_object}

        
        obj = MsgWorklistBuild("Inform_Monitor_Alarm_Stop", dict_data)                 
        obj_database = EventCode.auto_build_bind_physic_worklist(cpe, obj)   
        
        try:
            ret, err_message = EventCode.tx_worklist_exec(obj_database)        
            ret = EventCode.rx_worklist_exec(ret, err_message)      
            if (ret == ERR_SUCCESS):
            
                ret, err_message = EventCode.wait_worklist_exec_finish(obj_database)
                if ret == ERR_SUCCESS:           
                    desc = "stop_alarm_worklist success." 
                    log.app_info(desc) 

                    obj_alarm.dict_ret["str_result"] = desc
                else:
                    log.app_err(err_message)

                    obj_alarm.dict_ret["str_result"] = err_message
                    break
            else:
                log.app_err(err_message)

                obj_alarm.dict_ret["str_result"] = err_message
                break
        except Exception,e:
            print_trace(e) 	

            obj_alarm.dict_ret["str_result"] = e
            break

        ret = ERR_SUCCESS   

    return ret
    

def stop_alarm_worklist_callback(args, obj):
    """
    obj is MsgAlarmInform
    """
    
    ret         = ERR_FAIL

    ret = args      
    if (ret == ERR_SUCCESS):
        obj.status = MONITOR_INFORM_STATUS_STOP_SUCCESS
    else:
        obj.status = MONITOR_INFORM_STATUS_STOP_FAIL

    update_acs_monitor_rules(obj, "STATUS", obj.status)

    return None



def start_monitor_worklist(cpe, obj_monitor):
    """
    obj_alarm is MsgMonitorInform
    """
    
    ret         = ERR_FAIL
    err_message = ""        

    sn = cpe.get_sn()
    
    for nwf in [1]:
    
        # physic worklist ---------------        
        dict_data = {"parameterlist":   obj_monitor.parameterlist, 
                    "timelist":         obj_monitor.timelist}
        obj = MsgWorklistBuild("Inform_Monitor_Monitor_Start", dict_data)           
        obj_database = EventCode.auto_build_bind_physic_worklist(cpe, obj)   

        save_id2worklistid(obj_monitor.id_, obj_database.id_)        
        
        try:
            ret, err_message = EventCode.tx_worklist_exec(obj_database)        
            ret = EventCode.rx_worklist_exec(ret, err_message)      
            if (ret == ERR_SUCCESS):
            
                ret, err_message = EventCode.wait_worklist_exec_finish(obj_database)
                if ret == ERR_SUCCESS:                  

                    desc = "start_monitor_worklist(id=%s) success." %(obj_database.id_)
                    log.app_info(desc) 
                    
                    obj_monitor.dict_ret["str_result"] = desc                    

                else:
                    # worklist(id=worklist_2014-07-08_11:48:15.781_82424709) status is not success(fail)
                    # nwf 2014-07-08; +worklist fail
                    obj_db = restore_acs_worklist(obj_database.id_)
                    err_message = err_message + "\n" + obj_db.dict_ret["str_result"]
                    log.app_err(err_message)

                    obj_monitor.dict_ret["str_result"] = err_message
                    break
            else:
                log.app_err(err_message)

                obj_monitor.dict_ret["str_result"] = err_message
                break
                
        except Exception,e:
            print_trace(e) 	

            obj_monitor.dict_ret["str_result"] = e
            break

        ret = ERR_SUCCESS  
    # save to DB
    update_acs_monitor_rules(obj_monitor, "STATUS_DESC", obj_monitor.dict_ret["str_result"])        

    return ret
    

def start_monitor_worklist_callback(args, obj):
    """
    obj is MsgMonitorInform
    """
    
    ret         = ERR_FAIL

    ret = args      
    if (ret == ERR_SUCCESS):
        obj.status = MONITOR_INFORM_STATUS_START_SUCCESS
    else:
        obj.status = MONITOR_INFORM_STATUS_START_FAIL

    update_acs_monitor_rules(obj, "STATUS", obj.status)
    
    return None


def stop_monitor_worklist(cpe, obj_monitor):
    """
    obj_alarm is MsgMonitorInform
    """
    
    ret         = ERR_FAIL
    err_message = ""        

    sn = cpe.get_sn()
    
    for nwf in [1]:
    
        # physic worklist ---------------  
        start_worklist_id = get_id2worklistid(obj_monitor.id_)
        pop_id2worklistid(obj_monitor.id_)
        
        node_add_object = get_worklist_node_add_object(start_worklist_id)
        if (not node_add_object):
            desc = "node_add_object is None." 
            log.app_err(desc)             
        pop_worklist_node_add_object(obj_monitor.id_)
        
        dict_data = {"node_add_object":node_add_object}
        obj = MsgWorklistBuild("Inform_Monitor_Monitor_Stop", dict_data)                 
        obj_database = EventCode.auto_build_bind_physic_worklist(cpe, obj)        
        
        try:
            ret, err_message = EventCode.tx_worklist_exec(obj_database)        
            ret = EventCode.rx_worklist_exec(ret, err_message)      
            if (ret == ERR_SUCCESS):
            
                ret, err_message = EventCode.wait_worklist_exec_finish(obj_database)
                if ret == ERR_SUCCESS:           
                    desc = "stop_monitor_worklist success."
                    log.app_info(desc) 

                    obj_monitor.dict_ret["str_result"] = desc
                else:
                    log.app_err(err_message)

                    obj_monitor.dict_ret["str_result"] = err_message
                    break
            else:
                log.app_err(err_message)

                obj_monitor.dict_ret["str_result"] = err_message
                break
        except Exception,e:
            print_trace(e) 	

            obj_monitor.dict_ret["str_result"] = e
            break

        ret = ERR_SUCCESS   

    return ret
    

def stop_monitor_worklist_callback(args, obj):
    """
    obj is MsgMonitorInform
    """
    
    ret         = ERR_FAIL

    ret = args      
    if (ret == ERR_SUCCESS):
        obj.status = MONITOR_INFORM_STATUS_STOP_SUCCESS
    else:
        obj.status = MONITOR_INFORM_STATUS_STOP_FAIL

    update_acs_monitor_rules(obj, "STATUS", obj.status)

    return None    



# -------------------------------------- assist

def save_id2worklistid(id_, worklistid):
    InformMonitor.m_dict_id2worklistid[id_] = worklistid
    
def get_id2worklistid(id_):
    return InformMonitor.m_dict_id2worklistid.get(id_, None)

def pop_id2worklistid(id_):
    InformMonitor.m_dict_id2worklistid.pop(id_, None)


# global 
__all__ = [ "save_id2worklistid", 
            "get_id2worklistid",
            "pop_id2worklistid",

          ]
          
