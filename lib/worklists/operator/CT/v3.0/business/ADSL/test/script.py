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
    parent4 = os.path.dirname(parent3) 
    parent5 = os.path.dirname(parent4)
    parent6 = os.path.dirname(parent5)  # lib
    parent7 = os.path.dirname(parent6)
    parent8 = os.path.dirname(parent7)
    parent9 = os.path.dirname(parent8)
    sys.path.insert(0, parent9)         # project
    sys.path.insert(0, os.path.join(parent6, 'common'))
    sys.path.insert(0, os.path.join(parent6, 'worklist'))
    sys.path.insert(0, os.path.join(parent6, 'usercmd'))

from    TR069.lib.common.error      import *
from    TR069.lib.users.user        import UserRpc as User 
from    time import sleep
import  TR069.lib.common.logs.log   as log 
from    TR069.lib.common.event      import *
import  TR069.lib.worklists.worklistcfg      as worklistcfg 

g_prj_dir = os.path.dirname(__file__)
parent1 = os.path.dirname(g_prj_dir)  # system
parent2 = os.path.dirname(parent1)      # ct\v3.0
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

import imp
name_imp = "_IPTVEnable"
file_imp, imppath, description = imp.find_module(name_imp, [parent2])
_IPTVEnable =imp.load_module(name_imp, file_imp, imppath, description)
if (file_imp):
    file_imp.close()

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

            desc = str(_IPTVEnable)
            log.app_info (desc)
            log.app_info ("sys.path=%s" % sys.path) 
             
            u1=User(sn, ip=worklistcfg.AGENT_HTTP_IP, port=worklistcfg.AGENT_HTTP_PORT, page=worklistcfg.WORKLIST2AGENT_PAGE, sender=KEY_SENDER_WORKLIST, worklist_id=obj.id_)            

            log.app_info ("cpe interface version=v3.0")
            
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
                ret_data_scr += ret_data
                break
           
            
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
    
    
    