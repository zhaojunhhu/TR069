#coding:utf-8

# -----------------------------rpc --------------------------

import os
import sys

#debug
DEBUG_UNIT = False
if (DEBUG_UNIT):
    g_prj_dir = os.path.dirname(__file__)
    parent1 = os.path.dirname(g_prj_dir)
    parent2 = os.path.dirname(parent1)
    parent3 = os.path.dirname(parent2)
    parent4 = os.path.dirname(parent3)  # tr069v3\lib
    sys.path.insert(0, parent4)
    sys.path.insert(0, os.path.join(parent4, 'common'))
    sys.path.insert(0, os.path.join(parent4, 'worklist'))
    sys.path.insert(0, os.path.join(parent4, 'usercmd'))

from TR069.lib.common.error import *
from TR069.lib.users.user import UserRpc as User
from time import sleep
import TR069.lib.common.logs.log as log 
from TR069.lib.common.event import *
import  TR069.lib.worklists.worklistcfg as worklistcfg 

def test_script(obj):
    """
    obj = MsgWorklistExecute
    default function name= test_script    
    """
    ret_worklist    = ERR_FAIL # default
    ret_rpc         = ERR_FAIL
    ret_datas       = ""
    bool_reboot     = False
    instance_number = 1
    
    sn = obj.sn      
    
    for nwf in [1]:
        try:
            
            u1=User(sn, ip=worklistcfg.AGENT_HTTP_IP, port=worklistcfg.AGENT_HTTP_PORT, page=worklistcfg.WORKLIST2AGENT_PAGE, sender=KEY_SENDER_WORKLIST, worklist_id=obj.id_)            

            # ----------------------------------------------------------
            log.app_info ("first rpc")
            
            ret_rpc, ret_data = u1.set_parameter_values(ParameterList=[
                                dict(Name="InternetGatewayDevice.DeviceInfo.X_CT-COM_Alarm.Enable", 
                                    Value="1")])
            ret_datas = ret_datas + "\n" + str(ret_data)
            if (ret_rpc == ERR_SUCCESS):
                log.app_info("success:%s" %ret_data)
            else:
                log.app_err("fail:%s" %ret_data)
                break                                      
            
            # ----------------------------------------------------------            
            log.app_info ("second rpc")
            
            alarm_root_path     = "InternetGatewayDevice.DeviceInfo.X_CT-COM_Alarm.AlarmConfig."
            ret_rpc, ret_data   = u1.add_object(ObjectName=alarm_root_path)                        
            ret_datas = ret_datas + "\n" + str(ret_data)
            if (ret_rpc == ERR_SUCCESS):
                log.app_info("success:%s" %ret_data)
                
                status = int(ret_data["Status"])
                if (status == 1):
                    bool_reboot = True
                instance_number = int(ret_data["InstanceNumber"])
            else:
                log.app_err("fail:%s" %ret_data)
                break            
            
            # ----------------------------------------------------------            
            log.app_info ("third rpc")            
            
            alarm_node_path = "%s%s." %(alarm_root_path, instance_number)
            ret_rpc, ret_data = u1.set_parameter_values(ParameterList=[
                                dict(Name="%sParaList" %(alarm_node_path), 
                                    Value=obj.dict_data["parameterlist"]),
                                dict(Name="%sLimit-Max" %(alarm_node_path),
                                     Value=obj.dict_data["limit_max"]),
                                dict(Name="%sLimit-Min" %(alarm_node_path),
                                     Value=obj.dict_data["limit_min"]),
                                dict(Name="%sTimeList" %(alarm_node_path),
                                     Value=obj.dict_data["timelist"]),
                                dict(Name="%sMode" %(alarm_node_path),
                                     Value=obj.dict_data["mode"])])
            ret_datas = ret_datas + "\n" + str(ret_data)
            if (ret_rpc == ERR_SUCCESS):
                log.app_info("success:%s" %ret_data)
                
                status = int(ret_data["Status"])
                if (status == 1):                    
                    bool_reboot = True
            else:
                log.app_err("fail:%s" %ret_data)
                break             
            
            if (bool_reboot):
                # ----------------------------------------------------------            
                log.app_info ("need reboot")
                
                ret_rpc, ret_data = u1.reboot()
                ret_datas = ret_datas + "\n" + str(ret_data)                
                if (ret_rpc == ERR_SUCCESS):
                    log.app_info("success:%s" %ret_data)                
                else:
                    log.app_err("fail:%s" %ret_data)
                    break                 
            
            # need del
            obj.dict_ret["node_add_object"] = alarm_node_path
            ret_worklist = ERR_SUCCESS            

        except Exception,e:
            ret_datas = ret_datas + "\n" + str(e)
            
            log.app_err (e)
            break                

    obj.dict_ret["str_result"] = ret_datas     
    
    return ret_worklist         

if __name__ == '__main__':
    log_dir = g_prj_dir
    log.start(name="nwf", directory=log_dir, level="DebugWarn")
    log.set_file_id(testcase_name="tr069")    
    
    obj = MsgWorklistExecute(id_="1")
    obj.sn = "2013012901"
    test_script(obj)
    
    
    