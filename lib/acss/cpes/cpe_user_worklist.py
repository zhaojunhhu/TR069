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
import  copy 
from    datetime                    import  datetime
import  random
from    twisted.internet            import  reactor
import  re

# user lib
from    TR069.lib.common.error      import  *
from    TR069.lib.common.event      import  *
import  TR069.lib.common.logs.log   as      log 
from    TR069.lib.common.function   import  print_trace, get_id, create_id
import  TR069.lib.acss.acs.webservercfg     as      webservercfg
from    cpe_db                      import  *

# ----------------------------------------------------------------------

class CpeUserWorklist(object):
    """
    """    

    m_dict_id2event             = {}
    m_dict_id2timer             = {}
    m_dict_id2node_add_object   = {}
    #m_dict_desc_id = {}
    
    def __init__(self, sn):
        """
        
        """
        pass         


    @staticmethod    
    def process_worklist4user(msg, obj):    
        """
        build + bind + get + report == query(sync, block, but quickly)
        exec_rqst is async
        """  
        ret = None
        cpe = None       
        msg_rsp = msg +2 # default
        obj_database = obj 

        for nwf in [1]:
            if (msg == EV_WORKLIST_BUILD_RQST):
                ret, msg_rsp, obj_database = on_rx_worklist_build(msg, obj)
                
            elif (msg == EV_WORKLIST_BIND_PHISIC_RQST):
                ret, msg_rsp, obj_database  = on_rx_worklist_bind_physic(msg, obj)

            elif (msg == EV_WORKLIST_BIND_LOGIC_RQST):
                ret, msg_rsp, obj_database = on_rx_worklist_bind_logic(msg, obj)

            elif (msg == EV_WORKLIST_RESERVE_RQST):
                ret, msg_rsp, obj_database = on_rx_worklist_reserve(msg, obj)

            elif (msg == EV_WORKLIST_EXEC_START_RQST):
                ret, msg_rsp, obj_database = on_rx_worklist_exec_start(msg, obj)

            elif (msg == EV_WORKLIST_EXEC_FINISH_RQST):
                ret, msg_rsp, obj_database = on_rx_worklist_exec_finish(msg, obj)

            elif (msg == EV_WORKLIST_QUERY_RQST):
                ret, msg_rsp, obj_database = on_rx_worklist_query(msg, obj)                
            else :
                ret = ERR_FAIL

                desc = "msg(%s) is not recognize" %msg
                log.app_err(desc)
                
                break                

            if (ret == ERR_FATAL):
                # msg is not recognize
                break
        
        return ret, msg_rsp, obj_database
    

# msg --------------------------------------------------------------------      
def on_rx_worklist_build(msg, obj):    
    """ 
    1 generated id
    2 change status
    3 collect obj
    """
    ret = ERR_FAIL  # default      
    msg_rsp = msg + 2 # default fail
    obj_database = obj

    for nwf in [1]:
        # check args
        if (not isinstance(obj, MsgWorklistBuild)):
            log.app_err("obj is not MsgWorklistBuild") 
            
            ret = ERR_FATAL
            break                

        # new obj; nwf 2014-06-10
        #obj_database = MsgWorklist()
        
        # 1 generated id
        #id_ = get_id("ID_worklist")
        id_desc = create_id('worklist')
        
        #obj_database.id_ = id_
        #log.app_info("id =%s, worklist_name=%s" %(id_desc, obj.worklist_name))
        obj_database.time_build = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 兼容BS和RF的工单新建操作 Alter by lizn 2014-05-20
        # 新建过程本没有逻辑工单和物理工单之分，但BS的逻辑工单没有绑定操作，故需提前处理，导致：
        # 1)BS的逻辑工单新建和绑定时间一致
        # 2)RF的新建工单都默认为物理工单
        # 2 update  args
        if obj.dict_data.has_key('username'):   # BS的逻辑工单 2014-05-08
            obj_database.type_ = WORK_LIST_TYPE_LOGIC
            obj_database.username = obj.dict_data.pop('username')
            obj_database.userid = obj.dict_data.pop('userid')
            obj_database.status = WORK_LIST_STATUS_BIND
            obj_database.time_bind = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            obj_database.type_ = WORK_LIST_TYPE_PHISIC
            obj_database.status = WORK_LIST_STATUS_BUILD
            
        obj_database.worklist_name = obj.worklist_name
        obj_database.dict_data = obj.dict_data
            
        # 2 update server
        #obj_database.time_build = datetime.now()
        #obj_database.time_build = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # nwf 2014-06-27; for backward compatibility
        if (not hasattr(obj_database, "group")):
            obj_database.group = "USER"
            # for RF sys worklist
            if (obj_database.worklist_name == "Auto_GetTelecomAccountPassword"):
                obj_database.group = "SYS"
        # mysql
        id_ = insert_acs_worklist(obj_database, id_desc)
        obj_database.id_ = id_desc
        #obj_database.worklist_id = worklist_id
        log.app_info("[%s]id=%s, worklist_name=%s" %(id_, id_desc, obj.worklist_name))
        #CpeUserWorklist.m_dict_desc_id[id_desc] = id_
    
        ret = ERR_SUCCESS
        msg_rsp = msg + 1
                   
    return ret,msg_rsp,obj_database

       
