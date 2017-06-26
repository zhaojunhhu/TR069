#coding:utf-8

# -----------------------------rpc --------------------------
import os
from TR069.lib.common.error import *
from TR069.lib.users.user import UserRpc as User
from time import sleep
import TR069.lib.common.logs.log as log 
import _Common
reload(_Common)
from _Common import *
import  TR069.lib.worklists.worklistcfg as worklistcfg 

def WLANMultiWANSetUP(obj, sn, WANEnable_Switch, DeviceType,
                      AccessMode, PVC_OR_VLAN,
                      dict_wanlinkconfig={},
                      dict_wanpppconnection={},
                      dict_wanipconnection={},
                      change_account=1,
                      rollbacklist=[]):
    """
    """
    ret_res = ERR_FAIL # 脚本返回值,成功或失败.缺省失败
    ret_data_scr = "" # 返回结果日志
    
    ROOT_PATH = "InternetGatewayDevice.WANDevice.1.WANConnectionDevice."
    for nwf in [1]:
        try:
            u1=User(sn, ip=worklistcfg.AGENT_HTTP_IP, port=worklistcfg.AGENT_HTTP_PORT, page=worklistcfg.WORKLIST2AGENT_PAGE, sender=KEY_SENDER_WORKLIST, worklist_id=obj.id_)
            reboot_Yes = 0

            WAN_Flag = 1 # 强制新建
            if WAN_Flag == 1 or WAN_Flag == 2:
                #第三--一步：新建WANConnectionDevice实例
                info = u"开始调用AddObject新建WANConnectionDevice实例\n"
                log.app_info (info)
                ret_data_scr += info
                Classpath = ROOT_PATH
                #sleep(3)  # must be ;otherwise exception
                ret3, ret_data3 = u1.add_object(
                                    ObjectName=Classpath)
                if (ret3 == ERR_SUCCESS):
                    instanceNum1 = ret_data3["InstanceNumber"]
                    info = u"新建WANConnectionDevice实例成功,返回实例号：%s\n" % instanceNum1
                    log.app_info (info)
                    ret_data_scr += info
                    tmp_path3 = Classpath + instanceNum1 + '.'
                    # GCW 20130327 增加回退机制
                    rollbacklist.append(tmp_path3)
                    rebootFlag = int(ret_data3["Status"])
                    if (rebootFlag == 1):
                        reboot_Yes = 1
                else:
                    #对于失败的情况，直接返回失败
                    info = u"新建WANConnectionDevice实例失败，错误原因：%s\n" % ret_data3
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                
                #第三--二步：新建WANIPConnection或WANPPPConnection实例
                #log.app_info (u"第四步：增加WANIPConnection或WANPPPConnection实例")
                #只有是桥模式和路由PPPOE时,才新建WANPPPConnection实例.暂时不考虑桥
                if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':
                    path4 = ROOT_PATH + instanceNum1 + '.WANPPPConnection.'
                    info = u"开始调用AddObject新建WAN连接的WANPPPConnection实例\n"
                else:
                    path4 = ROOT_PATH + instanceNum1 + '.WANIPConnection.'
                    info = u"开始调用AddObject新建WAN连接的WANIPConnection实例\n"
                log.app_info (info)
                ret_data_scr += info
                
                #sleep(3)  # must be ;otherwise exception
                ret4, ret_data4 = u1.add_object(
                                    ObjectName=path4)

                if (ret4 == ERR_SUCCESS):
                    instanceNum1 = ret_data4["InstanceNumber"]
                    tmp_path4 = path4 + instanceNum1
                    info = u"新建实例成功,返回实例号：%s\n" % instanceNum1
                    log.app_info (info)
                    ret_data_scr += info
                    rebootFlag = int(ret_data4["Status"])
                    if (rebootFlag == 1):
                        reboot_Yes = 1
                else:
                    #对于失败的情况，如何处理?
                    #对于失败的情况,直接返回失败
                    info = u"新建实例实例失败，退出执行，错误原因：%s\n" % ret_data4
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                
                #第三--三步:调用SetParameterValues设置linkconfig参数：

                if DeviceType == 'ADSL':
                    path5 = tmp_path3 + 'WANDSLLinkConfig.'
                    info = u"开始调用SetParameterValues设置WANDSLLinkConfig参数\n"
                elif DeviceType == 'LAN':
                    path5 = tmp_path3 + 'WANEthernetLinkConfig.'
                    info = u"开始调用SetParameterValues设置WANEthernetLinkConfig参数\n"
                elif DeviceType == 'EPON':
                    path5 = tmp_path3 + 'X_CT-COM_WANEponLinkConfig.'
                    info = u"开始调用SetParameterValues设置X_CT-COM_WANEponLinkConfig参数\n"
                elif DeviceType == 'VDSL':
                    path5 = tmp_path3 + 'WANDSLLinkConfig.'
                    info = u"开始调用SetParameterValues设置WANDSLLinkConfig参数\n"
                elif DeviceType == 'GPON':
                    path5 = tmp_path3 + 'X_CT-COM_WANGponLinkConfig.'
                    info = u"开始调用SetParameterValues设置X_CT-COM_WANGponLinkConfig参数\n"
                else:
                    path5 = tmp_path3 + 'WANDSLLinkConfig.'
                    info = u"开始调用SetParameterValues设置WANDSLLinkConfig参数\n"
                log.app_info (info)
                ret_data_scr += info
                
                para_list5 = []
                for i in dict_wanlinkconfig:
                    if dict_wanlinkconfig[i][0] == 1:
                        tmp_path = path5 + i
                        para_list5.append(dict(Name=tmp_path, Value=dict_wanlinkconfig[i][1]))
                if para_list5 == []:
                    ret_data = u"参数列表为空,请检查\n"
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                
                #sleep(3)  # must be ;otherwise exception
                ret5, ret_data5 = u1.set_parameter_values(ParameterList=para_list5)
                if (ret5 == ERR_SUCCESS):
                    info = u"设置参数成功\n"
                    log.app_info (info)
                    ret_data_scr += info
                    rebootFlag = int(ret_data5["Status"])
                    if (rebootFlag == 1):
                        reboot_Yes = 1
                else:
                    #对于失败的情况，直接退出
                    info = u"设置参数失败，错误原因：%s\n" % ret_data5
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr

                #第三--四步:调用SetParameterValues设置WANPPPConnection参数：
                if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':
                    tmp_values = dict_wanpppconnection
                    info = u"开始调用SetParameterValues设置WANPPPConnection参数\n"
                else:
                    tmp_values = dict_wanipconnection
                    info = u"开始调用SetParameterValues设置WANIPConnection参数\n"
                log.app_info (info)
                ret_data_scr += info
                
                #第三--四步:调用SetParameterValues设置WANPPPConnection参数：
                #log.app_info (u"第六步：调用SetParameterValues设置参数")
                path6 = tmp_path4 + '.'
                para_list6 = []
                WAN_Enable = []
                for i in tmp_values:
                    if tmp_values[i][0] == 1:
                        #如果WAN连接使能需单独下发,则将使能的动作单独保存
                        if WANEnable_Switch == False and i == 'Enable':
                            WAN_Enable.append(dict(Name=path6 + i, Value=tmp_values[i][1]))
                            continue
                        
                        tmp_path = path6 + i
                        para_list6.append(dict(Name=tmp_path, Value=tmp_values[i][1]))
                if para_list6 == []:
                    ret_data = u"参数列表为空,请检查\n"
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                
                #sleep(3)  # must be ;otherwise exception
                ret6, ret_data6 = u1.set_parameter_values(ParameterList=para_list6)
                if (ret6 == ERR_SUCCESS):
                    info = u"设置参数成功\n"
                    log.app_info (info)
                    ret_data_scr += info
                    rebootFlag = int(ret_data6["Status"])
                    if (rebootFlag == 1):
                        reboot_Yes = 1
                else:
                    #对于失败的情况，直接返回失败
                    #对于失败的情况，直接返回失败
                    info = u"设置参数失败，错误原因：%s\n" % ret_data6
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                
                #将WAN连接使能单独下发
                if WAN_Enable != []:
                    info = u"开始调用SetParameterValues设置WAN连接使能参数\n"
                    log.app_info (info)
                    ret_data_scr += info
                    #sleep(3)  # must be ;otherwise exception
                    ret_wan_enable, ret_data_wan_enable = u1.set_parameter_values(ParameterList=WAN_Enable)
                    if (ret_wan_enable == ERR_SUCCESS):
                        info = u"设置WAN连接使能参数成功\n"
                        log.app_info (info)
                        ret_data_scr += info
                        rebootFlag = int(ret_data_wan_enable["Status"])
                        if (rebootFlag == 1):
                            reboot_Yes = 1
                    else:
                        #对于失败的情况，直接返回错误
                        info = u"设置WAN连接使能参数失败，错误原因：%s\n" % ret_data_wan_enable
                        log.app_err (info)
                        ret_data_scr += info
                        return ret_res, ret_data_scr
        
            # 如果需要重启,则下发Reboot方法,目前采用静等待130S
            if (reboot_Yes == 1):

                # nwf 2013-07-12
                #sleep(130)
                ret, ret_data = u1.wait_next_inform(sn, worklistcfg.REBOOT_WAIT_NEXT_INFORM_TIMEOUT)
                ret_data_scr += ret_data
                if ret != ERR_SUCCESS:                    
                    break                
                
            #第七步：调用修改电信维护密码,目前密码固定为nE7jA%5m
            ret, ret_data = ChangeAccount_CT(obj, sn, change_account)
            if ret == ERR_FAIL:
                ret_data_scr += ret_data
                return ret, ret_data_scr
            else:
                ret_data_scr += ret_data
            
            ret_res = ERR_SUCCESS
        except Exception,e:
            log.app_err (str(e))
            ret_data_scr += str(e)+'\n'
            return ret_res, ret_data_scr
    
    return ret_res, ret_data_scr     