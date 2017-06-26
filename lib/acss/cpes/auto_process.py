#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: auto_process
#  function: 处理某些需要自动处理流程的eventcode。
#            例如"0 BOOTSTRAP"， "X CT-COM BIND"， "X CT-COM ACCOUNTCHANGE"等
#  Author: ATT development group
#  version: V2.0
#  date: 2013.02.26
#  change log:
#  nwf      2013-02-26   created
#  lana     2013-12-09   在"0 BOOTSTRAP"和 "X CT-COM BIND"的处理流程中，添加对电信维护账号的修改和双向DIGEST的账号用户名的修改；
#                        提炼公共函数reset_digest_account_and_telecom_account_ct
#  lana     2013-12-10   分拆电信和联调的bootstrap，添加公共函数 reset_telecom_account_cu
#  lana     2013-12-11   替换reset_telecom_account_cu为reset_digest_account_and_telecom_account_cu
# ***************************************************************************


# sys lib
import  sys
import  os
import  random
from    operator                    import  attrgetter

from    TR069.lib.common.error      import  *
from    TR069.lib.common.event      import  *
import  TR069.lib.common.logs.log   as      log 
from    TR069.lib.common.function   import  print_trace
import  TR069.lib.acss.acs.webservercfg     as      webservercfg
from    eventcode                   import  EventCode
from    cpe_db                      import  *
from    cpe_operator                import  CpeOperator


def bootstrap_ct(cpe):
    """
    in thread
    """
    
    ret         = ERR_FAIL
    err_message = ""        

    sn = cpe.get_sn()
    
    for nwf in [1]:

        # nwf 2014-06-16; user config
        #update_interface_version(cpe)
        
        # 重置双向的DIGEST认证账号和电信维护账号密码  --added by lana 20131209
        ret = reset_digest_account_and_telecom_account_ct(cpe)
        if ret != ERR_SUCCESS:
            break 
        
        # physic worklist --------------- 
        obj = MsgWorklistBuild("Auto_GetRPCMethods", {})  
        obj_database = EventCode.auto_build_bind_physic_worklist(cpe, obj)       
        try:
            ret, err_message = EventCode.tx_worklist_exec(obj_database)        
            ret = EventCode.rx_worklist_exec(ret, err_message)      
            if (ret == ERR_SUCCESS):

                ret, err_message = EventCode.wait_worklist_exec_finish(obj_database)
                if ret == ERR_SUCCESS:                
                    desc = "worklist(Auto_GetRPCMethods) execute success."
                    log.app_info(desc)
                else:
                    log.app_err(err_message)
                    
                    break
            else:
                desc = "worklist(Auto_GetRPCMethods) execute fail."
                log.app_err(desc) 
                
                break
        except Exception,e:
            print_trace(e) 	
            break     

        ret = ERR_SUCCESS

    return ret        


def bootstrap_cu(cpe):
    """
    in thread
    """
    
    ret         = ERR_FAIL
    err_message = ""        

    sn = cpe.get_sn()
    
    for nwf in [1]:
        # 获取上网账号和密码
        # 组建工单参数
        dict_data = {}
        # 组建工单消息，下发工单执行命令
        obj = MsgWorklistBuild("Auto_GetPPPConnectionAccount", dict_data)                 
        obj_database = EventCode.auto_build_bind_physic_worklist(cpe, obj)        
        try:
            ret, err_message = EventCode.tx_worklist_exec(obj_database)        
            ret = EventCode.rx_worklist_exec(ret, err_message)      
            if (ret == ERR_SUCCESS):
            
                ret, err_message = EventCode.wait_worklist_exec_finish(obj_database)
                if ret == ERR_SUCCESS:
                    desc = "worklist(Auto_GetPPPConnectionAccount) execute success."
                    log.app_info(desc)
                else:
                    log.app_err(err_message)
                    # 忽略查询结果
                    # break
            else:
                desc = "worklist(Auto_GetPPPConnectionAccount) execute fail."
                log.app_err(desc)
                
                break
        except Exception,e:
            print_trace(e) 	
            break
        
        # physic worklist --------------- 
        obj = MsgWorklistBuild("Auto_GetRPCMethods", {})  
        obj_database = EventCode.auto_build_bind_physic_worklist(cpe, obj)       
        try:
            ret, err_message = EventCode.tx_worklist_exec(obj_database)        
            ret = EventCode.rx_worklist_exec(ret, err_message)      
            if (ret == ERR_SUCCESS):

                ret, err_message = EventCode.wait_worklist_exec_finish(obj_database)
                if ret == ERR_SUCCESS:                
                    desc = "worklist(Auto_GetRPCMethods) execute success."
                    log.app_info(desc)
                else:
                    log.app_err(err_message)
                    
                    break
            else:
                desc = "worklist(Auto_GetRPCMethods) execute fail."
                log.app_err(desc) 
                
                break
        except Exception,e:
            print_trace(e) 	
            break     

        ret = ERR_SUCCESS

    return ret


