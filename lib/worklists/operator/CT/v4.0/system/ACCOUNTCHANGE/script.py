#coding:utf-8


# -----------------------------rpc --------------------------

import os
import sys

#debug
DEBUG_UNIT = True
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

from    TR069.lib.common.error      import *
from    TR069.lib.users.user        import UserRpc as User 
from    time import sleep
import  TR069.lib.common.logs.log   as log 
from    TR069.lib.common.event      import *
import  TR069.lib.worklists.worklistcfg      as worklistcfg 

g_prj_dir = os.path.dirname(__file__)
parent1 = os.path.dirname(g_prj_dir)
parent2 = os.path.dirname(parent1) # dir is system
try:
    i = sys.path.index(parent1)
    if (i !=0):
        # stratege= boost priviledge
        sys.path.pop(i)
        sys.path.insert(0, parent1)
except Exception,e: 
    sys.path.insert(0, parent1)


import _Common
reload(_Common)
from _Common import *


def test_script(obj):
    """
    obj = MsgWorklistExecute
    default function name= test_script    
    """
    ret_worklist = ERR_FAIL # default
    ret_rpc = ERR_FAIL
    ret_datas = ""
    sn = obj.sn      

    
    for nwf in [1]:
        try:
            
            # data传参            
            password = random.randrange(10000000,99999999)
            password = "telecomadmin" + str(password)

            ParameterList = [
                            dict(Name="InternetGatewayDevice.DeviceInfo.X_CT-COM_TeleComAccount.Enable", 
                                 Value="1"), 
                            dict(Name="InternetGatewayDevice.DeviceInfo.X_CT-COM_TeleComAccount.Password", 
                                 Value=password)]           
            
            u1=User(sn, ip=worklistcfg.AGENT_HTTP_IP, port=worklistcfg.AGENT_HTTP_PORT, page=worklistcfg.WORKLIST2AGENT_PAGE, sender=KEY_SENDER_WORKLIST, worklist_id=obj.id_)            
            log.app_info ("Auto process set parameter value: %s " % ParameterList)
            ret_rpc, ret_data = u1.set_parameter_values(ParameterList=ParameterList)
            
            if (ret_rpc == ERR_SUCCESS):
                ret_datas = ret_datas + "\n" + str(ret_data)
                log.app_info("success:%s" % ret_data)
            else:
                log.app_err ("fail:%s"%ret_data)
                break
            
            ret_worklist = ERR_SUCCESS
            obj.dict_ret["str_result"] = ret_datas

        except Exception,e:
            log.app_err (e)
            break                
        
    return ret_worklist

if __name__ == '__main__':
    log_dir = g_prj_dir
    log.start(name="nwf", directory=log_dir, level="DebugWarn")
    log.set_file_id(testcase_name="tr069")    
    
    obj = MsgWorklistExecute(id_="1")
    obj.sn = "2013012901"
    test_script(obj)
    
    
    