def on_rx_worklist_bind_physic(msg, obj):    
    """
    obj = MsgWorklistBindPhysical
    1 query exist?
    2 exist, status right? 
    3 update sn + type
    """
    
    ret = ERR_FAIL  # default       
    msg_rsp = msg + 2 # default fail     
    obj_database = obj
    
    for nwf in [1]:
        # check args
        if (not isinstance(obj, MsgWorklistBindPhysical)):
            log.app_err("obj is not MsgWorklistBindPhysical")  
            ret = ERR_FATAL
            break                
        
        # 1 query exist?
        id_ = obj.id_
        #worklist_id = obj.id_
        #worklist_id = CpeUserWorklist.m_dict_desc_id[id_]
        """
        dict_col = dict(WORKLIST_DESC='', WORKLIST_NAME='', STATUS='')
        dict_data = {}
        
        dict_data['columns'] = dict_col
        dict_data['condition'] = 'WORKLIST_ID=%s' % worklist_id
        flag = operate_db('WORKLIST', 'SELECT', dict_data)
        if not flag:
        """
        obj_database = restore_acs_part_worklist(id_)
        if (obj_database is None):
            desc = "id(%s) is not exist." %(id_)
            log.app_err(desc) 

            obj_database = obj   
            obj_database.dict_ret["str_result"] = desc
            break
        """
        obj_database.worklist_name = dict_col['WORKLIST_NAME']
        obj_database.status = dict_col['STATUS']
        """
        log.app_info("id=%s, worklist_name=%s" %(id_, obj_database.worklist_name))
        worklist_id = obj_database.worklist_id

        # 2 status right?
        status_expect = [WORK_LIST_STATUS_BUILD, WORK_LIST_STATUS_BIND]
        if (obj_database.status not in status_expect):
            desc = "worklist status is %s, not in (%s)" %(obj_database.status, status_expect)
            log.app_err(desc) 

            obj_database.dict_ret["str_result"] = desc
            break
        
        # 3 update  
        obj_database.status = WORK_LIST_STATUS_BIND
        obj_database.sn = obj.sn  # be careful ,cpe(sn)'s domain delay to exec start
        obj_database.type_ = WORK_LIST_TYPE_PHISIC
        obj_database.time_bind = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # mysql
        """
        update_acs_worklist(obj_database, "STATUS", obj_database.status)
        update_acs_worklist(obj_database, "SN", obj_database.sn)
        update_acs_worklist(obj_database, "WORKLIST_TYPE", obj_database.type_)
        update_acs_worklist(obj_database, "TIME_BIND", obj_database.time_bind)
        """
        
        from cpe import CPE
        cpe = CPE.get_cpe(obj_database.sn)
        
        dict_col = {}
        dict_data = {}
        
        dict_col['STATUS'] = obj_database.status
        dict_col['CPE_ID'] = cpe.get_cpe_id()
        dict_col['SN'] = obj_database.sn
        dict_col['WORKLIST_TYPE'] = obj_database.type_
        dict_col['TIME_BIND'] = obj_database.time_bind
        
        if dict_col:
            # 字典的值不为空时，才更新数据库
            dict_data['columns'] = dict_col
            dict_data['condition'] = 'WORKLIST_ID=%s' % worklist_id
            operate_db('WORKLIST', 'UPDATE', dict_data)
        
    
        ret = ERR_SUCCESS
        msg_rsp = msg + 1
                   
    return ret,msg_rsp,obj_database

       