def get_random_8str(old):

    new_str = ""
    
    # nwf 2013-07-09;  password =old + xxxxxxxx[8]
    str8 = str(random.randrange(10000000,99999999))
    
    old8 = old[-8:]
    if (old8.isdigit() and (len(old8) == 8)):
        old8_pre = old[:-8]            

        # nwf 2013-07-26; random is the same as old?
        for nwf in range(3):
            if (old8 == str8):
                str8 = str(random.randrange(10000000,99999999))
            else:
                break        
        new_str = old8_pre + str8   # replace
    else:           
        new_str = old + str8        # concat
        
    return new_str


def bind_get_status_worklists(cpe, user_name=None, user_id=None):
    """
    in thread
    """
    
    ret                         = ERR_FAIL
    err_message                 = ""    
    logic_worklists             = []
    logic_worklists_name_id_ok  = []
    logic_worklists_bind        = []
    bl_name_match               = False
    bl_id_match                 = False
    status_value                = -1     # 
   
    sn = cpe.get_sn() 
    
    logic_worklists = restore_acs_logic_worklists()

    # nwf 2014-07-23; user_id =="" or user_id==None(tr069 node is missing)
    if (user_name is None):
        user_name = ""
    if (user_id is None):
        user_id = ""
    
    for nwf in [1]:
    
        # step 1.1; search UserName or UserId
        for obj in logic_worklists:
            
            if (obj.username == user_name ): 
                bl_name_match = True
            if (obj.userid == user_id ):
                bl_id_match = True
                
            if ((obj.username == user_name) and (obj.userid == user_id)):
                logic_worklists_name_id_ok.append(obj)                
            
        # InternetGatewayDevice.X_CT-COM_UserInfo.Status = 0
        if (logic_worklists_name_id_ok):
            status_value = 0  # match success
            
            # step 2; search  there are have worklist be binded
            for logic_worklist in logic_worklists_name_id_ok:        
                
                if ((logic_worklist.status == WORK_LIST_STATUS_BIND) and 
                    (not logic_worklist.sn)):
                    
                    logic_worklists_bind.append(logic_worklist)

            if (not logic_worklists_bind):
                status_value = 5
            
                desc = "inform UserName(%s) and UserId(%s) match Success, but no worklist is binded." %(user_name, user_id)
                log.app_info(desc)            
        else:
            # first line:   user name(logic id);   
            # second line:  user id(real id, authenticate id); nwf 2013-07-08
            if (bl_name_match and (not bl_id_match)):
                status_value = 1    # (auth id not exist)
                
            if ((not bl_name_match) and bl_id_match):
                status_value = 2    # (logic id not exist)
                
            if ((not bl_id_match) and (not bl_name_match)):
                status_value = 3    # 
                
    return status_value, logic_worklists_bind


def bind_set_status(cpe, status_value, node_name):
    """
    in thread
    """
    
    ret                         = ERR_FAIL
    err_message                 = ""    


    for nwf in [1]:    

        # rpc1, path_name = "InternetGatewayDevice.X_CT-COM_UserInfo.Status"
        dict_data = {"ParameterList": [
                                    dict(Name   =node_name, 
                                         Value  =status_value)]}
        obj = MsgWorklistBuild("Auto_SetParameterValue", dict_data) 
        obj_database = EventCode.auto_build_bind_physic_worklist(cpe, obj)        
        try:        
            ret, err_message = EventCode.tx_worklist_exec(obj_database)        
            ret = EventCode.rx_worklist_exec(ret, err_message)        
            if (ret == ERR_SUCCESS):
            
                ret, err_message = EventCode.wait_worklist_exec_finish(obj_database)
                if (ret != ERR_SUCCESS):          
                    log.app_err(err_message)
                    
                    break                
            else:
                log.app_err(err_message)
                
                break
        except Exception,e:
            print_trace(e)
            break
    
    return ret


def bind_set_result(cpe, status_result, node_name):
    """
    in thread
    """
    
    ret                         = ERR_FAIL
    err_message                 = ""    


    for nwf in [1]:    

        #rpc 3; path_name = "InternetGatewayDevice.X_CT-COM_UserInfo.Result"
        dict_data = {"ParameterList": [
                                    dict(Name   =node_name, 
                                         Value  =status_result)]}
        obj = MsgWorklistBuild("Auto_SetParameterValue", dict_data) 
        obj_database = EventCode.auto_build_bind_physic_worklist(cpe, obj)        
        try:        
            ret, err_message = EventCode.tx_worklist_exec(obj_database)        
            ret = EventCode.rx_worklist_exec(ret, err_message)        
            if (ret == ERR_SUCCESS):
            
                ret, err_message = EventCode.wait_worklist_exec_finish(obj_database)
                if (ret != ERR_SUCCESS):   
                    log.app_err(err_message)
                    
                    break  
            else:
                log.app_err(err_message)
                
                break
        except Exception,e:
            print_trace(e) 	
            break
    
    return ret


