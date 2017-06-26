#coding:utf-8

# -----------------------------rpc --------------------------

import os
import sys
import re

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
    
    ret_worklist = ERR_FAIL       # 工单执行结果，默认为FAIL
    ret_rpc = ERR_FAIL            # RPC方法执行结果，默认为FAIL
    ret_datas = ""                # 初始化执行成功的返回信息
    sn = obj.sn      
    
    # 根路径，在该路径下查找上网账号和密码的节点全路径
    ROOT_PATH = "InternetGatewayDevice.WANDevice.1.WANConnectionDevice."
    # 上网账号和密码的正则表达式
    regex_user_name_path = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice\.\d+\.WANPPPConnection\.\d+\.Username"
    regex_password_path = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice\.\d+\.WANPPPConnection\.\d+\.Password"
    find_user_name_path = False       # 是否找到上网账号节点路径的标志，默认为False
    find_password_path = False        # 是否找到上网密码节点路径的标志，默认为False
    user_name_path = ""               # 用于保存上网账号节点路径  
    password_path = ""                # 用于保存上网密码几多路径
    
    for nwf in [1]:
        
        try:
            u1=User(sn, ip=worklistcfg.AGENT_HTTP_IP, port=worklistcfg.AGENT_HTTP_PORT,
                    page=worklistcfg.WORKLIST2AGENT_PAGE, sender=KEY_SENDER_WORKLIST, worklist_id=obj.id_)            
            #reboot_Yes = 0
            
            #第一步：调用GetParameterNames方法，查询WAN连接
            info = u"开始调用GetParameterNames方法，查询WAN连接\n"
            log.app_info (info)
            ret_datas += info
            
            ret_rpc, ret_data = u1.get_parameter_names(ParameterPath=ROOT_PATH)
            if (ret_rpc == ERR_SUCCESS):
                info = u"查询WAN连接成功\n"
                log.app_info (info)
                ret_datas += info
                
                # 从查询结果中筛选上网账号和密码的路径
                for tmp_dict in ret_data['ParameterList']:
                    
                    if re.search(regex_user_name_path, tmp_dict['Name']) is not None:
                        find_user_name_path = True
                        user_name_path = tmp_dict['Name']
                        
                    if re.search(regex_password_path, tmp_dict['Name']) is not None:
                        find_password_path = True
                        password_path = tmp_dict['Name']
                        
                    if find_user_name_path and find_password_path:
                        break
                else:
                    # 没有找到匹配的路径，说明没有相应的节点，直接返回
                    info = u"没有找到上网账号和密码的节点路径.\n"
                    log.app_info (info)
                    ret_datas += info
                    break
                
                # 找到相应的节点路径，获取节点路径的值
                list_path = [user_name_path, password_path]
                ret_rpc, ret_data = u1.get_parameter_values(ParameterNames=list_path)
                if (ret_rpc == ERR_SUCCESS):
                    # TODO:如果以后需要返回查询到的值，可以返回ret_data进行解析
                    info = u"查询终端上网账号和密码成功. %s\n" % ret_data
                    log.app_info (info)
                    ret_datas += info
                    ret_datas += str(ret_data)
                    
                    
                    obj.dict_ret["str_result"] = ret_datas
                else:
                    info = u"查询终端上网账号和密码失败.\n %s \n" % ret_data
                    log.app_err (info)
                    ret_datas += info
                    break
            else:
                #对于失败的情况，直接返回失败
                info = u"查询WAN连接失败,错误信息:%s\n" % ret_data
                log.app_err (info)
                ret_datas += info
                break

            ret_worklist = ERR_SUCCESS

        except Exception,e:
            log.app_err (e)
            break                
        
    return ret_worklist      

if __name__ == '__main__':
    log_dir = g_prj_dir
    log.start(name="nwf", directory=log_dir, level="DebugWarn")
    log.set_file_id(testcase_name="tr069")    
    
    obj = MsgWorklistExecute(id_="1")
    obj.sn = "021018-021018010001"
    test_script(obj)
    
    
    