def on_rx_worklist_bind_logic(msg, obj):    
    """
    obj = MsgWorklistBindLogical
    1 query exist?
    2 exist, status right?
    3 update username+userid + type       
    """
    ret = ERR_FAIL  # default     
    msg_rsp = msg + 2 # default fail
    obj_database = obj      

    for nwf in [1]:
        # check args
        if (not isinstance(obj, MsgWorklistBindLogical)):
            log.app_err("obj is not MsgWorklistBindLogical")  
            
            ret = ERR_FATAL
            break                
        
        # 1 query exist?
        id_ = obj.id_
        #worklist_id = obj.id_
        #worklist_id = CpeUserWorklist.m_dict_desc_id[id_]
        obj_database = restore_acs_part_worklist(id_)
        if (obj_database is None):
            desc = "id(%s) is not exist." %(id_)
            log.app_err(desc) 

            obj_database = obj  
            obj_database.dict_ret["str_result"] = desc 
            break         
        log.app_info("id =%s, worklist_name=%s" %(id_, obj_database.worklist_name))
        worklist_id = obj_database.worklist_id

        # 2 status right?
        status_expect = [WORK_LIST_STATUS_BUILD, WORK_LIST_STATUS_BIND]
        if (obj_database.status not in status_expect):
            desc = "worklist status is %s, not in (%s)" %(obj_database.status, status_expect)
            log.app_err(desc) 

            obj_database.dict_ret["str_result"] = desc                             
            break

        # 3 update  
        obj_database.status = WORK_LIST_STATUS_BIND
        obj_database.username = obj.username
        obj_database.userid = obj.userid
        obj_database.type_ = WORK_LIST_TYPE_LOGIC 
        obj_database.time_bind = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # mysql
        """
        update_acs_worklist(obj_database, "STATUS", obj_database.status)
        update_acs_worklist(obj_database, "USER_NAME", obj_database.username)
        update_acs_worklist(obj_database, "USER_ID", obj_database.userid)
        update_acs_worklist(obj_database, "WORKLIST_TYPE", obj_database.type_)        
        update_acs_worklist(obj_database, "TIME_BIND", obj_database.time_bind)
        """
        
        dict_col = {}
        dict_data = {}
        
        dict_col['STATUS'] = obj_database.status
        dict_col['WORKLIST_TYPE'] = obj_database.type_
        dict_col['TIME_BIND'] = obj_database.time_bind
        
        if obj.username:    # 兼容BS和RF的逻辑工单绑定
            dict_col['USER_NAME'] = obj_database.username
            dict_col['USER_ID'] = obj_database.userid
        
        if dict_col:
            # 字典的值不为空时，才更新数据库
            dict_data['columns'] = dict_col
            dict_data['condition'] = 'WORKLIST_ID=%s' % worklist_id
            operate_db('WORKLIST', 'UPDATE', dict_data)
           
        ret = ERR_SUCCESS
        msg_rsp = msg + 1
                   
    return ret,msg_rsp,obj_database            
    
     
def on_rx_worklist_reserve(msg, obj):    
    """
    convert id to sn
    1 query exist?
    2 exist, get database obj     
    3 timer, wait exec start
    """
    ret = ERR_FAIL  # default   
    msg_rsp = msg + 2 # default fail
    obj_database = obj

    for nwf in [1]:
        # check args
        if (not isinstance(obj, MsgWorklistReserve)):
            log.app_err("obj is not MsgWorklistReserve")  
            
            ret = ERR_FATAL
            break                    
        
        # 1 query exist?
        id_ = obj.id_
        #worklist_id = obj.id_
        #worklist_id = CpeUserWorklist.m_dict_desc_id[id_]
        obj_database = restore_acs_part_worklist(id_)
        if (obj_database is None):
            desc = "id(%s) is not exist." %id_
            log.app_err(desc) 

            obj_database = obj # default
            obj_database.dict_ret["str_result"] = desc 
            break
        log.app_info("id=%s, worklist_name=%s, sn=%s" %(id_, obj_database.worklist_name, obj_database.sn))
        worklist_id = obj_database.worklist_id
        
        # 2 strategy: can reserve? (can try many times)
        status_expect = [WORK_LIST_STATUS_BIND]
        if (obj_database.status not in status_expect):
            msg_rsp = msg + 2 # fail
            desc = "worklist status is %s, not (%s)" %(obj_database.status, status_expect)
            log.app_err(desc)                   
            obj_database.dict_ret["str_result"] = desc    

            break
        
        # 3 update
        obj_database.status = WORK_LIST_STATUS_RESERVE
        obj_database.time_reserve = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # wait exec start
        timer = reactor.callLater(webservercfg.ACS_WORKLIST_RESERVE_WAIT_EXEC_START_TIMEOUT, 
                                    on_worklist_timeout, 
                                    EV_WORKLIST_EXEC_START_RQST,
                                    obj_database)     
        save_worklist_timer(obj_database.id_, timer)

        # mysql
        """
        update_acs_worklist(obj_database, "STATUS", obj_database.status)
        update_acs_worklist(obj_database, "TIME_RESERVE", obj_database.time_reserve)
        """
        dict_col = {}
        dict_data = {}
        
        dict_col['STATUS'] = obj_database.status
        dict_col['TIME_RESERVE'] = obj_database.time_reserve
        
        if dict_col:
            # 字典的值不为空时，才更新数据库
            dict_data['columns'] = dict_col
            dict_data['condition'] = 'WORKLIST_ID=%s' % worklist_id
            operate_db('WORKLIST', 'UPDATE', dict_data)
        
        msg_rsp = msg + 1 # response                          
        ret = ERR_SUCCESS
                               
    return ret,msg_rsp,obj_database                      

       
