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
    parent5 = os.path.dirname(parent4)
    parent6 = os.path.dirname(parent5)
    parent7 = os.path.dirname(parent6)
    parent8 = os.path.dirname(parent7)
    sys.path.insert(0, parent8)
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
parent1 = os.path.dirname(g_prj_dir)  #
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
import _Config

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

            # 新的双向的DIGEST认证账号的生成规则为：old+8为随机数
            user_name = get_random_8str(_Config.CPE2ACS_LOGIN_NAME)
            password = get_random_8str(_Config.CPE2ACS_LOGIN_PASSWORD)
            connection_request_user_name = get_random_8str(_Config.ACS2CPE_LOGIN_NAME)
            connection_request_password = get_random_8str(_Config.ACS2CPE_LOGIN_PASSWORD)

            # 新的电信维护账号密码的生成规则为 “cttelecomadmin” + 8位随机数
            # tele_com_account_password = get_random_8str("cttelecomadmin")

            # 组建所有要设置的节点参数
            ParameterList = [
                        dict(Name="InternetGatewayDevice.ManagementServer.Username",
                             Value=user_name),
                        dict(Name="InternetGatewayDevice.ManagementServer.Password",
                             Value=password),
                        dict(Name="InternetGatewayDevice.ManagementServer.ConnectionRequestUsername",
                             Value=connection_request_user_name),
                        dict(Name="InternetGatewayDevice.ManagementServer.ConnectionRequestPassword",
                             Value=connection_request_password)]
                        # dict(Name="InternetGatewayDevice.DeviceInfo.X_CT-COM_TeleComAccount.Enable",
                        #      Value="1"),
                        # dict(Name="InternetGatewayDevice.DeviceInfo.X_CT-COM_TeleComAccount.Password",
                        #      Value=tele_com_account_password)]

            u1=User(sn, ip=worklistcfg.AGENT_HTTP_IP, port=worklistcfg.AGENT_HTTP_PORT, page=worklistcfg.WORKLIST2AGENT_PAGE, sender=KEY_SENDER_WORKLIST, worklist_id=obj.id_)
            log.app_info ("Auto process set parameter value: %s " % ParameterList)
            ret_rpc, ret_data = u1.set_parameter_values(ParameterList=ParameterList)
            ret_datas = ret_datas + "\n" + str(ret_data)
            if (ret_rpc == ERR_SUCCESS):
                info = "success:%s" % ret_data
                log.app_info(info)
            else:
                info = "fail:%s"%ret_data
                log.app_err (info)
                break

            # update 2 acs
            ret_rpc, ret_data = update_username_password_to_acs(sn, user_name, password, connection_request_user_name, connection_request_password)
            if (ret_rpc != ERR_SUCCESS):
                info = "fail:%s"%ret_data
                log.app_err (info)
                break

            # -------------------------
            log.app_info ("Auto process get rpc methods")
            ret_rpc, ret_data = u1.get_rpc_methods()
            ret_datas = ret_datas + "\n" + str(ret_data)
            if (ret_rpc == ERR_SUCCESS):
                info = "success:%s" % ret_data
                log.app_info(info)
            else:
                info = "fail:%s"%ret_data
                log.app_err (info)
                break

            ret_worklist = ERR_SUCCESS

        except Exception,e:
            info = str(e)
            log.app_err (info)
            ret_datas = ret_datas + "\n" + info
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
