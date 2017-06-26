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

def IPV6IPTVEnable(obj, sn, WANEnable_Switch, DeviceType,
               AccessMode, PVC_OR_VLAN,
               dict_root, dict_wanlinkconfig,
               dict_wanpppconnection,
               dict_wanipconnection,
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
                info = u"查询WAN连接失败,错误信息:%s 。\n" % ret_data_root
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
            
            path2 = '' # 保存查到有相同的PVC或关键参数值的WAN连接路径
            path2_1 = '' # 保存WANPPPConection或WANIPConection节点路径保存,后面修改参数时有用
            
            for i_pvcorvlan in pvcorvlan_items:
                            
                if i_pvcorvlan['Value'] == PVC_OR_VLAN:
                    WAN_Flag = 0
                    path2 = i_pvcorvlan['Name']
                    break
                else:
                    # 查不到匹配的PVC
                    continue

            # 如果一直没有查到相同的,则没有对WAN_Flag标志位做过修改,则走新建流程
            if WAN_Flag == None:
                WAN_Flag = 1
            
            
            
            # 查不到匹配的PVC或VLAN,则走新建流程,否则还需再查WANPPPConnection节点下的值
            if WAN_Flag == 0:
                
                # 不同的WAN连接模式,其节点路径不同
                if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':
                    
                    # GCW 20130418 应该只区分是路由还是桥接
                    if AccessMode == "PPPoE_Bridged":
                        tmp_ConnectionType = "PPPoE_Bridged"
                    else:
                        tmp_ConnectionType = "IP_Routed"
                    tmp_X_CT_COM_LanInterface =  dict_wanpppconnection['X_CT-COM_LanInterface'][1]
                    tmp_X_CT_COM_ServiceList = dict_wanpppconnection['X_CT-COM_ServiceList'][1]
                    
                elif AccessMode == 'DHCP' or AccessMode == 'Static':
                    
                    # GCW 20130418 应该只区分是路由还是桥接
                    tmp_ConnectionType = "IP_Routed"
                    tmp_X_CT_COM_LanInterface = dict_wanipconnection['X_CT-COM_LanInterface'][1]
                    tmp_X_CT_COM_ServiceList = dict_wanipconnection['X_CT-COM_ServiceList'][1]
                    

                tmp_link_list = path2.split('.')[0:-2]     
                tmp_link_path = '.'.join(tmp_link_list)                # 保存XXXX.WANPPPConnection.i.路径
                
                WAN_Flag_server = 1
                WAN_Flag_connect = 1
                WAN_Flag_interface = 1
                
                if serverlist_items != []:
                    
                    # 查找到pvc及对应连接方式的serverlist,connecttype以及interface
                    #X_CT_COM_ServiceList
                    for i_serverlist in serverlist_items:
                        
                        if tmp_link_path in i_serverlist['Name']:
                            
                            if i_serverlist['Value'] == tmp_X_CT_COM_ServiceList:
                                
                                pass
                            else:
                                tmp_path3_list = i_serverlist['Name'].split('.')[0:-1]     
                                ret_tmp_path3 = '.'.join(tmp_path3_list) + "."
                                
                                WAN_Flag_server = 0
                        
                    # ConnectionType
                    for i_connect_type in connect_type_items:
                        
                        if tmp_link_path in i_connect_type['Name']:
                            
                            if i_connect_type['Value'] == tmp_ConnectionType:
                                
                                pass
                            else:
                                # 路由和桥的区别时，需重新走新建WAN连接流程  GCW 20130506
                                WAN_Flag_connect = 3
                                break
                    
                    # X_CT_COM_LanInterface
                    for i_laninterface in laninterface_items:
                        
                        if tmp_link_path in i_laninterface['Name']:
                            
                            if i_laninterface['Value'] == tmp_X_CT_COM_LanInterface:
                                
                                pass
                            else:
                                tmp_path3_list = i_laninterface['Name'].split('.')[0:-1]     
                                ret_tmp_path3 = '.'.join(tmp_path3_list) + "."
                                WAN_Flag_interface = 0
                else:
                    # 查找到pvc但是没有对应连接方式的serverlist,connecttype以及interface，此时需要走新建流程
                    WAN_Flag_connect = 3
                
                if WAN_Flag_connect != 3:
                                    
                    #如果有一个不匹配,则修改WANPPPConnection节点下的值
                    if WAN_Flag_interface == 0 or WAN_Flag_server == 0:
                        #对于查到是INTERNET,而待下发的是OTHER的话,贝曼的处理是重新修改为"INTERNET,OTHER"
                        # GCW 20130401 以下处理虽然符合贝曼,但不合理.重新定义为以传参为准.
                        #for j in xrange(3):
                        #    if 'X_CT-COM_ServiceList' in ret_data3_2['ParameterList'][j]['Name'].split("."):
                        #        if ret_data3_2['ParameterList'][j]['Value'] != tmp_X_CT_COM_ServiceList:
                        #            tmp_X_CT_COM_ServiceList = 'INTERNET,OTHER'
                        
                        
                        info = u"查找到匹配的PVC（VLAN）但参数不匹配，走修改WAN连接。\n"
                        log.app_info (info)
                        ret_data_scr += info
                        
                        
                        if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':
                            tmp_values = dict_wanpppconnection
                            info = u"查询到的值与用户工单中传参过来的有不相等情况,开始调用SetParameterValues修改参数。\n"
                        else:
                            tmp_values = dict_wanipconnection
                            info = u"查询到的值与用户工单中传参过来的有不相等情况,开始调用SetParameterValues修改参数。\n"
                        log.app_info (info)
                        ret_data_scr += info
                        
                        #第三--四步:调用SetParameterValues设置WANPPPConnection参数：
                        # 同时下发IGMP参数；
                        path6 = ret_tmp_path3
                        para_list6 = []
                        WAN_Enable = []
                        for j in tmp_values:
                            if tmp_values[j][0] == 1:
                                #如果WAN连接使能需单独下发,则将使能的动作单独保存
                                if WANEnable_Switch == False and j == 'Enable':
                                    WAN_Enable.append(dict(Name=path6 + j, Value=tmp_values[j][1]))
                                    continue
                                
                                tmp_path = path6 + j
                                # 如果是X_CT-COM_ServiceList,则用修改后的值
                                if (j == 'X_CT-COM_ServiceList'):
                                    para_list6.append(dict(Name=tmp_path, Value=tmp_X_CT_COM_ServiceList))
                                else:
                                    para_list6.append(dict(Name=tmp_path, Value=tmp_values[j][1]))
                        
                        # IGMP参数
                        path = 'InternetGatewayDevice.Services.X_CT-COM_IPTV.'
                        for i in dict_root:
                            if dict_root[i][0] == 1:
                                tmp_path = path + i
                                para_list6.append(dict(Name=tmp_path, Value=dict_root[i][1]))
                        
                        if para_list6 == []:
                            info = u"参数为空,请检查。\n"
                            log.app_err (info)
                            ret_data_scr += info
                            return ret_res, ret_data_scr

                        #sleep(3)  # must be ;otherwise exception
                        ret6, ret_data6 = u1.set_parameter_values(ParameterList=para_list6)
                        if (ret6 == ERR_SUCCESS):
                            info = u"修改参数成功。\n"
                            log.app_info (info)
                            ret_data_scr += info
                            rebootFlag = int(ret_data6["Status"])
                            if (rebootFlag == 1):
                                reboot_Yes = 1
                        else:
                            #对于失败的情况，直接返回失败
                            info = u"修改参数失败，错误原因：%s 。\n" % ret_data6
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
                                #对于失败的情况，如何处理?
                                info = u"设置WAN连接使能参数失败，错误原因：%s 。\n" % ret_data_wan_enable
                                log.app_err (info)
                                ret_data_scr += info
                                return ret_res, ret_data_scr
                    else:
                        info = u"查询到的值与用户工单中传参过来的相等,无需修改WAN连接参数 。\n"
                        log.app_info (info)
                        ret_data_scr += info
                        
                else :
                    WAN_Flag = 1   # 重置WAN_Flag标志位，走新建WAN连接流程
                

            if WAN_Flag == 1:
                #第三--一步：新建WANConnectionDevice实例
                info = u"查不到匹配的PVC（VLAN）、或ConnectionType（模式）不匹配，走新建WAN连接。\n"
                log.app_info (info)
                ret_data_scr += info
                
                info = u"开始调用AddObject新建WANConnectionDevice实例。\n"
                log.app_info (info)
                ret_data_scr += info
                
                Classpath = ROOT_PATH
                #sleep(3)  # must be ;otherwise exception
                ret3, ret_data3 = u1.add_object(
                                    ObjectName=Classpath)
                if (ret3 == ERR_SUCCESS):
                    instanceNum1 = ret_data3["InstanceNumber"]
                    info = u"新建实例成功,返回实例号：%s 。\n" % instanceNum1
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
                    info = u"新建实例失败，错误原因：%s 。\n" % ret_data3
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                
                #第三--二步：新建WANIPConnection或WANPPPConnection实例
                #只有是桥模式和路由PPPOE时,才新建WANPPPConnection实例.暂时不考虑桥
                if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':
                    path4 = ROOT_PATH + instanceNum1 + '.WANPPPConnection.'
                    info = u"开始调用AddObject新建WANPPPConnection实例。\n"
                    log.app_info (info)
                    ret_data_scr += info
                else:
                    path4 = ROOT_PATH + instanceNum1 + '.WANIPConnection.'
                    info = u"开始调用AddObject新建WANIPConnection实例。\n"
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
                    #对于失败的情况，直接退出
                    info = u"新建实例失败，错误原因：%s 。\n" % ret_data4
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                
                #第三--三步:调用SetParameterValues设置linkconfig参数：

                if DeviceType == 'ADSL':
                    path5 = tmp_path3 + 'WANDSLLinkConfig.'
                    info = u"开始调用SetParameterValues设置WANDSLLinkConfig，WANPPPConnection（或WANIPConnection）及IGMP参数。\n"
                elif DeviceType == 'LAN':
                    path5 = tmp_path3 + 'WANEthernetLinkConfig.'
                    info = u"开始调用SetParameterValues设置WANEthernetLinkConfig，WANPPPConnection（或WANIPConnection）及IGMP参数。\n"
                elif DeviceType == 'EPON':
                    path5 = tmp_path3 + 'X_CT-COM_WANEponLinkConfig.'
                    info = u"开始调用SetParameterValues设置X_CT-COM_WANEponLinkConfig，WANPPPConnection（或WANIPConnection）及IGMP参数。\n"
                elif DeviceType == 'VDSL':
                    path5 = tmp_path3 + 'WANDSLLinkConfig.'
                    info = u"开始调用SetParameterValues设置VDSL/ADSL兼容网关的WANDSLLinkConfig，WANPPPConnection（或WANIPConnection）及IGMP参数。\n"
                elif DeviceType == 'GPON':
                    path5 = tmp_path3 + 'X_CT-COM_WANGponLinkConfig.'
                    info = u"开始调用SetParameterValues设置X_CT-COM_WANGponLinkConfig，WANPPPConnection（或WANIPConnection）及IGMP参数。\n"
                else:
                    path5 = tmp_path3 + 'WANDSLLinkConfig.'
                    info = u"开始调用SetParameterValues设置WANDSLLinkConfig，WANPPPConnection（或WANIPConnection）及IGMP参数。\n"
                log.app_info (info)
                ret_data_scr += info
                
                # 添加link层
                para_list5 = []
                for i in dict_wanlinkconfig:
                    if dict_wanlinkconfig[i][0] == 1:
                        tmp_path = path5 + i
                        para_list5.append(dict(Name=tmp_path, Value=dict_wanlinkconfig[i][1]))
                if para_list5 == []:
                    info = u"参数为空,请检查。\n"
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                #sleep(3)  # must be ;otherwise exception
                
                # 添加ppp或ip层
                if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':
                    tmp_values = dict_wanpppconnection
                    
                else:
                    tmp_values = dict_wanipconnection
                    
                path6 = tmp_path4 + '.'
                
                WAN_Enable = []
                for i in tmp_values:
                    if tmp_values[i][0] == 1:
                        #如果WAN连接使能需单独下发,则将使能的动作单独保存
                        if WANEnable_Switch == False and i == 'Enable':
                            WAN_Enable.append(dict(Name=path6 + i, Value=tmp_values[i][1]))
                            continue
                        
                        tmp_path = path6 + i
                        para_list5.append(dict(Name=tmp_path, Value=tmp_values[i][1]))
                
                # 添加IGMP
                # IGMP参数
                path = 'InternetGatewayDevice.Services.X_CT-COM_IPTV.'
                for i in dict_root:
                    if dict_root[i][0] == 1:
                        tmp_path = path + i
                        para_list5.append(dict(Name=tmp_path, Value=dict_root[i][1]))
                
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
        
        reg_VLAN = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANDSLLinkConfig.X_CT-COM_VLAN$"
    elif DeviceType == 'GPON':
        
        reg_VLAN = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.X_CT-COM_WANGponLinkConfig.VLANIDMark$"
    else:
        
        reg_VLAN = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANDSLLinkConfig.DestinationAddress$"


    if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':
                       
        reg_LanInterface = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANPPPConnection.\d+\.X_CT-COM_LanInterface$"
        reg_X_CT_COM_ServiceList = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANPPPConnection.\d+\.X_CT-COM_ServiceList$"
        reg_ConnectionType = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANPPPConnection.\d+\.ConnectionType$"
            
    elif AccessMode == 'DHCP' or AccessMode == 'Static':
                        
        reg_LanInterface = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANIPConnection.\d+\.X_CT-COM_LanInterface$"
        reg_X_CT_COM_ServiceList = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANIPConnection.\d+\.X_CT-COM_ServiceList$"
        reg_ConnectionType = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANIPConnection.\d+\.ConnectionType$"
                    
    ret_pvcorvlan = []
    ret_connectiontype = []
    ret_serverlist = []
    ret_laninterface = []    
    
    pvcorvlan_items = []
    laninterface_items = []   # 保存查询到的serverlist 路径值
    serverlist_items = []     # 保存查询到的serverlist 路径值
    connect_type_items = []   # 保存查询到的connecttype 路径值
    
    for i in xrange(len(ret_data_root['ParameterList'])):
                    
        tmp_path_getvalue = ret_data_root['ParameterList'][i]['Name']
                    
        m_pvcorvlan = re.match(reg_VLAN,tmp_path_getvalue)
        m_laninterface = re.match(reg_LanInterface,tmp_path_getvalue)
        m_serverlist = re.match(reg_X_CT_COM_ServiceList,tmp_path_getvalue)
        m_connectiontype = re.match(reg_ConnectionType,tmp_path_getvalue)
        
        if m_pvcorvlan is not None:
           
            path2_1_list.append(tmp_path_getvalue)
            ret_pvcorvlan.append(tmp_path_getvalue)
        
                   
        if m_laninterface is not None:
           
            path2_1_list.append(tmp_path_getvalue)
            ret_laninterface.append(tmp_path_getvalue)
        if m_serverlist is not None:
            
            path2_1_list.append(tmp_path_getvalue)
            ret_serverlist.append(tmp_path_getvalue)            
        if m_connectiontype is not None:
            
            path2_1_list.append(tmp_path_getvalue)
            ret_connectiontype.append(tmp_path_getvalue)
        
            
    if len(ret_connectiontype) != len(ret_serverlist) and len(ret_connectiontype) != len(ret_laninterface):
        info = u"GetParameterNames查找到WAN连接的X_CT_COM_ServiceList,ConnectionType和X_CT-COM_LanInterface节点个数不等，工单异常退出。\n"
        log.app_info (info)
        ret_data_scr += info 
        return ret_res,pvcorvlan_items, serverlist_items,connect_type_items,ret_data_scr 
                
    ret_data_getvalue = []
                
    if path2_1_list != []:
                    
        info = u"开始调用GetParameterValues查找WAN连接实例下的VLANID、X_CT_COM_ServiceList,ConnectionType和X_CT-COM_LanInterface值。\n"
        log.app_info (info)
        ret_data_scr += info
                    
        ret_get_value, ret_data_getvalue = sn_obj.get_parameter_values(ParameterNames=path2_1_list)
                    
        if (ret_get_value == ERR_SUCCESS):
            info = u"查找WAN连接实例下的VLANID、X_CT_COM_ServiceList,ConnectionType和X_CT-COM_LanInterface值成功。\n" 
            log.app_info (info)
            ret_data_scr += info
                        
        else:
                        
            info = u"获取WAN连接实例下的VLANID、X_CT_COM_ServiceList，ConnectionType和X_CT-COM_LanInterface值失败，错误信息：%s 。\n" % ret_data_getvalue
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
        tmp_m_laninterface = re.match(reg_LanInterface,item['Name'])
        tmp_m_pvcorvlan = re.match(reg_VLAN,item['Name'])
        
        if tmp_m_serverlist is not None:
            serverlist_items.append(item)
                            
        if tmp_m_connecttype is not None:
            connect_type_items.append(item)
            
        if tmp_m_laninterface is not None:
            laninterface_items.append(item)
        
        if tmp_m_pvcorvlan is not None:
            pvcorvlan_items.append(item)
                        
    return ERR_SUCCESS,pvcorvlan_items, serverlist_items,connect_type_items,laninterface_items,ret_data_scr