def on_rx_worklist_exec_start(msg, obj):    
    """
    logic & physic worklist share
    1 query exist?
    2 status right?
    3 exist, update exec time    
    4 timer, wait exec finish
    """
    from cpe import CPE
    
    ret = ERR_FAIL  # default
    cpe = None        
    msg_rsp = msg + 2 # default fail
    obj_database = obj
    
    for nwf in [1]:
        # check args
        if (not isinstance(obj, MsgWorklistExecStart)):
            desc = "obj is not MsgWorklistExecStart"
            log.app_err(desc)  
            
            ret = ERR_FATAL
            break                
        
        # 1 query exist?
        id_ = obj.id_
        #worklist_id = obj.id_
        #worklist_id = CpeUserWorklist.m_dict_desc_id[id_]
        obj_database = restore_acs_worklist(id_)
        if (obj_database is None):
            desc = "id(%s) is not exist." %id_
            log.app_err(desc) 

            obj_database = obj  
            obj_database.dict_ret["str_result"] = desc                   
            break
        log.app_info("id=%s, worklist_name=%s, sn=%s" %(id_, obj_database.worklist_name, obj_database.sn))
        worklist_id = obj_database.worklist_id

        # cancel pre status timer (msg is valid for worklist id can kill timer
        # , otherwise skip)
        try:
            timer = get_worklist_timer(obj_database.id_)
            if (timer):
                pop_worklist_timer(obj_database.id_)
                
                timer.cancel()
                
        except Exception,e:
            pass

        # this msg try only 1 time, if fail, then worklist fail
        
        # 2 status right?
        status_expect = [WORK_LIST_STATUS_RESERVE]
        if (obj_database.status not in status_expect):
            desc = "worklist status is %s, not in (%s)" %(obj_database.status, status_expect)
            log.app_err(desc) 
            
            obj_database.dict_ret["str_result"] = desc    
            set_worklist_status(obj_database, WORK_LIST_STATUS_FAIL, desc)  
            break            

        # be careful, cpe(sn)'s domain delay to here(exec start)
        sn = obj_database.sn 
        cpe = CPE.get_cpe(sn)
        if (cpe is None):
            desc = "cpe(sn=%s) is not online" %sn
            log.app_err(desc)
            
            obj_database.dict_ret["str_result"] = desc
            set_worklist_status(obj_database, WORK_LIST_STATUS_FAIL, desc)                
            break
        
        # 3 can update ?
        domain = cpe.cpe_property.get_cpe_domain()
        if (not domain):
            desc = "cpe(sn=%s) domain(type) is Not config" %sn
            log.app_err(desc)
            
            obj_database.dict_ret["str_result"] = desc    
            set_worklist_status(obj_database, WORK_LIST_STATUS_FAIL, desc)                
            break

        operator = cpe.cpe_property.get_cpe_operator()
        if (not operator):
            # delay to worklist server's judge, fail too
            operator = "standard"
            
            desc = "cpe(sn=%s) operator(type) is Not config, use default" %sn
            log.app_info(desc)
            
        version = cpe.cpe_property.get_cpe_interface_version()
            
        # 用户执行的工单需要对执行的参数和模板做匹配，系统工单暂时没有处理
        if obj_database.group and obj_database.group.lower() == "user":
            cpe_interface_version = cpe.cpe_property.get_cpe_interface_version()
            
            # 获取工单参数模板
            worklist_template_data = get_worklist_template(operator, cpe_interface_version, domain, obj_database.worklist_name)
            if worklist_template_data is None:  # 可能工单参数为空情况 by zsj 2014-6-17 
                desc = u"用户新增的%s %s %s %s工单，服务器不支持！" % (operator, cpe_interface_version, domain, obj_database.worklist_name)
                log.app_err(desc)
                
                obj_database.dict_ret["str_result"] = desc    
                set_worklist_status(obj_database, WORK_LIST_STATUS_FAIL, desc)                
                break
            
            # 用户参数和模板做匹配，重置工单参数
            obj_database.dict_data = _set_worklist_args(worklist_template_data, obj_database.dict_data)
            
            # 更新数工单参数到据库
            str_data = str(obj_database.dict_data)
            update_acs_worklist_ex_by_id(worklist_id, 'PARAMETERS', str_data)
        
        # 3 update     
        obj_database.operator = operator
        obj_database.cpe_interface_version = version
        obj_database.domain = domain            
        obj_database.status = WORK_LIST_STATUS_RUNNING            
        obj_database.time_exec_start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        obj_database.rollback = cpe.cpe_property.get_cpe_worklist_rollback() # default = False           
        

        # 4 wait exec finish
        timer = reactor.callLater(webservercfg.ACS_WAIT_WORKLIST_EXEC_FINISH_TIMEOUT, 
                                    on_worklist_timeout, 
                                    EV_WORKLIST_EXEC_FINISH_RQST,
                                    obj_database)
        save_worklist_timer(obj_database.id_, timer)            

        # mysql
        """
        update_acs_worklist(obj_database, "OPERATOR", obj_database.operator)
        update_acs_worklist(obj_database, "CPE_DEVICE_TYPE", obj_database.domain)
        update_acs_worklist(obj_database, "STATUS", obj_database.status)
        update_acs_worklist(obj_database, "TIME_EXEC_START", obj_database.time_exec_start)
        update_acs_worklist(obj_database, "ROLLBACK", obj_database.rollback)
        update_acs_worklist(obj_database, "SN", obj_database.sn)
        """
        
        dict_col = {}
        dict_data = {}
        
        dict_col['STATUS'] = obj_database.status
        dict_col['OPERATOR'] = obj_database.operator
        dict_col['OPERATOR_VERSION'] = obj_database.cpe_interface_version
        dict_col['DOMAIN'] = obj_database.domain
        dict_col['TIME_EXEC_START'] = obj_database.time_exec_start
        dict_col['ROLLBACK'] = str(obj_database.rollback)
        
        if dict_col:
            # 字典的值不为空时，才更新数据库
            dict_data['columns'] = dict_col
            dict_data['condition'] = 'WORKLIST_ID=%s' % worklist_id
            operate_db('WORKLIST', 'UPDATE', dict_data)
        
        ret = ERR_SUCCESS
        msg_rsp = msg + 1 # response

    return ret,msg_rsp,obj_database             

      