def bind_do_worklists(logic_worklists):
    """
    """
    
    ret                         = ERR_FAIL
    err_message                 = ""    
    bool_logic_worklist         = True  # default success
    status_result               = 1     

    # logic worklist ---------------
    for obj_database in logic_worklists:
    
        try:
            
            desc = "begin to exec worklist---name:%s  time_bind:%s" % (obj_database.worklist_name, obj_database.time_bind)
            log.app_info(desc)
            
            ret, err_message = EventCode.tx_worklist_exec(obj_database)
            ret = EventCode.rx_worklist_exec(ret, err_message)        
            if (ret == ERR_SUCCESS):
                ret, err_message = EventCode.wait_worklist_exec_finish(obj_database)
                if (ret != ERR_SUCCESS):
                    log.app_err(err_message)
                    bool_logic_worklist = False
            else:
                log.app_err(err_message)
                bool_logic_worklist = False
                # continue, not break
                
        except Exception,e:
            print_trace(e) 	                
            bool_logic_worklist = False

    # 
    if (bool_logic_worklist):
        status_result = 1   # success
        desc = "logic worklist exec success."
    else:
        status_result = 2   # fail
        desc = "logic worklist exec fail."
    log.app_info(desc)

    return status_result


def bind_ct(cpe, user_name=None, user_id=None):
    """
    in thread
    """
    
    ret                         = ERR_FAIL
    err_message                 = ""    
    logic_worklists             = []
    status_value                = 0     # default success
    status_result               = 0     # default success

    # nwf 2013-06-28  --------------------------------------------------
    no_rpc_name     = webservercfg.LOGIC_WORKLIST_NO_RPC_NAME
    no_rpc_id       = webservercfg.LOGIC_WORKLIST_NO_RPC_ID

    if (user_name and user_id):
        if ((no_rpc_name.upper() == user_name.upper()) and 
            (no_rpc_id.upper() == user_id.upper())):
            return bind_no_rpc_ct(cpe, user_name, user_id)

    # ----------------------------------------------------------        
    sn = cpe.get_sn() 
    
    for nwf in [1]:
    
        status_value, logic_worklists= bind_get_status_worklists(cpe, user_name, user_id)
        desc = "step1: InternetGatewayDevice.X_CT-COM_UserInfo.Status = %s" %(status_value)
        log.app_info(desc)  

        node_name = "InternetGatewayDevice.X_CT-COM_UserInfo.Status"
        ret = bind_set_status(cpe, status_value, node_name)
        if (ret != ERR_SUCCESS):
            break            

        # continue?
        if (status_value != 0):
            desc = "step1: InternetGatewayDevice.X_CT-COM_UserInfo.Status = %s(!=0, stopped)" %(status_value)        
            log.app_err(desc)
            break

        # CT V4.0, modulation_type match?
        interface_version = cpe.cpe_property.get_cpe_interface_version()
        if ("v4" == interface_version.lower()):
            ret = is_modulation_type_match(cpe)
            if (ret != ERR_SUCCESS):
                break 
                    
        # 重置双向的DIGEST认证账号和电信维护账号密码  --added by lana 20131209
        ret = reset_digest_account_and_telecom_account_ct(cpe)
        if ret != ERR_SUCCESS:
            break     
    
        # change the sn to hold            
        for obj in logic_worklists:
            obj.sn = sn  
            
            # mysql
            update_acs_worklist(obj, "SN", obj.sn)
            update_acs_worklist(obj, "CPE_ID", cpe.get_cpe_id())
        
        # sort logic_worklists by time_bind
        logic_worklists = sorted(logic_worklists, key=attrgetter('time_bind'))

        node_name = "InternetGatewayDevice.X_CT-COM_UserInfo.Result"
        ret = bind_set_result(cpe, "0", node_name) 
        if (ret != ERR_SUCCESS):
            break

        status_result = bind_do_worklists(logic_worklists)

        ret = bind_set_result(cpe, status_result, node_name)        

    return ret


