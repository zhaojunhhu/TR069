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

#  针对”在TR069属性连接的同一PVC内开通桥接上网业务“业务编写的接口 add by shenlige 2014-5-30

def AddAnWAN(obj, sn, WANEnable_Switch, DeviceType,
             AccessMode, PVC_OR_VLAN,
             dict_wanlinkconfig={},
             dict_wanpppconnection={},
             dict_wanipconnection={},
             change_account=1,
             rollbacklist=[]):
    ret_res = ERR_FAIL # 返回成功或失败
    ret_data_scr = "" # 返回结果日志

    ROOT_PATH = "InternetGatewayDevice.WANDevice.1.WANConnectionDevice."
    for nwf in [1]:
        try:
            u1=User(sn, ip=worklistcfg.AGENT_HTTP_IP, port=worklistcfg.AGENT_HTTP_PORT, page=worklistcfg.WORKLIST2AGENT_PAGE, sender=KEY_SENDER_WORKLIST, worklist_id=obj.id_)
            reboot_Yes = 0
            
            #第一步：调用GetParameterNames方法，查询WAN连接
            info = u"开始调用GetParameterNames方法，查询WAN连接。\n"
            log.app_info (info)
            ret_data_scr += info
            #sleep(3)  # must be ;otherwise exception
            ret_root, ret_data_root = u1.get_parameter_names(ParameterPath=ROOT_PATH, NextLevel=0)
            if (ret_root == ERR_SUCCESS):
                info = u"查询WAN连接成功。\n"
                log.app_info (info)
                ret_data_scr += info
                # GCW　20130329　解决部分CPE同时将当前路径返回的情况,将其删除
                ret_data_root = DelOwnParameterNames(ret_data_root, ROOT_PATH)
            else:
                #对于失败的情况，直接返回失败
                info = u"查询WAN连接失败,错误信息:%s。\n" % ret_data_root
                log.app_err (info)
                ret_data_scr += info
                return ret_res, ret_data_scr

            
            if AccessMode == 'PPPoE' or AccessMode == 'DHCP' or AccessMode == 'Static' or AccessMode == 'PPPoE_Bridged':
               
                if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':
                        
                    X_CT_COM_ServiceList = dict_wanpppconnection['X_CT-COM_ServiceList'][1]
                     
                elif AccessMode == 'DHCP' or AccessMode == 'Static':
                        
                    X_CT_COM_ServiceList = dict_wanipconnection['X_CT-COM_ServiceList'][1]
                    
                ret_find,pvcorvlan_items, serverlist_items,connect_type_items, laninterface_items, ret_data_find = _find_wan_server_and_connecttype(u1,
                                     DeviceType,
                                     AccessMode,
                                     dict_wanpppconnection,
                                     dict_wanipconnection,
                                     ret_data_root,
                                     ret_data_scr)
                
                if ret_find == ERR_SUCCESS:
                    ret_data_scr = ret_data_find
                else:
                    ret_data_scr = ret_data_find
                    return ret_res, ret_data_find
                
                if AccessMode == "PPPoE_Bridged":
                    ConnectionType = "PPPoE_Bridged"
                else:
                    ConnectionType = "IP_Routed"
                
            else:
                info = u"输入的AccessMode参数不合法,请检查!\n"
                log.app_info (info)
                ret_data_scr += info
                return ret_res, ret_data_scr
            
            WAN_Flag = None 
            WAN_PVC = None  # 是否找到PVC
            path2 = '' # 保存查到有相同的PVC或关键参数值的WAN连接路径
            
            for i_pvcorvlan in pvcorvlan_items:
                            
                if i_pvcorvlan['Value'] == PVC_OR_VLAN:
                    WAN_PVC = 0
                    path2 = i_pvcorvlan['Name']
                    tmp_link_list = path2.split('.')[0:-2]     
                    path2 = '.'.join(tmp_link_list)      
                    break
                else:
                    # 查不到匹配的PVC
                    continue
            
            if WAN_PVC == None:
                # 如果一直没有查到相同的,则没有对WAN_Flag标志位做过修改,则走新建流程
                #对于未查找到相同PVC的，直接返回错误
                info = u"未查找到PVC或VLAN为 %s 的连接，请确认！" % PVC_OR_VLAN
                log.app_err (info)
                ret_data_scr += info
                return ret_res, ret_data_scr
            
            
            
            #第二步：逐个查找
            
            # 是否有查到已存在的类似WAN连接的状态位,符合以下标识,桥只关心PVC,其他的只关心X_CT-COM_ServiceList
            
            modify_path = "" 
            
            for i_connect in connect_type_items:
                            
                tmp_ppp_list = i_connect['Name'].split('.')[0:-1]     
                tmp_ppp_path = '.'.join(tmp_ppp_list)                # 保存XXXX.WANPPPConnection.i.路径
                    
                # 确定WAN，是否修改
                for j_serverlist in serverlist_items:
                        
                    tmp_serverlist = j_serverlist['Name']       
                        
                    # 同一条WAN连接下进行比较
                    if tmp_ppp_path in tmp_serverlist:
                            
                        # 桥对桥，路由对路由            
                        if ConnectionType in i_connect['Value']:
                                            
                            if X_CT_COM_ServiceList in j_serverlist['Value'] or j_serverlist['Value'] in X_CT_COM_ServiceList:
                                    
                                modify_path = j_serverlist['Name']
                                if j_serverlist['Value'] in X_CT_COM_ServiceList:
                                                    
                                    info = u"当前CPE中的X_CT-COM_ServiceList值包含于工单中要求的X_CT-COM_ServiceList值:%s,\n" % X_CT_COM_ServiceList
                                    info += u"走修改WAN连接的流程,且重新下发X_CT-COM_ServiceList值的修改。\n"
                                    log.app_info (info)
                                    ret_data_scr += info
                                    WAN_Flag = 0
                                else:
                                    info = u"当前工单中的X_CT-COM_ServiceList值：%s包含于CPE中的X_CT-COM_ServiceList值，\n" % X_CT_COM_ServiceList
                                    info += u"走修改WAN连接流程,但不下发对X_CT-COM_ServiceList值的修改。\n"
                                    log.app_info (info)
                                    ret_data_scr += info
                                    WAN_Flag = 3
                                            
                                break
                                               
                            else:
                                continue
                
            
            #0 均相同，只修改LinkConfig.（参考a.1包）
            #1 两者均不相同的情况下：等同于查到是空的情况，后续新建WAN连接参考a.2包）
            #2 部分相同，而且关键点X_CT-COM_ServiceList不相同的情况下：等同于查到是空的情况，后续新建WAN连接（参考a.3包）
            #3 部分相同，而且关键点X_CT-COM_ServiceList相同的情况下：等同于查到均相同的情况，只修改LinkConfig.（参考a.4包）
            if WAN_Flag == None:
                #第三--一步：新建WANConnectionDevice实例
                info = u"走X_CT-COM_ServiceList不相同的流程(新建WAN连接)。\n"
                log.app_info (info)
                ret_data_scr += info
                
                # 解决用户新建tr069WAN连接导致CPE与ACS通讯异常的问题,强制不准新建包含TR0069的WAN连接
                
                if (("tr069" in X_CT_COM_ServiceList) or
                    ("TR069" in X_CT_COM_ServiceList)):
                    info = u"工单失败:为避免新建包含tr069模式的WAN连接对原有tr069WAN连接产生影响,所以不再新建。\n"
                    log.app_info (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                """
                info = u"开始调用AddObject新建WANConnectionDevice实例。\n"
                log.app_info (info)
                ret_data_scr += info
                """
                
                #第三--二步：新建WANIPConnection或WANPPPConnection实例
                #只有是桥模式和路由PPPOE时,才新建WANPPPConnection实例
                if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':
                    path4 = path2 + '.WANPPPConnection.'
                    info = u"开始调用AddObject新建WAN连接的WANPPPConnection实例。\n"
                else:
                    path4 = path2 + '.WANIPConnection.'
                    info = u"开始调用AddObject新建WAN连接的WANIPConnection实例。\n"
                log.app_info (info)
                ret_data_scr += info
                
                #sleep(3)  # must be ;otherwise exception
                ret4, ret_data4 = u1.add_object(
                                    ObjectName=path4)
                
                if (ret4 == ERR_SUCCESS):
                    instanceNum1 = ret_data4["InstanceNumber"]
                    tmp_path4 = path4 + instanceNum1
                    info = u"新建实例成功,返回实例号：%s 。\n" % instanceNum1
                    log.app_info (info)
                    ret_data_scr += info
                    rebootFlag = int(ret_data4["Status"])
                    if (rebootFlag == 1):
                        reboot_Yes = 1
                else:
                    #对于失败的情况,直接返回失败
                    info = u"新建实例实例失败，退出执行，错误原因：%s 。\n" % ret_data4
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                
                # 同一PVC下两条WAN连接不需要设置link层：
                
                """
                if DeviceType == 'ADSL':
                    path5 = tmp_path3 + 'WANDSLLinkConfig.'
                    info = u"开始调用SetParameterValues设置WANDSLLinkConfig参数。\n"
                elif DeviceType == 'LAN':
                    path5 = tmp_path3 + 'WANEthernetLinkConfig.'
                    info = u"开始调用SetParameterValues设置WANEthernetLinkConfig参数。\n"
                elif DeviceType == 'EPON':
                    path5 = tmp_path3 + 'X_CT-COM_WANEponLinkConfig.'
                    info = u"开始调用SetParameterValues设置X_CT-COM_WANEponLinkConfig参数。\n"
                elif DeviceType == 'VDSL':
                    path5 = tmp_path3 + 'X_CT-COM_WANVdslLinkConfig.'
                    info = u"开始调用SetParameterValues设置X_CT-COM_WANVdslLinkConfig参数。\n"
                elif DeviceType == 'GPON':
                    path5 = tmp_path3 + 'X_CT-COM_WANGponLinkConfig.'
                    info = u"开始调用SetParameterValues设置X_CT-COM_WANGponLinkConfig参数。\n"
                else:
                    path5 = tmp_path3 + 'WANDSLLinkConfig.'
                    info = u"开始调用SetParameterValues设置WANDSLLinkConfig参数。\n"
                log.app_info (info)
                ret_data_scr += info
                
                para_list5 = []
                for i in dict_wanlinkconfig:
                    if dict_wanlinkconfig[i][0] == 1:
                        tmp_path = path5 + i
                        para_list5.append(dict(Name=tmp_path, Value=dict_wanlinkconfig[i][1]))
                if para_list5 == []:
                    ret_data = u"参数列表为空,请检查。\n"
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                #sleep(3)  # must be ;otherwise exception
                ret5, ret_data5 = u1.set_parameter_values(ParameterList=para_list5)
                if (ret5 == ERR_SUCCESS):
                    info = u"设置参数成功。\n"
                    log.app_info (info)
                    ret_data_scr += info
                    rebootFlag = int(ret_data5["Status"])
                    if (rebootFlag == 1):
                        reboot_Yes = 1
                else:
                    #对于失败的情况，直接退出
                    info = u"设置参数失败，错误原因：%s 。\n" % ret_data5
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                """
                #第三--四步:调用SetParameterValues设置WANPPPConnection参数：
                if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':
                    tmp_values = dict_wanpppconnection
                    info = u"开始调用SetParameterValues设置WANPPPConnection参数。\n"
                else:
                    tmp_values = dict_wanipconnection
                    info = u"开始调用SetParameterValues设置WANIPConnection参数。\n"
                log.app_info (info)
                ret_data_scr += info
                
                #第三--四步:调用SetParameterValues设置WANPPPConnection参数：
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
                    ret_data = u"参数列表为空,请检查。\n"
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                
                #sleep(3)  # must be ;otherwise exception
                ret6, ret_data6 = u1.set_parameter_values(ParameterList=para_list6)
                if (ret6 == ERR_SUCCESS):
                    info = u"设置参数成功。\n"
                    log.app_info (info)
                    ret_data_scr += info
                    rebootFlag = int(ret_data6["Status"])
                    if (rebootFlag == 1):
                        reboot_Yes = 1
                else:
                    #对于失败的情况，直接返回失败
                    info = u"设置参数失败，错误原因：%s 。\n" % ret_data6
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                
                #将WAN连接使能单独下发
                if WAN_Enable != []:
                    info = u"开始调用SetParameterValues设置WAN连接使能参数。\n"
                    log.app_info (info)
                    ret_data_scr += info
                    #sleep(3)  # must be ;otherwise exception
                    ret_wan_enable, ret_data_wan_enable = u1.set_parameter_values(ParameterList=WAN_Enable)
                    if (ret_wan_enable == ERR_SUCCESS):
                        info = u"设置WAN连接使能参数成功。\n"
                        log.app_info (info)
                        ret_data_scr += info
                        rebootFlag = int(ret_data_wan_enable["Status"])
                        if (rebootFlag == 1):
                            reboot_Yes = 1
                    else:
                        #对于失败的情况，直接返回错误
                        info = u"设置WAN连接使能参数失败，错误原因：%s 。\n" % ret_data_wan_enable
                        log.app_err (info)
                        ret_data_scr += info
                        return ret_res, ret_data_scr

            else :
                #第三--三步:调用SetParameterValues设置linkconfig参数：
                path2_list = modify_path.split('.')[0:-3]
                path2_1_list = modify_path.split('.')[0:-1]
                
                path2 = '.'.join(path2_list) + '.'
                path2_1 = '.'.join(path2_1_list) + '.'
                
                
                
                #当查到有相匹配的X_CT-COM_ServiceList和Username值时的处理流程，不需要新建,只需更改WANIPConnection或WANPPPConnection节点下的参数即可
                #第三--三步:调用SetParameterValues设置linkconfig参数：
                """
                if DeviceType == 'ADSL':
                    info = u"走X_CT-COM_ServiceList相同的流程(修改WAN连接),开始调用SetParameterValues修改WANDSLLinkConfig参数。\n"
                    path5 = path2 + 'WANDSLLinkConfig.'
                elif DeviceType == 'LAN':
                    info = u"走X_CT-COM_ServiceList相同的流程(修改WAN连接),开始调用SetParameterValues修改WANEthernetLinkConfig参数。\n"
                    path5 = path2 + 'WANEthernetLinkConfig.'
                elif DeviceType == 'EPON':
                    info = u"走X_CT-COM_ServiceList相同的流程(修改WAN连接),开始调用SetParameterValues修改X_CT-COM_WANEponLinkConfig参数。\n"
                    path5 = path2 + 'X_CT-COM_WANEponLinkConfig.'                
                elif DeviceType == 'VDSL':
                    info = u"走X_CT-COM_ServiceList相同的流程(修改WAN连接),开始调用SetParameterValues修改X_CT-COM_WANVdslLinkConfig参数。\n"
                    path5 = path2 + 'X_CT-COM_WANVdslLinkConfig.'
                elif DeviceType == 'GPON':
                    info = u"走X_CT-COM_ServiceList相同的流程(修改WAN连接),开始调用SetParameterValues修改X_CT-COM_WANGponLinkConfig参数。\n"
                    path5 = path2 + 'X_CT-COM_WANGponLinkConfig.'
                else:
                    info = u"走X_CT-COM_ServiceList相同的流程(修改WAN连接),开始调用SetParameterValues修改WANDSLLinkConfig参数。\n"
                    path5 = path2 + 'WANDSLLinkConfig.'
                log.app_info (info)
                ret_data_scr += info
                
                para_list5 = []
                
                for i in dict_wanlinkconfig:
                    if dict_wanlinkconfig[i][0] == 1:
                        #对于Linkconfig的PVC或VLAN节点删除,不做修改
                        # GCW 20130418 修改WAN连接参数时，对X_CT-COM_Mode节点也不修改
                        if i == 'DestinationAddress' or i == 'VLANIDMark' or \
                           i == 'X_CT-COM_VLANIDMark' or i == "X_CT-COM_Mode":
                            continue
                        tmp_path = path5 + i
                        para_list5.append(dict(Name=tmp_path, Value=dict_wanlinkconfig[i][1]))
                if para_list5 == []:
                    info = u"参数列表为空,请检查。\n"
                    log.app_info (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                #sleep(3)  # must be ;otherwise exception
                ret5, ret_data5 = u1.set_parameter_values(ParameterList=para_list5)
                if (ret5 == ERR_SUCCESS):
                    info = u"设置参数成功。\n"
                    log.app_info (info)
                    ret_data_scr += info
                    rebootFlag = int(ret_data5["Status"])
                    if (rebootFlag == 1):
                        reboot_Yes = 1
                else:
                    #对于失败的情况，直接退出
                    info = u"设置参数失败,错误原因：%s 。\n" % ret_data5
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                """
                # 修改SetParameterValues设置WANPPPConnection参数
                if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':
                    tmp_values = dict_wanpppconnection
                    info = u"开始调用SetParameterValues设置WANPPPConnection参数。\n"
                    log.app_info (info)
                    ret_data_scr += info
                else:
                    tmp_values = dict_wanipconnection
                    info = u"开始调用SetParameterValues设置WANIPConnection参数。\n"
                    log.app_info (info)
                    ret_data_scr += info
                
                #第三--四步:调用SetParameterValues设置WANPPPConnection参数：
                path6 = path2_1
                para_list6 = []
                WAN_Enable = []
                
                for i in tmp_values:
                    if tmp_values[i][0] == 1:
                        # GCW 20130408 判断X_CT-COM_ServiceList包含与被包含的关系做区分处理.
                        # 标志位0表示X_CT-COM_ServiceList值需以工单中的为准,重新下发,3表示不下发
                        if WAN_Flag == 0:
                            pass
                        else:
                            if i == 'X_CT-COM_ServiceList':
                                continue
                        #如果WAN连接使能需单独下发,则将使能的动作单独保存
                        if WANEnable_Switch == False and i == 'Enable':
                            WAN_Enable.append(dict(Name=path6 + i, Value=tmp_values[i][1]))
                            continue

                        tmp_path = path6 + i
                        para_list6.append(dict(Name=tmp_path, Value=tmp_values[i][1]))
                if para_list6 == []:
                    return ret_res, ret_data_scr
                
                #sleep(3)  # must be ;otherwise exception
                ret6, ret_data6 = u1.set_parameter_values(ParameterList=para_list6)
                if (ret6 == ERR_SUCCESS):
                    info = u"设置参数成功。\n"
                    log.app_info (info)
                    ret_data_scr += info
                    rebootFlag = int(ret_data6["Status"])
                    if (rebootFlag == 1):
                        reboot_Yes = 1
                else:
                    #对于失败的情况，直接返回失败
                    info = u"设置参数失败，错误原因：%s 。\n" % ret_data6
                    log.app_info (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                    
                #将WAN连接使能单独下发
                if WAN_Enable != []:
                    info = u"开始调用SetParameterValues设置WAN连接使能参数。\n"
                    log.app_info (info)
                    ret_data_scr += info
                    #sleep(3)  # must be ;otherwise exception
                    ret_wan_enable, ret_data_wan_enable = u1.set_parameter_values(ParameterList=WAN_Enable)
                    if (ret_wan_enable == ERR_SUCCESS):
                        info = u"设置WAN连接使能参数成功。\n"
                        log.app_info (info)
                        ret_data_scr += info
                        rebootFlag = int(ret_data_wan_enable["Status"])
                        if (rebootFlag == 1):
                            reboot_Yes = 1
                    else:
                        #对于失败的情况，直接返回错误
                        info = u"设置WAN连接使能参数失败，错误原因：%s 。\n" % ret_data_wan_enable
                        log.app_err (info)
                        ret_data_scr += info
                        return ret_res, ret_data_scr
            # 如果需要重启,则下发Reboot方法,目前采用静等待130S
            if (reboot_Yes == 1):

                #sleep(130)
                ret, ret_data = reboot_wait_next_inform(u1)
                if (ret != ERR_SUCCESS):
                    ret_data_scr += ret_data
                    break
                
            # 第七步：调用修改电信维护密码,目前密码固定为nE7jA%5m
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



def _find_wan_server_and_connecttype(sn_obj,DeviceType,
                                     AccessMode,
                                     dict_wanpppconnection,
                                     dict_wanipconnection,
                                     ret_data_root,
                                     ret_data_scr):
    ret_res = ERR_FAIL
    path2_1_list = []
    
    
    if DeviceType == 'ADSL':
        
        reg_VLAN = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANDSLLinkConfig.DestinationAddress$"
    elif DeviceType == 'LAN':
        
        reg_VLAN = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANEthernetLinkConfig.X_CT-COM_VLANIDMark$"
    elif DeviceType == 'EPON':
        
        reg_VLAN = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.X_CT-COM_WANEponLinkConfig.VLANIDMark$"
    elif DeviceType == 'VDSL':
        
        reg_VLAN = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.X_CT-COM_WANVdslLinkConfig.VLANIDMark$"
    elif DeviceType == 'GPON':
        
        reg_VLAN = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.X_CT-COM_WANGponLinkConfig.VLANIDMark$"
    else:
        
        reg_VLAN = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANDSLLinkConfig.DestinationAddress$"


    if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':
                       
        reg_Username = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANPPPConnection.\d+\.Username$"
        reg_X_CT_COM_ServiceList = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANPPPConnection.\d+\.X_CT-COM_ServiceList$"
        reg_ConnectionType = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANPPPConnection.\d+\.ConnectionType$"
            
    elif AccessMode == 'DHCP' or AccessMode == 'Static':
                        
        reg_Username = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANIPConnection.\d+\.Username$"
        reg_X_CT_COM_ServiceList = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANIPConnection.\d+\.X_CT-COM_ServiceList$"
        reg_ConnectionType = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANIPConnection.\d+\.ConnectionType$"
                    
    ret_pvcorvlan = []
    ret_connectiontype = []
    ret_serverlist = []
    ret_username = []    
    
    pvcorvlan_items = []
    laninterface_items = []   # 保存查询到的serverlist 路径值
    serverlist_items = []     # 保存查询到的serverlist 路径值
    connect_type_items = []   # 保存查询到的connecttype 路径值
    
    for i in xrange(len(ret_data_root['ParameterList'])):
                    
        tmp_path_getvalue = ret_data_root['ParameterList'][i]['Name']
                    
        m_pvcorvlan = re.match(reg_VLAN,tmp_path_getvalue)
        m_username = re.match(reg_Username,tmp_path_getvalue)
        m_serverlist = re.match(reg_X_CT_COM_ServiceList,tmp_path_getvalue)
        m_connectiontype = re.match(reg_ConnectionType,tmp_path_getvalue)
        
        if m_pvcorvlan is not None:
           
            path2_1_list.append(tmp_path_getvalue)
            ret_pvcorvlan.append(tmp_path_getvalue)
        
                   
        if m_username is not None:
           
            path2_1_list.append(tmp_path_getvalue)
            ret_username.append(tmp_path_getvalue)
        if m_serverlist is not None:
            
            path2_1_list.append(tmp_path_getvalue)
            ret_serverlist.append(tmp_path_getvalue)            
        if m_connectiontype is not None:
            
            path2_1_list.append(tmp_path_getvalue)
            ret_connectiontype.append(tmp_path_getvalue)
        
            
    if len(ret_connectiontype) != len(ret_serverlist) and len(ret_connectiontype) != len(ret_username):
        info = u"GetParameterNames查找到WAN连接的X_CT_COM_ServiceList,ConnectionType和Username节点个数不等，工单异常退出。\n"
        log.app_info (info)
        ret_data_scr += info 
        return ret_res,pvcorvlan_items, serverlist_items,connect_type_items,ret_data_scr 
                
    ret_data_getvalue = []
                
    if path2_1_list != []:
                    
        info = u"开始调用GetParameterValues查找WAN连接实例下的VLANID、X_CT_COM_ServiceList,ConnectionType和Username值。\n"
        log.app_info (info)
        ret_data_scr += info
                    
        ret_get_value, ret_data_getvalue = sn_obj.get_parameter_values(ParameterNames=path2_1_list)
                    
        if (ret_get_value == ERR_SUCCESS):
            info = u"查找WAN连接实例下的VLANID、X_CT_COM_ServiceList,ConnectionType和Username值成功。\n" 
            log.app_info (info)
            ret_data_scr += info
                        
        else:
                        
            info = u"获取WAN连接实例下的VLANID、X_CT_COM_ServiceList，ConnectionType和Username值失败，错误信息：%s 。\n" % ret_data_getvalue
            log.app_err (info)
            ret_data_scr += info
            return ret_res, serverlist_items,connect_type_items, laninterface_items,ret_data_scr            
                        
    else:
        pass
                    
    if ret_data_getvalue != []:
                    
        getvalue_list = ret_data_getvalue["ParameterList"]
    else:
        getvalue_list = []
                                           
    for item in getvalue_list:
                            
        tmp_m_serverlist = re.match(reg_X_CT_COM_ServiceList,item['Name'])
        tmp_m_connecttype = re.match(reg_ConnectionType,item['Name'])
        tmp_m_username = re.match(reg_Username,item['Name'])
        tmp_m_pvcorvlan = re.match(reg_VLAN,item['Name'])
        
        if tmp_m_serverlist is not None:
            serverlist_items.append(item)
                            
        if tmp_m_connecttype is not None:
            connect_type_items.append(item)
            
        if tmp_m_username is not None:
            laninterface_items.append(item)
        
        if tmp_m_pvcorvlan is not None:
            pvcorvlan_items.append(item)
                        
    return ERR_SUCCESS,pvcorvlan_items, serverlist_items,connect_type_items,laninterface_items,ret_data_scr