def on_rx_worklist_exec_finish(msg, obj):    
    """
    logic & physic worklist share
    1 query exist?
    2 exist, get database obj         
    """
    ret = ERR_FAIL  # default     
    msg_rsp = msg + 2 # default fail
    obj_database = obj
    
    for nwf in [1]:
        # check args
        if (not isinstance(obj, MsgWorklistExecFinish)):
            log.app_err("obj is not MsgWorklistExecFinish")  
            
            ret = ERR_FATAL
            break                
        
        # 1 query exist?
        id_ = obj.id_
        #worklist_id = id_
        #worklist_id = CpeUserWorklist.m_dict_desc_id[id_]
        obj_database = restore_acs_part_worklist(id_)
        if (obj_database is None):
            desc = "id(%s) is not exist." % id_
            log.app_err(desc) 

            obj_database = obj 
            obj_database.dict_ret["str_result"] = desc                    
            break
        log.app_info("id=%s, worklist_name=%s, sn=%s" %(id_, obj_database.worklist_name, obj_database.sn))
        worklist_id = obj_database.worklist_id

        # MySQL need extend data
        obj_database.dict_ret = obj.dict_ret
        # extend data
        node_add_object = obj_database.dict_ret.get("node_add_object", None)
        if (node_add_object):
            save_worklist_node_add_object(obj_database.id_, node_add_object)        

        # cancel pre status timer (msg is valid for worklist id can kill timer
        # , otherwise skip)
        try:
            timer = get_worklist_timer(obj_database.id_)
            if (timer):
                pop_worklist_timer(obj_database.id_)
                
                timer.cancel()
        except Exception,e:
            pass  
            
        # 2 status right?
        status_expect = [WORK_LIST_STATUS_RUNNING]
        if (obj_database.status not in status_expect):
            desc = "worklist status is %s, not (%s)" %(obj_database.status, status_expect)
            log.app_err(desc) 
            
            obj_database.dict_ret["str_result"] = desc 
            set_worklist_status(obj_database, WORK_LIST_STATUS_FAIL, desc)                
            break 

        # 3 update    
        obj_database.time_exec_end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')   
        
        execute_status = obj.execute_status       
        if (execute_status == EV_WORKLIST_EXECUTE_RSP):                       
            set_worklist_status(obj_database, WORK_LIST_STATUS_SUCCESS)   
        else:            
            set_worklist_status(obj_database, WORK_LIST_STATUS_FAIL)                                                                  

        # MySQL
        #update_acs_worklist(obj_database, "STATUS", obj_database.status)
        update_acs_worklist_by_id(worklist_id, "TIME_EXEC_FINISH", obj_database.time_exec_end)

        insert_ex_acs_worklist_log(worklist_id, obj_database)
        
        ret = ERR_SUCCESS
        msg_rsp = msg + 1 # response                
                   
    return ret,msg_rsp,obj_database   
    
     