def bind_cu(cpe, user_name=None, user_id=None):
    """
    in thread
    """
    
    ret                         = ERR_FAIL
    err_message                 = ""    
    logic_worklists             = []
    status_value                = 0     # default success
    status_result               = 0     # default success

    # nwf 2013-06-28  --------------------------------------------------
    no_rpc_name     = webservercfg.LOGIC_WORKLIST_NO_RPC_NAME
    no_rpc_id       = webservercfg.LOGIC_WORKLIST_NO_RPC_ID
    
    if ((no_rpc_name.upper() == user_name.upper()) and 
        (no_rpc_id.upper() == user_id.upper())):
        return bind_no_rpc_cu(cpe, user_name, user_id)

    # ----------------------------------------------------------        
    sn = cpe.get_sn() 
    
    for nwf in [1]:
    
        status_value, logic_worklists= bind_get_status_worklists(cpe, user_name, user_id)
        desc = "step1: InternetGatewayDevice.X_CU_UserInfo.Status = %s" %(status_value)
        log.app_info(desc)  
        
        node_name = "InternetGatewayDevice.X_CU_UserInfo.Status"
        ret = bind_set_status(cpe, status_value, node_name)
        if (ret != ERR_SUCCESS):
            break            

        # continue?
        if (status_value != 0):
            desc = "step1: InternetGatewayDevice.X_CU_UserInfo.Status = %s(!=0, stopped)" %(status_value)        
            log.app_err(desc)
            break
        
        # 重置双向DIGEST认证账号终端维护账号密码  --added by lana 20131209
        ret = reset_digest_account_and_telecom_account_cu(cpe)
        if ret != ERR_SUCCESS:
            break    
        
        # change the sn to hold            
        for obj in logic_worklists:
            obj.sn = sn  
            
            # mysql
            update_acs_worklist(obj, "SN", obj.sn)
            update_acs_worklist(obj, "CPE_ID", cpe.get_cpe_id())
        
        # sort logic_worklists by time_bind
        logic_worklists = sorted(logic_worklists, key=attrgetter('time_bind'))

        node_name = "InternetGatewayDevice.X_CU_UserInfo.Result"
        ret = bind_set_result(cpe, "0", node_name) 
        if (ret != ERR_SUCCESS):
            break

        status_result = bind_do_worklists(logic_worklists)

        ret = bind_set_result(cpe, status_result, node_name)        

    return ret    
    

def bind_no_rpc_ct(cpe, user_name, user_id):
    """
    in thread
    """
    
    ret                         = ERR_FAIL 

    # nwf 2013-06-28
    desc = "system defined username(%s), userid(%s)" %(user_name, user_id)
    log.app_info(desc)
    
    for nwf in [1]:

        node_name = "InternetGatewayDevice.X_CT-COM_UserInfo.Status"
        ret = bind_set_status(cpe, 0, node_name)  # 0=success
        if (ret != ERR_SUCCESS):
            break 
        
        node_name = "InternetGatewayDevice.X_CT-COM_UserInfo.Result"
        ret = bind_set_result(cpe, 0, node_name)  # start
        if (ret != ERR_SUCCESS):
            break  

        # nwf 2013-07-01
        ret = bind_set_result(cpe, 1, node_name)   # finish

    return ret


def bind_no_rpc_cu(cpe, user_name, user_id):
    """
    in thread
    """
    
    ret                         = ERR_FAIL 

    # nwf 2013-06-28
    desc = "system defined username(%s), userid(%s)" %(user_name, user_id)
    log.app_info(desc)
    
    for nwf in [1]:

        node_name = "InternetGatewayDevice.X_CU_UserInfo.Status"
        ret = bind_set_status(cpe, 0, node_name)  # 0=success
        if (ret != ERR_SUCCESS):
            break 

        node_name = "InternetGatewayDevice.X_CU_UserInfo.Result"
        ret = bind_set_result(cpe, 0, node_name)  # start
        if (ret != ERR_SUCCESS):
            break  

        # nwf 2013-07-01
        ret = bind_set_result(cpe, 1, node_name)   # finish

    return ret
    
    
def accountchange_ct(cpe):
    """
    """
    
    ret         = ERR_FAIL
    err_message = ""        

    sn = cpe.get_sn()
    
    for nwf in [1]:
              
        # physic worklist ---------------
        password = random.randrange(10000000,99999999)
        password = "telecomadmin" + str(password)
        
        dict_data = {"ParameterList": [
                        dict(Name="InternetGatewayDevice.DeviceInfo.X_CT-COM_TeleComAccount.Enable", 
                             Value="1"), 
                        dict(Name="InternetGatewayDevice.DeviceInfo.X_CT-COM_TeleComAccount.Password", 
                             Value=password)]}
        obj = MsgWorklistBuild("Auto_SetParameterValue", dict_data)                 
        obj_database = EventCode.auto_build_bind_physic_worklist(cpe, obj)        
        try:
            ret, err_message = EventCode.tx_worklist_exec(obj_database)        
            ret = EventCode.rx_worklist_exec(ret, err_message)      
            if (ret == ERR_SUCCESS):
            
                ret, err_message = EventCode.wait_worklist_exec_finish(obj_database)
                if ret == ERR_SUCCESS:             
                    log.app_info("update InternetGatewayDevice.DeviceInfo.X_CT-COM_TeleComAccount.Password success: %s" % password) 
                else:
                    log.app_err(err_message)
                    
                    break
            else:
                log.app_err(err_message)
                
                break
        except Exception,e:
            print_trace(e) 	
            break

        ret = ERR_SUCCESS   

    return ret


