#coding:utf-8
# -----------------------------rpc --------------------------
import os
import re
from TR069.lib.common.error import *
from TR069.lib.users.user import UserRpc as User
from time import sleep
import TR069.lib.common.logs.log as log 
import _Common
reload(_Common)
from _Common import *
import  TR069.lib.worklists.worklistcfg as worklistcfg 


def SmartTV(obj,sn,
               X_CT_COM_Mode,
               X_CT_COM_VLAN,
               IPTV_Interface,
               change_account=1):
    """
    开通智能电视，即,将LAN侧（除绑定IPTV外的接口）与IPTV WAN连接的VLAN绑定
    """
    ret_res = ERR_FAIL # 返回成功或失败
    ret_data_scr = "" # 返回结果日志
    
    Lan_Interface_Path = "InternetGatewayDevice.LANDevice.1.LANEthernetInterfaceConfig."
       
    for i in [1]:
        
        try:
            u1=User(sn, ip=worklistcfg.AGENT_HTTP_IP, port=worklistcfg.AGENT_HTTP_PORT, page=worklistcfg.WORKLIST2AGENT_PAGE, sender=KEY_SENDER_WORKLIST, worklist_id=obj.id_)
            reboot_Yes = 0

            ret, lan_iptv = ParseLANName(IPTV_Interface)
            if ret == ERR_FAIL:
                info = u'输入的X_CT_COM_LanInterface参数错误'
                log.app_err (info)
                ret_data_scr += info
                return ret_res, ret_data_scr
            
            info = u"开始调用GetParameterNames方法，查询LANEthernetInterfaceConfig信息。\n"
            log.app_info (info)
            ret_data_scr += info
            ret_lan_device, ret_data_lan_device = u1.get_parameter_names(ParameterPath=Lan_Interface_Path, NextLevel=0)
            
            if (ret_lan_device == ERR_SUCCESS):
                info = u"查询LANEthernetInterfaceConfig信息成功。\n"
                log.app_info (info)
                ret_data_scr += info
                ret_data_lan_device = DelOwnParameterNames(ret_data_lan_device, Lan_Interface_Path)
            else:
                #对于失败的情况，直接返回失败
                info = u"查询LANEthernetInterfaceConfig信息失败,错误信息:%s 。\n" % ret_data_device_info
                log.app_err (info)
                ret_data_scr += info
                return ret_res, ret_data_scr
            
            reg_LAN_Mode = "InternetGatewayDevice.LANDevice.1.LANEthernetInterfaceConfig.[1-9]+.X_CT-COM_Mode"
            reg_LAN_VLAN = "InternetGatewayDevice.LANDevice.1.LANEthernetInterfaceConfig.[1-9]+.X_CT-COM_VLAN"
            
            bind_lan_list = []
            
            for i in xrange(len(ret_data_lan_device['ParameterList'])):
                
                tmp_lan_path = ret_data_lan_device['ParameterList'][i]['Name']
                
                m_Mode = re.match(reg_LAN_Mode,tmp_lan_path)
                m_VLAN = re.match(reg_LAN_VLAN,tmp_lan_path)
       
                if (m_Mode is not None) and (lan_iptv not in tmp_lan_path):
                    
                    bind_lan_list.append(dict(Name=tmp_lan_path,Value=X_CT_COM_Mode))
                
                if (m_VLAN is not None) and (lan_iptv not in tmp_lan_path):
                    
                    bind_lan_list.append(dict(Name=tmp_lan_path,Value=X_CT_COM_VLAN))
            
            if bind_lan_list == []:
                info = u"未查找到LAN侧的X_CT-COM_Mode和X_CT-COM_Vlan节点。"
                log.app_err (info)
                ret_data_scr += info
                return ret_res, ret_data_scr
            
            info = u"开始调用SetParameterValues设置LAN侧的X_CT-COM_Mode和X_CT-COM_VLAN。\n"       
            log.app_info (info)
            ret_data_scr += info
            
            ret, ret_data = u1.set_parameter_values(ParameterList=bind_lan_list)
            if (ret == ERR_SUCCESS):
                info = u"设置参数成功。\n"
                log.app_info (info)
                ret_data_scr += info
                rebootFlag = int(ret_data["Status"])
                if (rebootFlag == 1):
                    reboot_Yes = 1
                
            else:
                #对于失败的情况，直接返回失败
                info = u"设置参数失败，错误原因：%s 。\n" % ret_data
                log.app_info (info)
                ret_data_scr += info
                return ret_res, ret_data_scr
            
            # 如果需要重启,则下发Reboot方法,目前采用静等待130S
            if (reboot_Yes == 1):
                #sleep(130)
                ret, ret_data = reboot_wait_next_inform(u1)
                if (ret != ERR_SUCCESS):
                    ret_data_scr += ret_data
                    break
            
            #第七步：调用修改电信维护密码,目前密码固定为nE7jA%5m
            ret, ret_data = ChangeAccount_CT(obj, sn, change_account)
            if ret == ERR_FAIL:
                ret_data_scr += ret_data
                return ret, ret_data_scr
            else:
                ret_data_scr += ret_data
            
            ret_res = ERR_SUCCESS
            
        except Exception, e:
            log.app_err (str(e))
            ret_data_scr += str(e)+'\n'
            return ret_res, ret_data_scr
        
    return ret_res, ret_data_scr    