def on_rx_worklist_query(msg, obj):    
    """
    logic & physic worklist share
    1 query exist?
    2 exist, get database obj    
    # nwf 2013-06-01; user query high frequency
    """
    ret = ERR_FAIL  # default     
    msg_rsp = msg + 2 # default fail

    for nwf in [1]:
        # check args
        if (not isinstance(obj, MsgWorklistQuery)):
            log.app_err("obj is not MsgWorklistQuery")  
            
            ret = ERR_FATAL
            break                
        
        # 1 query exist?
        id_ = obj.id_
        #worklist_id = id_
        #worklist_id = CpeUserWorklist.m_dict_desc_id.get(id_, "")
        """if (not worklist_id):
            desc = "worklist id=%s is not exist." %id_
            obj_database = obj  
            obj_database.dict_ret["str_result"] = desc             
            break
        """
        obj_database = restore_acs_worklist(id_)
        if (obj_database is None):
            desc = "id(%s) is not exist." %id_
            log.app_err(desc) 

            obj_database = obj  
            obj_database.dict_ret["str_result"] = desc                    
            break          
                                                        
        ret = ERR_SUCCESS
        msg_rsp = msg + 1 # response
                   
    return ret,msg_rsp,obj_database       


def set_worklist_status(obj_database, status, desc=""):
    """
    monitor
    """        
    worklist_id = obj_database.worklist_id
    obj_database.status = status
    #update_acs_worklist(obj_database, "STATUS", obj_database.status)
    update_acs_worklist_by_id(worklist_id, "STATUS", obj_database.status)

    if (desc):
        insert_ex_acs_worklist_log(worklist_id, obj_database)        

    if ((status == WORK_LIST_STATUS_SUCCESS) or 
        (status == WORK_LIST_STATUS_FAIL)):

        try:                
            event = get_worklist_event(obj_database.id_)
            if (event):
                log.app_info("worklist(id=%s) exec finish." %obj_database.id_)

                event.set()
                
        except Exception,e:
            print_trace(e)  


def on_worklist_timeout(msg, obj_database):
    """
    msg is wait, but timeout
    """
    ret = None    
           
    desc = "wait %s timeout(sn=%s)" %(get_event_desc(msg), obj_database.sn)
    log.app_info(desc)

    # cancel pre status timer 
    try:
        timer = get_worklist_timer(obj_database.id_)
        if (timer):
            pop_worklist_timer(obj_database.id_)
            
            timer.cancel()
    except Exception,e:
        pass        
    
    # exec fail
    set_worklist_status(obj_database, WORK_LIST_STATUS_FAIL, desc)
        
    return ret 
       