def accountchange_cu(cpe):
    """
    """
    
    ret         = ERR_FAIL
    err_message = ""        

    sn = cpe.get_sn()
    
    for nwf in [1]:
              
        # physic worklist ---------------
        password = random.randrange(10000000,99999999)
        password = "cuadmin" + str(password)
        
        dict_data = {"ParameterList": [dict(Name="InternetGatewayDevice.X_CU_Function.Web.AdminPassword", 
                             Value=password)]}
        obj = MsgWorklistBuild("Auto_SetParameterValue", dict_data)                 
        obj_database = EventCode.auto_build_bind_physic_worklist(cpe, obj)        
        try:
            ret, err_message = EventCode.tx_worklist_exec(obj_database)        
            ret = EventCode.rx_worklist_exec(ret, err_message)      
            if (ret == ERR_SUCCESS):
            
                ret, err_message = EventCode.wait_worklist_exec_finish(obj_database)
                if ret == ERR_SUCCESS:             
                    log.app_info("update InternetGatewayDevice.X_CU_Function.Web.AdminPassword success: %s" % password) 
                else:
                    log.app_err(err_message)
                    
                    break
            else:
                log.app_err(err_message)
                
                break
        except Exception,e:
            print_trace(e) 	
            break

        ret = ERR_SUCCESS   

    return ret    


def dsl_mode_change_ct(cpe):
    """
    in thread
    """
    
    ret                     = ERR_FAIL
    cpe_device_type_new     = ""

    for nwf in [1]:

        try:
            # ADSL_2LAN  ADSL_4+1 ADSL_4LAN
            # VDSL_4+1 VDSL_4+2 VDSL_4LAN
            cpe_device_type_old = cpe.cpe_property.get_cpe_domain()
            type_ = cpe_device_type_old[:4]
            if (type_ == "ADSL"):
                cpe_device_type_new = "VDSL" + cpe_device_type_old[4:]
            elif(type_ == "VDSL"):
                cpe_device_type_new = "ADSL" + cpe_device_type_old[4:]

            # update
            cpe.cpe_property.set_cpe_domain(cpe_device_type_new)
            
        except Exception,e:
            print_trace(e) 	
            break  
            
        ret = ERR_SUCCESS    
    
    return ret    


def process_operator_eventcodes(eventcodes, cpe):
    """
    in thread
    """    
    ret             = ERR_FAIL
    user_name       = None
    user_id         = None
    
    try:

        # nwf 2013-05-21; copy soap inform, maybe overwrite(0-boot + x_ct_com_bind in one inform)
        # step1:backup data
        cpe_operator = cpe.cpe_property.get_cpe_operator()                
        soap_inform = cpe.cpe_soap.get_soap_inform()        
        ParameterList = soap_inform.result.ParameterList
        for para in ParameterList:

            # ct
            if (para.Name == "InternetGatewayDevice.X_CT-COM_UserInfo.UserName"):
                user_name = para.Value
                
            if (para.Name == "InternetGatewayDevice.X_CT-COM_UserInfo.UserId"):
                user_id = para.Value

            # cu
            if (para.Name == "InternetGatewayDevice.X_CU_UserInfo.UserName"):
                user_name = para.Value
                
            if (para.Name == "InternetGatewayDevice.X_CU_UserInfo.UserId"):
                user_id = para.Value 
                

        # sys operator eventcode first, then user
        for eventcode in eventcodes:

            log.app_info("cpe(sn=%s), eventcode=%s" %(cpe.get_sn(), eventcode))
        
            if (eventcode in [ "X CT-COM BIND", "X CT-COM DSLMODECHANGE", "X CU BIND"]):
                if ("X CT-COM BIND" in eventcode):
                    ret = bind_ct(cpe, user_name, user_id)
                elif ("X CT-COM DSLMODECHANGE" in eventcode):
                    ret = dsl_mode_change_ct(cpe)
                elif ("X CU BIND" in eventcode):
                    ret = bind_cu(cpe, user_name, user_id)                
                
            else:
                ret = process_user_operator_eventcode(eventcode, cpe)            
                
    except Exception,e:
        print_trace(e) 	
                
    return ret


def process_user_operator_eventcode(eventcode, cpe):
    """
    """
    ret         = ERR_FAIL
    err_message = ""

    try:
    
        cpe_operator = cpe.cpe_property.get_cpe_operator()
        interface_version = cpe.cpe_property.get_cpe_interface_version()
        interface_version = interface_version.lower()
        eventcode_map = CpeOperator.get_operator_eventcode_map(cpe_operator, interface_version)
        dict_worklist = eval(eventcode_map)
        
        worklist = dict_worklist.get(eventcode)
        if (worklist):  
            ret = auto_exec_worklist(worklist, cpe)
            
    except Exception,e:
        print_trace(e)

    return ret


