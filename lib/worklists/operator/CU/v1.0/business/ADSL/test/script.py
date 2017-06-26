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
    i = sys.path.index(parent2)
    if (i !=0):
        # stratege= boost priviledge
        sys.path.pop(i)
        sys.path.insert(0, parent2)
except Exception,e: 
    sys.path.insert(0, parent2)

import _Common
reload(_Common)
from _Common import *

print "cu common"

def test_script(obj):
    """
    obj = MsgWorklistExecute
    default function name= test_script    
    """
    ret_worklist    = ERR_FAIL # default
    ret_rpc         = ERR_FAIL
    ret_datas       = ""
    
    sn = obj.sn      
    
    for nwf in [1]:
        try:
            
            u1=User(sn, ip=worklistcfg.AGENT_HTTP_IP, port=worklistcfg.AGENT_HTTP_PORT, page=worklistcfg.WORKLIST2AGENT_PAGE, sender=KEY_SENDER_WORKLIST, worklist_id=obj.id_)            

            log.app_info ("cpe interface version=V1.0")
                    
            log.app_info ("first rpc")
            
            ret_rpc, ret_data = u1.get_rpc_methods()
            ret_datas = ret_datas + "\n" + str(ret_data)
            if (ret_rpc == ERR_SUCCESS):
                log.app_info("success:%s" %ret_data)
            else:
                log.app_err("fail:%s" %ret_data)
                break                                     

            
            #sleep(130)
            ret, ret_data = reboot_wait_next_inform(u1)
            if (ret != ERR_SUCCESS):
                ret_datas += ret_data
                break

            ret, ret_data = ChangeAccount_CU(obj, sn, 1)
            print ret_data
           
            
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
    
    
    