# -------------------------------------- assist
def save_worklist_timer(id_, timer):
    """
    """
    CpeUserWorklist.m_dict_id2timer[id_] = timer

def get_worklist_timer(id_):
    """
    """
    return CpeUserWorklist.m_dict_id2timer.get(id_, None)

def pop_worklist_timer(id_):
    """
    """
    CpeUserWorklist.m_dict_id2timer.pop(id_)


def save_worklist_event(id_, event):
    """
    """
    CpeUserWorklist.m_dict_id2event[id_] = event

def get_worklist_event(id_):
    """
    """
    return CpeUserWorklist.m_dict_id2event.get(id_, None)

def pop_worklist_event(id_):
    """
    """
    CpeUserWorklist.m_dict_id2event.pop(id_, None)


def save_worklist_node_add_object(id_, node_add_object):
    CpeUserWorklist.m_dict_id2node_add_object[id_] = node_add_object
    
def get_worklist_node_add_object(id_):
    return CpeUserWorklist.m_dict_id2node_add_object.get(id_, None)

def pop_worklist_node_add_object(id_):
    CpeUserWorklist.m_dict_id2node_add_object.pop(id_, None)
    
def _set_worklist_args(worklist_default_args, dict_data):
    """
    函数功能：对用户上传的工单参数和数据库中工单模板参数做匹配补齐，更新工单参数
    参数：
        worklist_default_args： 数据库中读取的dict型工单模板数据{args_name:(args,index)}
        dict_data： 用户上传工单参数{args_name_or_index:(args,index)}
    返回值：
        ret_dict_data：格式和模板相同的工单数据{args_name:(args,index)}
    """
    list_change_keys = []
    ret_dict_data = {}
    
    # 如果rf没有传入参数将用模板默认参数
    if not dict_data:
        return worklist_default_args
 
    # 对字典中的元组值做转换为list，以便修改值
    for key,value in worklist_default_args.items():
        ret_dict_data.update({key:list(value)})
    
    list_default_keys = worklist_default_args.keys()
    # 处理用户输入的key=value格式的参数
    for key,value in dict_data.items():
        if key in list_default_keys:  # 当用户输入的key为正常的情况下，改变母版中的参数值
            ret_dict_data[key][0] = value[0]
                
            list_change_keys     += (key,ret_dict_data[key][1]) # 记录已经修改过的key和索引
            dict_data.pop(key)
        elif re.match(r"^[1-9]\d*$", key): # 当用户输入为单个值时，把key为str变为int方便排序
            pass
        else: # 当用户输入的key母版中不识别时把"key=value"当为整体value，已索引为key
            new_value = ("%s=%s" % (key, value[0]), value[1])
            new_key = value[1]
            dict_data.update({new_key:new_value})
            
            dict_data.pop(key)
            
    temp_dict = {}
    for key, tuple_value in worklist_default_args.items():
        temp_dict.update({tuple_value[1]:(tuple_value[0], key)})
    
    list_default_keys = temp_dict.keys()
    for key, value in dict_data.items():
        if (key not in list_change_keys) and (key in list_default_keys):
            new_key = temp_dict[key][1]
            if new_key not in list_change_keys and value[0]:
                ret_dict_data.update({new_key:list(value)})
                list_change_keys.append(key)
     
     
    # 对参数中的null及false、true做兼容处理    zsj 2014-6-27
    for key, value in ret_dict_data.items():
        
        temp_data = value[0]
        
        if isinstance(temp_data, str) or\
           isinstance(temp_data, unicode):
            
            args_data = temp_data.lower()
            
            if args_data == "null":
                args_data = ""
            elif args_data == "true":
                args_data = True
            elif args_data == "false":
                args_data = False
            else:
                args_data = temp_data
                
            ret_dict_data[key][0] = args_data
            
    return ret_dict_data


# global 
__all__ = [ "on_rx_worklist_build", 
            "on_rx_worklist_bind_physic",
            "on_rx_worklist_bind_logic",
            "CpeUserWorklist",

            "save_worklist_timer", 
            "get_worklist_timer",
            "pop_worklist_timer",
            
            "save_worklist_event",
            "get_worklist_event",
            "pop_worklist_event",

            "save_worklist_node_add_object",
            "get_worklist_node_add_object",
            "pop_worklist_node_add_object",
          ]


if __name__ == '__main__':
    pass
 