def process_ct_eventcodes(eventcodes, cpe):
    """
    in thread
    """
    
    ret         = ERR_FAIL
    user_name   = None
    user_id     = None

    try:

        # nwf 2013-05-21; copy soap inform, maybe overwrite(0-boot + x_ct_com_bind in one inform)
        # step1:backup data
        cpe_operator = cpe.cpe_property.get_cpe_operator()                
        soap_inform = cpe.cpe_soap.get_soap_inform()        
        ParameterList = soap_inform.result.ParameterList
        for para in ParameterList:
        
            if (para.Name == "InternetGatewayDevice.X_CT-COM_UserInfo.UserName"):
                user_name = para.Value
                
            if (para.Name == "InternetGatewayDevice.X_CT-COM_UserInfo.UserId"):
                user_id = para.Value               
            
        # step2:do eventcodes in one inform
        for eventcode in eventcodes:

            log.app_info("cpe(sn=%s), eventcode=%s" %(cpe.get_sn(), eventcode))

            # nwf 2013-05-21; skip eventcode fail
            if ("0 BOOTSTRAP" in eventcode):                
                ret = bootstrap_ct(cpe)
                
            elif ("X CT-COM BIND" in eventcode):
                ret = bind_ct(cpe, user_name, user_id)
                
            elif ("X CT-COM ACCOUNTCHANGE" in eventcode):
                ret = accountchange_ct(cpe)   

            elif ("X CT-COM DSLMODECHANGE" in eventcode):
                ret = dsl_mode_change_ct(cpe)                 
                
    except Exception,e:
        print_trace(e) 	
                
    return ret


def process_cu_eventcodes(eventcodes, cpe):
    """
    in thread
    """
    
    ret         = ERR_FAIL
    user_name   = None
    user_id     = None

    try:

        # nwf 2013-05-21; copy soap inform, maybe overwrite(0-boot + x_ct_com_bind in one inform)
        # step1:backup data
        cpe_operator = cpe.cpe_property.get_cpe_operator()                
        soap_inform = cpe.cpe_soap.get_soap_inform()        
        ParameterList = soap_inform.result.ParameterList
        for para in ParameterList:

            if (para.Name == "InternetGatewayDevice.X_CU_UserInfo.UserName"):
                user_name = para.Value
                
            if (para.Name == "InternetGatewayDevice.X_CU_UserInfo.UserId"):
                user_id = para.Value                
            
        # step2:do eventcodes in one inform
        for eventcode in eventcodes:

            log.app_info("cpe(sn=%s), eventcode=%s" %(cpe.get_sn(), eventcode))

            # nwf 2013-05-21; skip eventcode fail
            if ("0 BOOTSTRAP" in eventcode):                
                ret = bootstrap_cu(cpe)
                
            elif ("X CU BIND" in eventcode):
                ret = bind_cu(cpe, user_name, user_id)
                              
            elif ("X_CU_ADMINPASSWORDCHANGE" in eventcode):
                ret = accountchange_cu(cpe)                
                
    except Exception,e:
        print_trace(e) 	
                
    return ret


def reset_digest_account_and_telecom_account_ct(cpe):
    """
    重置双向的DIGEST认证账号和电信维护账号密码
    """
    
    ret         = ERR_FAIL
    err_message = ""        

    for i in [1]:
        # 新的双向的DIGEST认证账号的生成规则为：old+8为随机数
        user_name = get_random_8str(cpe.cpe_property.get_cpe2acs_loginname())
        password = get_random_8str(cpe.cpe_property.get_cpe2acs_loginpassword())
        connection_request_user_name = get_random_8str(cpe.cpe_property.get_acs2cpe_loginname())
        connection_request_password = get_random_8str(cpe.cpe_property.get_acs2cpe_loginpassword())
        
        # 新的电信维护账号密码的生成规则为 “cttelecomadmin” + 8位随机数
        tele_com_account_password = get_random_8str("cttelecomadmin")
        
        # 组建所有要设置的节点参数
        dict_data = {"ParameterList": [
                        dict(Name="InternetGatewayDevice.ManagementServer.Username", 
                             Value=user_name),
                        dict(Name="InternetGatewayDevice.ManagementServer.Password", 
                             Value=password),
                        dict(Name="InternetGatewayDevice.ManagementServer.ConnectionRequestUsername", 
                             Value=connection_request_user_name),
                        dict(Name="InternetGatewayDevice.ManagementServer.ConnectionRequestPassword", 
                             Value=connection_request_password),
                        dict(Name="InternetGatewayDevice.DeviceInfo.X_CT-COM_TeleComAccount.Enable", 
                             Value="1"), 
                        dict(Name="InternetGatewayDevice.DeviceInfo.X_CT-COM_TeleComAccount.Password", 
                             Value=tele_com_account_password)]}
        # 组建工单消息，下发工单执行命令
        obj = MsgWorklistBuild("Auto_SetParameterValue", dict_data)                 
        obj_database = EventCode.auto_build_bind_physic_worklist(cpe, obj)        
        try:
            ret, err_message = EventCode.tx_worklist_exec(obj_database)        
            ret = EventCode.rx_worklist_exec(ret, err_message)      
            if (ret == ERR_SUCCESS):
            
                ret, err_message = EventCode.wait_worklist_exec_finish(obj_database)
                if ret == ERR_SUCCESS:
                    cpe.cpe_property.set_cpe2acs_loginname(user_name)
                    cpe.cpe_property.set_cpe2acs_loginpassword(password)
                    cpe.cpe_property.set_acs2cpe_loginname(connection_request_user_name)
                    cpe.cpe_property.set_acs2cpe_loginpassword(connection_request_password)
                    
                    log.app_info("worklist(Auto_SetParameterValue) execute success.")
                    log.app_info("update InternetGatewayDevice.ManagementServer.Username success: %s" % user_name)
                    log.app_info("update InternetGatewayDevice.ManagementServer.Password success: %s" % password)
                    log.app_info("update InternetGatewayDevice.ManagementServer.ConnectionRequestUsername success: %s" % connection_request_user_name)
                    log.app_info("update InternetGatewayDevice.ManagementServer.ConnectionRequestPassword success: %s" % connection_request_password)
                    log.app_info("update InternetGatewayDevice.DeviceInfo.X_CT-COM_TeleComAccount.Password success: %s" % tele_com_account_password)
                else:
                    log.app_err(err_message)
                    
                    break
            else:
                desc = "worklist(Auto_SetParameterValue) execute fail."
                log.app_err(desc)
                
                break
        except Exception,e:
            print_trace(e) 	
            break
        
        ret = ERR_SUCCESS

    return ret


def reset_digest_account_and_telecom_account_cu(cpe):
    """
    重置联通双向的DIGEST认证账号和终端维护账号密码
    """
    
    ret         = ERR_FAIL
    err_message = ""        

    for i in [1]:
        # 新的双向的DIGEST认证账号的生成规则为：old+8为随机数
        user_name = get_random_8str(cpe.cpe_property.get_cpe2acs_loginname())
        password = get_random_8str(cpe.cpe_property.get_cpe2acs_loginpassword())
        connection_request_user_name = get_random_8str(cpe.cpe_property.get_acs2cpe_loginname())
        connection_request_password = get_random_8str(cpe.cpe_property.get_acs2cpe_loginpassword())
        
        # 新的电信维护账号密码的生成规则为 “cutelecomadmin” + 8位随机数
        tele_com_account_password = get_random_8str("cuadmin")
        
        # 组建所有要设置的节点参数
        dict_data = {"ParameterList": [
                        dict(Name="InternetGatewayDevice.ManagementServer.Username", 
                             Value=user_name),
                        dict(Name="InternetGatewayDevice.ManagementServer.Password", 
                             Value=password),
                        dict(Name="InternetGatewayDevice.ManagementServer.ConnectionRequestUsername", 
                             Value=connection_request_user_name),
                        dict(Name="InternetGatewayDevice.ManagementServer.ConnectionRequestPassword", 
                             Value=connection_request_password),
                        dict(Name="InternetGatewayDevice.X_CU_Function.Web.AdminPassword", 
                             Value=tele_com_account_password)]}
        # 组建工单消息，下发工单执行命令
        obj = MsgWorklistBuild("Auto_SetParameterValue", dict_data)                 
        obj_database = EventCode.auto_build_bind_physic_worklist(cpe, obj)        
        try:
            ret, err_message = EventCode.tx_worklist_exec(obj_database)        
            ret = EventCode.rx_worklist_exec(ret, err_message)      
            if (ret == ERR_SUCCESS):
            
                ret, err_message = EventCode.wait_worklist_exec_finish(obj_database)
                if ret == ERR_SUCCESS:
                    cpe.cpe_property.set_cpe2acs_loginname(user_name)
                    cpe.cpe_property.set_cpe2acs_loginpassword(password)
                    cpe.cpe_property.set_acs2cpe_loginname(connection_request_user_name)
                    cpe.cpe_property.set_acs2cpe_loginpassword(connection_request_password)
                    
                    log.app_info("worklist(Auto_SetParameterValue) execute success.")
                    log.app_info("update InternetGatewayDevice.ManagementServer.Username success: %s" % user_name)
                    log.app_info("update InternetGatewayDevice.ManagementServer.Password success: %s" % password)
                    log.app_info("update InternetGatewayDevice.ManagementServer.ConnectionRequestUsername success: %s" % connection_request_user_name)
                    log.app_info("update InternetGatewayDevice.ManagementServer.ConnectionRequestPassword success: %s" % connection_request_password)
                    log.app_info("update InternetGatewayDevice.X_CU_Function.Web.AdminPassword success: %s" % tele_com_account_password)
                else:
                    log.app_err(err_message)
                    
                    break
            else:
                desc = "worklist(Auto_SetParameterValue) execute fail."
                log.app_err(desc)
                
                break
        except Exception,e:
            print_trace(e) 	
            break
        
        ret = ERR_SUCCESS

    return ret  


def find_modulation_type_value(soap_inform):
    """
    """
    modulation_type_value = ""
          
    para_list = soap_inform.result.ParameterList
    for para in para_list:
        if (-1 != para.Name.rfind("ModulationType")):
            modulation_type_value = para.Value
            break
    
    return modulation_type_value

 
def is_modulation_type_match(cpe):
    """
    ct v4.0(and ADSL/VDSL) is valid

    return success = (match)
    return fail = (not match)
    """
    
    ret                     = ERR_SUCCESS   # default match     
    modulation_type_value   = ""
    cpe_device_type         = ""

    for nwf in [1]:

        try:
            cpe_device_type = cpe.cpe_property.cpe_domain.upper()
            if ((-1 == cpe_device_type.find("ADSL")) and
                (-1 == cpe_device_type.find("VDSL"))):
                desc = "cpe is not ([adsl or vdsl]) ,walk through like v3.0"
                log.app_info(desc)                
                break
        
            soap_inform = cpe.cpe_soap.get_soap_inform()
            modulation_type_value = find_modulation_type_value(soap_inform)
            if (not modulation_type_value):                
                desc = "no modulation_type, CT v4.0 will not fail here."
                log.app_info(desc)      
                ret = ERR_FAIL
                break
            
            modulation_type_value = modulation_type_value.upper()

            cpe_device_type2 = "ADSL"
            if (-1 == cpe_device_type.find("ADSL")):
                cpe_device_type2 = "VDSL"

            modulation_type_value2 = "ADSL"
            if (-1 == modulation_type_value.find("ADSL")):
                modulation_type_value2 = "VDSL"
            
        except Exception,e:
            break  
            
        if (cpe_device_type2 != modulation_type_value2):
            ret = ERR_FAIL
    
    return ret    


def update_interface_version(cpe):
    """
    0 boot need update AUTO version
    """
    
    ret         = ERR_FAIL
    err_message = ""        

    sn = cpe.get_sn()
    
    for nwf in [1]:                
        
        # physic worklist --------------- 
        obj = MsgWorklistBuild("Auto_UpdateInterfaceVersion", {})  
        obj_database = EventCode.auto_build_bind_physic_worklist(cpe, obj)       
        try:
            ret, err_message = EventCode.tx_worklist_exec(obj_database)        
            ret = EventCode.rx_worklist_exec(ret, err_message)      
            if (ret == ERR_SUCCESS):

                ret, err_message = EventCode.wait_worklist_exec_finish(obj_database)
                if ret == ERR_SUCCESS:                
                    desc = "worklist(Auto_UpdateInterfaceVersion) execute success."
                    log.app_info(desc)
                else:
                    log.app_err(err_message)
                    
                    break
            else:
                desc = "worklist(Auto_UpdateInterfaceVersion) execute fail."
                log.app_err(desc) 
                
                break
        except Exception,e:
            print_trace(e) 	
            break     

        ret = ERR_SUCCESS

    if (ret == ERR_SUCCESS):
        cpe.cpe_property.set_cpe_interface_version("v4.0")
    else:
        cpe.cpe_property.set_cpe_interface_version("v3.0")

    return ret


def auto_exec_worklist(worklist, cpe):
    """
    """
    ret             = ERR_FAIL
    err_message     = ""
        
    sn = cpe.get_sn()            
    for nwf in [1]:
        
        # physic worklist --------------- 
        obj = MsgWorklistBuild(worklist, {})  
        obj_database = EventCode.auto_build_bind_physic_worklist(cpe, obj)       
        try:
            ret, err_message = EventCode.tx_worklist_exec(obj_database)        
            ret = EventCode.rx_worklist_exec(ret, err_message)      
            if (ret == ERR_SUCCESS):

                ret, err_message = EventCode.wait_worklist_exec_finish(obj_database)
                if ret == ERR_SUCCESS:                
                    desc = "worklist(%s) execute success." %worklist
                    log.app_info(desc)
                else:
                    log.app_err(err_message)                            
                    break
            else:
                desc = "worklist(%s) execute fail." %worklist
                log.app_err(desc)                         
                break
        except Exception,e:
            print_trace(e) 	
            break     

        ret = ERR_SUCCESS

    return ret    
    