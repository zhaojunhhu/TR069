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

def V6WANSetUP(obj,sn, WANEnable_Switch, DeviceType,
             AccessMode1, PVC_OR_VLAN,AccessMode2='',
             dict_wanlinkconfig={},
             dict_wanpppconnection1={},
             dict_wanipconnection1={},
             dict_wanpppconnection2={},
             dict_wanipconnection2={},
             dict_v6config={},
             dict_v6prefixinformation={},
             dict_dhcpv6server={},
             dict_routeradvertisement={},
             change_account=1,
             rollbacklist=[]):
    ret_res = ERR_FAIL # 返回成功或失败
    ret_data_scr = "" # 返回结果日志

    ROOT_PATH = "InternetGatewayDevice.WANDevice.1.WANConnectionDevice."
    for nwf in [1]:
        try:
            u1=User(sn, ip=worklistcfg.AGENT_HTTP_IP, port=worklistcfg.AGENT_HTTP_PORT, page=worklistcfg.WORKLIST2AGENT_PAGE, sender=KEY_SENDER_WORKLIST, worklist_id=obj.id_)
            reboot_Yes = 0
            
            # 以下两个步骤工单流程中有，但是查询的结果后续步骤没使用，暂且保留 shenlige 2013-11-6
            DeviceInfo_Root_Path = "InternetGatewayDevice.DeviceInfo."
            
            info = u"开始调用GetParameterNames方法，查询DeviceInfo信息。\n"
            log.app_info (info)
            ret_data_scr += info
            ret_device_info, ret_data_device_info = u1.get_parameter_names(ParameterPath=DeviceInfo_Root_Path, NextLevel=0)
            
            if (ret_device_info == ERR_SUCCESS):
                info = u"查询DeviceInfo信息成功。\n"
                log.app_info (info)
                ret_data_scr += info
                ret_data_device_info = DelOwnParameterNames(ret_data_device_info, DeviceInfo_Root_Path)
            else:
                #对于失败的情况，直接返回失败
                info = u"查询DeviceInfo信息失败,错误信息:%s 。\n" % ret_data_device_info
                log.app_err (info)
                ret_data_scr += info
                return ret_res, ret_data_scr
            
            InterfaceVersion_Path = ""
            for i in xrange(len(ret_data_device_info['ParameterList'])):
                
                tmp_path = ret_data_device_info['ParameterList'][i]['Name']
                if tmp_path == "InternetGatewayDevice.DeviceInfo.X_CT-COM_InterfaceVersion":
                    InterfaceVersion_Path = tmp_path
                    break
            
            if InterfaceVersion_Path != "":
                info = u"开始调用GetParameterValues方法，查询接口版本号。\n"
                log.app_info(info)
                ret_data_scr += info
                
                ret_interface_version, ret_data_interface_version = u1.get_parameter_values(ParameterNames=InterfaceVersion_Path)
                
                if (ret_interface_version == ERR_SUCCESS):
                    interface_version = ret_data_interface_version["ParameterList"][0]['Value']
                    info = u"查询接口版本号成功 %s 。\n" % interface_version
                    log.app_info(info)
                    ret_data_scr += info
                else:
                    info = u"查询接口版本号失败,错误信息:%s 。\n" % ret_data_interface_version
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
            
            # 设置IPV6功能启用
            
            IPProtocolVersion_Path = "InternetGatewayDevice.DeviceInfo.X_CT-COM_IPProtocolVersion.Mode"
            
            info = u"开始调用SetParameterValues方法，启用IPv6功能。\n"
            para_list_ipversion = []    
            para_list_ipversion.append(dict(Name=IPProtocolVersion_Path, Value="3"))
            ret_ipversion, ret_data_ipversion = u1.set_parameter_values(ParameterList=para_list_ipversion)
            
            if (ret_ipversion == ERR_SUCCESS):
                info = u"启用IPv6功能成功。\n"
                log.app_info (info)
                ret_data_scr += info
                rebootFlag = int(ret_data_ipversion["Status"])
                if (rebootFlag == 1):
                    reboot_Yes = 1
            else:
                #对于失败的情况，直接返回失败
                info = u"启用IPv6功能失败，错误原因：%s 。\n" % ret_data_ipversion
                log.app_err (info)
                ret_data_scr += info
                return ret_res, ret_data_scr
            
            #获取IPv6 LAN 测PrefixInformation
            PrefixInformation_Path = "InternetGatewayDevice.LANDevice.1.X_CT-COM_IPv6Config.PrefixInformation."
            info = u"开始调用GetParameterNames方法，查询PrefixInformation信息。\n"
            log.app_info (info)
            ret_data_scr += info
            ret_prefix_info, ret_data_prefix_info = u1.get_parameter_names(ParameterPath=PrefixInformation_Path, NextLevel=0)
            
            if (ret_prefix_info == ERR_SUCCESS):
                info = u"查询PrefixInformation信息成功。\n"
                log.app_info (info)
                ret_data_scr += info
                ret_data_prefix_info = DelOwnParameterNames(ret_data_prefix_info, PrefixInformation_Path)
            else:
                #对于失败的情况，直接返回失败
                info = u"查询PrefixInformation信息失败,错误信息:%s 。\n" % ret_data_prefix_info
                log.app_err (info)
                ret_data_scr += info
                return ret_res, ret_data_scr
            
            # 获取支持的RPC方法
            info = u"开始调用GetRPCMethods方法，获取所支持的RPC方法"
            ret_rpc, ret_data_rpc = u1.get_rpc_methods()       
            if ret_rpc == ERR_SUCCESS:
                info = u'调用GetRPCMethods方法成功。\n' 
                log.user_info(info)
                ret_data_scr += info
                rpc_methods = ret_data_rpc["MethodsList"]
                
            else:
                info = u'调用GetRPCMethods方法失败，详细信息为：%s 。\n' % ret_data_rpc
                log.app_err (info)
                ret_data_scr += info
                return ret_res, ret_data_scr      

              
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
                info = u"查询WAN连接失败,错误信息:%s\n" % ret_data_root
                log.app_err (info)
                ret_data_scr += info
                return ret_res, ret_data_scr
            
            
            #第二步：逐个查找
            
            #保存WANPPPConection或WANIPConection节点路径保存,后面修改参数时有用
            # 是否有查到已存在的类似WAN连接的状态位,符合以下标识,桥只关心PVC,其他的只关心X_CT-COM_ServiceList
            
            X_CT_COM_ServiceList1 = None
            X_CT_COM_ServiceList2 = None
            
            #如果是桥连接,则只查PVC,其他的查X_CT-COM_ServiceList是否有相同的
            if AccessMode1 == 'PPPoE' or AccessMode1 == 'DHCP' or AccessMode1 == 'Static' or AccessMode1 == 'PPPoE_Bridged':
                #注意是调GetParameterNames,不同于桥时直接调GetParameterValues查值
                
                if AccessMode1 == 'PPPoE' or AccessMode1 == 'PPPoE_Bridged':
                       
                    reg_Username1 = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANPPPConnection.\d+\.Username"
                    reg_X_CT_COM_ServiceList1 = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANPPPConnection.\d+\.X_CT-COM_ServiceList"
                    reg_ConnectionType1 = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANPPPConnection.\d+\.ConnectionType"
                    
                    X_CT_COM_ServiceList1 = dict_wanpppconnection1['X_CT-COM_ServiceList'][1]
                     
                elif AccessMode1 == 'DHCP' or AccessMode1 == 'Static':
                        
                    reg_Username1 = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANIPConnection.\d+\.Username"
                    reg_X_CT_COM_ServiceList1 = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANIPConnection.\d+\.X_CT-COM_ServiceList"
                    reg_ConnectionType1 = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANIPConnection.\d+\.ConnectionType"
                    
                    X_CT_COM_ServiceList1 = dict_wanipconnection1['X_CT-COM_ServiceList'][1]
                    
                ret_find, serverlist_items1,connect_type_items1,ret_data_find = _find_wan_server_and_connecttype(u1,
                                     AccessMode1,
                                     dict_wanpppconnection1,
                                     dict_wanipconnection1,
                                     ret_data_root,
                                     ret_data_scr)
                
                if ret_find == ERR_SUCCESS:
                    ret_data_scr = ret_data_find
                else:
                    ret_data_scr = ret_data_find
                    return ret_res, ret_data_find
                
                if AccessMode1 == "PPPoE_Bridged":
                    ConnectionType1 = "PPPoE_Bridged"
                else:
                    ConnectionType1 = "IP_Routed"
                
            else:
                info = u"输入的AccessMode1参数不合法,请检查!\n"
                log.app_info (info)
                ret_data_scr += info
                return ret_res, ret_data_scr
            
            
            if AccessMode2 != '':
                if AccessMode2 == 'PPPoE' or AccessMode2 == 'DHCP' or AccessMode2 == 'Static' or AccessMode2 == 'PPPoE_Bridged':
                #注意是调GetParameterNames,不同于桥时直接调GetParameterValues查值
                
                    if AccessMode2 == 'PPPoE' or AccessMode2 == 'PPPoE_Bridged':
                       
                        reg_Username2 = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANPPPConnection.\d+\.Username"
                        reg_X_CT_COM_ServiceList2 = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANPPPConnection.\d+\.X_CT-COM_ServiceList"
                        reg_ConnectionType2 = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANPPPConnection.\d+\.ConnectionType"
                    
                        X_CT_COM_ServiceList2 = dict_wanpppconnection2['X_CT-COM_ServiceList'][1]
                     
                    elif AccessMode2 == 'DHCP' or AccessMode2 == 'Static':
                        
                        reg_Username2 = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANIPConnection.\d+\.Username"
                        reg_X_CT_COM_ServiceList2 = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANIPConnection.\d+\.X_CT-COM_ServiceList"
                        reg_ConnectionType1 = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANIPConnection.\d+\.ConnectionType"
                    
                        X_CT_COM_ServiceList2 = dict_wanipconnection2['X_CT-COM_ServiceList'][1]
                    
                    ret_find, serverlist_items2,connect_type_items2,ret_data_find = _find_wan_server_and_connecttype(u1,
                                     AccessMode2,
                                     dict_wanpppconnection2,
                                     dict_wanipconnection2,
                                     ret_data_root,
                                     ret_data_scr)
                
                    if ret_find == ERR_SUCCESS:
                        ret_data_scr = ret_data_find
                    else:
                        ret_data_scr = ret_data_find
                        return ret_res, ret_data_find
                
                    if AccessMode2 == "PPPoE_Bridged":
                        ConnectionType2 = "PPPoE_Bridged"
                    else:
                        ConnectionType2 = "IP_Routed"
                
                else:
                    info = u"输入的AccessMode1参数不合法,请检查!\n"
                    log.app_info (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
    
            modify_path_1 = None
            modify_path_2 = None
                
            WAN1_Flag = None
            WAN2_Flag = None
                
            for i_connect in connect_type_items1:
                            
                tmp_ppp_list = i_connect['Name'].split('.')[0:-1]     
                tmp_ppp_path = '.'.join(tmp_ppp_list)                # 保存XXXX.WANPPPConnection.i.路径
                    
                # 确定WAN1，是否修改
                for j_serverlist in serverlist_items1:
                        
                    tmp_serverlist = j_serverlist['Name']            
                        
                    # 同一条WAN连接下进行比较
                    if tmp_ppp_path in tmp_serverlist:
                            
                        # 桥对桥，路由对路由            
                        if ConnectionType1 in i_connect['Value']:
                                            
                            if X_CT_COM_ServiceList1 in j_serverlist['Value'] or j_serverlist['Value'] in X_CT_COM_ServiceList1:
                                    
                                modify_path_1 = j_serverlist['Name']
                                if j_serverlist['Value'] in X_CT_COM_ServiceList1:
                                                    
                                    info = u"当前CPE中的X_CT-COM_ServiceList值包含于工单中要求的X_CT-COM_ServiceList值:%s,\n" % X_CT_COM_ServiceList1
                                    info += u"走修改WAN连接的流程,且重新下发X_CT-COM_ServiceList值的修改。\n"
                                    log.app_info (info)
                                    ret_data_scr += info
                                    WAN1_Flag = 1 
                                else:
                                    info = u"当前工单中的X_CT-COM_ServiceList值：%s包含于CPE中的X_CT-COM_ServiceList值，\n" % X_CT_COM_ServiceList1
                                    info += u"走修改WAN连接流程,但不下发对X_CT-COM_ServiceList值的修改。\n"
                                    log.app_info (info)
                                    ret_data_scr += info
                                    WAN1_Flag = 2
                                            
                                break
                                               
                            else:
                                continue
                
                
            if X_CT_COM_ServiceList2 != None:
                    
                for i_connect in connect_type_items2:
                            
                    tmp_ppp_list = i_connect['Name'].split('.')[0:-1]     
                    tmp_ppp_path = '.'.join(tmp_ppp_list)                # 保存XXXX.WANPPPConnection.i.路径
                    
                    # 确定WAN2，是否修改
                    for j_serverlist in serverlist_items2:
                        
                        tmp_serverlist = j_serverlist['Name']            
                        
                        # 同一条WAN连接下进行比较
                        if tmp_ppp_path in tmp_serverlist:
                            
                            # 桥对桥，路由对路由            
                            if ConnectionType2 in i_connect['Value']:
                                            
                                if X_CT_COM_ServiceList2 in j_serverlist['Value'] or j_serverlist['Value'] in X_CT_COM_ServiceList2:
                                    
                                    modify_path_2 = j_serverlist['Name']
                                    if j_serverlist['Value'] in X_CT_COM_ServiceList2:
                                                    
                                        info = u"当前CPE中的X_CT-COM_ServiceList值包含于工单中要求的X_CT-COM_ServiceList值:%s,\n" % X_CT_COM_ServiceList2
                                        info += u"走修改WAN连接的流程,且重新下发X_CT-COM_ServiceList值的修改。\n"
                                        log.app_info (info)
                                        ret_data_scr += info
                                        WAN2_Flag = 1 
                                    else:
                                        info = u"当前工单中的X_CT-COM_ServiceList值：%s包含于CPE中的X_CT-COM_ServiceList值，\n" % X_CT_COM_ServiceList2
                                        info += u"走修改WAN连接流程,但不下发对X_CT-COM_ServiceList值的修改。\n"
                                        log.app_info (info)
                                        ret_data_scr += info
                                        WAN2_Flag = 2
                                            
                                    break
                                               
                                else:
                                    continue
                        
            # 分情况讨论：
            # 1 个 vlan下一条WAN连接
            # 1 个 vlan下两条WAN连接
            
            # 1个vlan下一条WAN连接
            if not X_CT_COM_ServiceList2:
                
                if WAN1_Flag == None:
                    
                    info = u"查找不到匹配 %s 模式的WAN连接，走新建流程。\n" % X_CT_COM_ServiceList1
                    log.app_info (info)
                    ret_data_scr += info
                    
                    # 解决用户新建tr069WAN连接导致CPE与ACS通讯异常的问题,强制不准新建包含TR0069的WAN连接
                
                    if (("tr069" in X_CT_COM_ServiceList1) or
                        ("TR069" in X_CT_COM_ServiceList1)):
                        info = u"工单失败:为避免新建包含tr069模式的WAN连接对原有tr069WAN连接产生影响,所以不再新建。\n"
                        log.app_info (info)
                        ret_data_scr += info
                        return ret_res, ret_data_scr
                
                    info = u"开始调用AddObject新建WANConnectionDevice实例。\n"
                    log.app_info (info)
                    ret_data_scr += info
                
                    Classpath = ROOT_PATH
                    #sleep(3)  # must be ;otherwise exception
                    ret3, ret_data3 = u1.add_object(
                                    ObjectName=Classpath)
                    
                    if (ret3 == ERR_SUCCESS):
                        instanceNum1 = ret_data3["InstanceNumber"]
                        info = u"新建WANConnectionDevice实例成功,返回实例号：%s 。\n" % instanceNum1
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
                        info = u"新建WANConnectionDevice实例失败，错误原因：%s 。\n" % ret_data3
                        log.app_err (info)
                        ret_data_scr += info
                        return ret_res, ret_data_scr
                
                    #第三--二步：新建WANIPConnection或WANPPPConnection实例
                    #只有是桥模式和路由PPPOE时,才新建WANPPPConnection实例
                    if AccessMode1 == 'PPPoE' or AccessMode1 == 'PPPoE_Bridged':
                        path4 = ROOT_PATH + instanceNum1 + '.WANPPPConnection.'
                        info = u"开始调用AddObject新建WAN连接的WANPPPConnection实例。\n"
                    else:
                        path4 = ROOT_PATH + instanceNum1 + '.WANIPConnection.'
                        info = u"开始调用AddObject新建WAN连接的WANIPConnection实例。\n"
                
                    log.app_info (info)
                    ret_data_scr += info
                
                    #sleep(3)  # must be ;otherwise exception
                    ret4, ret_data4 = u1.add_object(
                                    ObjectName=path4)
                
                    if (ret4 == ERR_SUCCESS):
                        instanceNum1_1 = ret_data4["InstanceNumber"]
                        tmp_path4 = path4 + instanceNum1_1
                        info = u"新建实例成功,返回实例号：%s 。\n" % instanceNum1_1
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
                
                    #第三--三步:调用SetParameterValues设置linkconfig参数：

                    ret5, ret_data5,reboot_Yes = _set_link_parameter_values(u1,DeviceType,tmp_path3,
                                                                         dict_wanlinkconfig,
                                                                         ret_data_scr,True)
                    if ret5 == ERR_SUCCESS:
                        ret_data_scr = ret_data5
                    else:
                        ret_data_scr = ret_data5
                        return ret_res, ret_data_scr
                    
                    #第三--四步:调用SetParameterValues设置WANPPPConnection参数：
                    if AccessMode1 == 'PPPoE' or AccessMode1 == 'PPPoE_Bridged':
                        tmp_values1 = dict_wanpppconnection1
                        info = u"开始调用SetParameterValues设置WANPPPConnection参数。\n"
                    else:
                        tmp_values1 = dict_wanipconnection1
                        info = u"开始调用SetParameterValues设置WANIPConnection参数。\n"
                    
                    log.app_info (info)
                    ret_data_scr += info
                
                    #第三--四步:调用SetParameterValues设置WANPPPConnection参数：
                    path6 = tmp_path4 + '.'
                    para_list6 = []
                    WAN_Enable = []
                    
                    ret6_1, ret_data6_1,reboot_Yes,WAN_Enable = _set_ppporip_para(u1,tmp_values1,path6,
                                                                       ret_data_scr,WAN1_Flag, WANEnable_Switch,WAN_Enable)
                    
                    if ret6_1 == ERR_SUCCESS:
                        ret_data_scr = ret_data6_1
                    else:
                        ret_data_scr = ret_data6_1
                        return ret_res, ret_data_scr
                    
                    v6config_path = path6
                    # 设置六v6相关配置
                    if dict_v6config != {}:
                        ret_v6, ret_data_v6, reboot_Yes = _ipv6_config(u1,ret_data_prefix_info,
                                                dict_v6prefixinformation,
                                                dict_v6config,
                                                dict_dhcpv6server,
                                                dict_routeradvertisement,
                                                v6config_path,
                                                ret_data_scr)
            
                        if ret_v6 == ERR_SUCCESS:
                            ret_data_scr = ret_data_v6
                        else:
                            ret_data_scr = ret_data_v6
                            return ret_res, ret_data_scr
                    
                    # 将WAN连接使能单独下发
                    ret_wan_enable, ret_data_wan_enable, reboot_Yes= _wan_enable(u1,WAN_Enable,ret_data_scr)
                    
                    if ret_wan_enable == ERR_SUCCESS:
                        ret_data_scr = ret_data_wan_enable
                    else:
                        ret_data_scr = ret_data_wan_enable
                        return ret_res, ret_data_scr
                
                # 修改WAN连接流程
                else:
                    #第三--三步:调用SetParameterValues设置linkconfig参数：
                    path2_list = modify_path_1.split('.')[0:-3]
                    path2_1_list = modify_path_1.split('.')[0:-1]
                    
                    path2 = '.'.join(path2_list) + '.'
                    path2_1 = '.'.join(path2_1_list) + '.'
                    
                    # 修改Link层配置
                    if AccessMode1 != 'PPPoE_Bridged':
                        ret5, ret_data5,reboot_Yes = _set_link_parameter_values(u1,DeviceType,path2,
                                                                         dict_wanlinkconfig,
                                                                         ret_data_scr)
                        if ret5 == ERR_SUCCESS:
                            ret_data_scr = ret_data5
                        else:
                            ret_data_scr = ret_data5
                            return ret_res, ret_data_scr
                    
                    # 修改SetParameterValues设置WANPPPConnection参数
                    if AccessMode1 == 'PPPoE' or AccessMode1 == 'PPPoE_Bridged':
                        tmp_values1 = dict_wanpppconnection1
                        info = u"开始调用SetParameterValues设置WANPPPConnection参数。\n"
                        log.app_info (info)
                        ret_data_scr += info
                    else:
                        tmp_values1 = dict_wanipconnection1
                        info = u"开始调用SetParameterValues设置WANIPConnection参数。\n"
                        log.app_info (info)
                        ret_data_scr += info
                
                    #第三--四步:调用SetParameterValues设置WANPPPConnection参数：
                    path6 = path2_1
                    para_list6 = []
                    WAN_Enable = []
                    
                    ret6_1, ret_data6_1,reboot_Yes,WAN_Enable = _set_ppporip_para(u1,tmp_values1,path6,
                                                                       ret_data_scr,WAN1_Flag, WANEnable_Switch,WAN_Enable)
                    
                    if ret6_1 == ERR_SUCCESS:
                        ret_data_scr = ret_data6_1
                    else:
                        ret_data_scr = ret_data6_1
                        return ret_res, ret_data_scr
                    
                    v6config_path = path6
                    # 设置六v6相关配置
                    # 设置六v6相关配置
                    if dict_v6config != {}:
                        ret_v6, ret_data_v6, reboot_Yes = _ipv6_config(u1,ret_data_prefix_info,
                                                dict_v6prefixinformation,
                                                dict_v6config,
                                                dict_dhcpv6server,
                                                dict_routeradvertisement,
                                                v6config_path,
                                                ret_data_scr)
            
                        if ret_v6 == ERR_SUCCESS:
                            ret_data_scr = ret_data_v6
                        else:
                            ret_data_scr = ret_data_v6
                            return ret_res, ret_data_scr
                    
                    # 将WAN连接使能单独下发
                    ret_wan_enable, ret_data_wan_enable,reboot_Yes = _wan_enable(u1,WAN_Enable,ret_data_scr)
                    
                    if ret_wan_enable == ERR_SUCCESS:
                        ret_data_scr = ret_data_wan_enable
                    else:
                        ret_data_scr = ret_data_wan_enable
                        return ret_res, ret_data_scr
            
            else:
                
                # 该标志为1，表示需要修改一条ppp或ip连接的值，另外需要增加一条连接
                # 该标志为2，表示一条vlan下面有两条wan连接，而且两条的serverlist均相同，走修改的流程
                One_VlanID_Two_WAN_Flag = None
                
                # 两条全部都是新建
                if WAN1_Flag == None and WAN2_Flag == None:
                    
                    info = u"查找不到匹配 %s 模式的WAN连接，走新建流程。\n" % X_CT_COM_ServiceList1
                    log.app_info (info)
                    ret_data_scr += info
                    
                    # 解决用户新建tr069WAN连接导致CPE与ACS通讯异常的问题,强制不准新建包含TR0069的WAN连接
                
                    if (("tr069" in X_CT_COM_ServiceList1) or
                        ("TR069" in X_CT_COM_ServiceList1)):
                        info = u"工单失败:为避免新建包含tr069模式的WAN连接对原有tr069WAN连接产生影响,所以不再新建。\n"
                        log.app_info (info)
                        ret_data_scr += info
                        return ret_res, ret_data_scr
                
                    info = u"开始调用AddObject新建WANConnectionDevice实例。\n"
                    log.app_info (info)
                    ret_data_scr += info
                
                    Classpath = ROOT_PATH
                    #sleep(3)  # must be ;otherwise exception
                    ret3, ret_data3 = u1.add_object(
                                    ObjectName=Classpath)
                    
                    if (ret3 == ERR_SUCCESS):
                        instanceNum1 = ret_data3["InstanceNumber"]
                        info = u"新建WANConnectionDevice实例成功,返回实例号：%s 。\n" % instanceNum1
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
                        info = u"新建WANConnectionDevice实例失败，错误原因：%s 。\n" % ret_data3
                        log.app_err (info)
                        ret_data_scr += info
                        return ret_res, ret_data_scr
                
                    #第三--二步：新建WANIPConnection或WANPPPConnection实例
                    #只有是桥模式和路由PPPOE时,才新建WANPPPConnection实例
                    if AccessMode1 == 'PPPoE' or AccessMode1 == 'PPPoE_Bridged':
                        path4_1 = ROOT_PATH + instanceNum1 + '.WANPPPConnection.'
                        info = u"开始调用AddObject新建WAN连接的WANPPPConnection实例。\n"
                    else:
                        path4_1 = ROOT_PATH + instanceNum1 + '.WANIPConnection.'
                        info = u"开始调用AddObject新建WAN连接的WANIPConnection实例。\n"
                
                    log.app_info (info)
                    ret_data_scr += info
                
                    #sleep(3)  # must be ;otherwise exception
                    ret4_1, ret_data4_1 = u1.add_object(
                                    ObjectName=path4_1)
                
                    if (ret4_1 == ERR_SUCCESS):
                        instanceNum1_1 = ret_data4_1["InstanceNumber"]
                        tmp_path4_1 = path4_1 + instanceNum1_1
                        info = u"新建实例成功,返回实例号：%s 。\n" % instanceNum1_1
                        log.app_info (info)
                        ret_data_scr += info
                        rebootFlag = int(ret_data4_1["Status"])
                        if (rebootFlag == 1):
                            reboot_Yes = 1
                    else:
                        #对于失败的情况,直接返回失败
                        info = u"新建实例实例失败，退出执行，错误原因：%s 。\n" % ret_data4_1
                        log.app_err (info)
                        ret_data_scr += info
                        return ret_res, ret_data_scr
                    
                    
                    #只有是桥模式和路由PPPOE时,才新建WANPPPConnection实例
                    if AccessMode2 == 'PPPoE' or AccessMode2 == 'PPPoE_Bridged':
                        path4_2 = ROOT_PATH + instanceNum1 + '.WANPPPConnection.'
                        info = u"开始调用AddObject新建WAN连接的WANPPPConnection实例。\n"
                    else:
                        path4_2 = ROOT_PATH + instanceNum1 + '.WANIPConnection.'
                        info = u"开始调用AddObject新建WAN连接的WANIPConnection实例。\n"
                    
                    # 同一条vlan下多建一条WAN连接 add by shenlige 2013-11-11
                    ret4_2, ret_data4_2 = u1.add_object(
                                    ObjectName=path4_2)
                
                    if (ret4_2 == ERR_SUCCESS):
                        instanceNum1_2 = ret_data4_2["InstanceNumber"]
                        tmp_path4_2 = path4_2 + instanceNum1_2
                        info = u"新建实例成功,返回实例号：%s 。\n" % instanceNum1_2
                        log.app_info (info)
                        ret_data_scr += info
                        rebootFlag = int(ret_data4_2["Status"])
                        if (rebootFlag == 1):
                            reboot_Yes = 1
                    else:
                        #对于失败的情况,直接返回失败
                        info = u"新建实例实例失败，退出执行，错误原因：%s 。\n" % ret_data4_2
                        log.app_err (info)
                        ret_data_scr += info
                        return ret_res, ret_data_scr
                    
                    #第三--三步:调用SetParameterValues设置linkconfig参数：

                    ret5, ret_data5,reboot_Yes = _set_link_parameter_values(u1,DeviceType,tmp_path3,
                                                                         dict_wanlinkconfig,
                                                                         ret_data_scr,True)
                    if ret5 == ERR_SUCCESS:
                        ret_data_scr = ret_data5
                    else:
                        ret_data_scr = ret_data5
                        return ret_res, ret_data_scr
                    
                    #第三--四步:调用SetParameterValues设置WANPPPConnection参数：
                    if AccessMode1 == 'PPPoE' or AccessMode1 == 'PPPoE_Bridged':
                        tmp_values1 = dict_wanpppconnection1
                        info = u"开始调用SetParameterValues设置WANPPPConnection参数。\n"
                    else:
                        tmp_values1 = dict_wanipconnection1
                        info = u"开始调用SetParameterValues设置WANIPConnection参数。\n"
                    
                    
                    log.app_info (info)
                    ret_data_scr += info
                
                    #第三--四步:调用SetParameterValues设置WANPPPConnection参数：
                    path6_1 = tmp_path4_1 + '.'
                    para_list6_1 = []
                    WAN_Enable = []
                    
                    ret6_1, ret_data6_1,reboot_Yes,WAN_Enable = _set_ppporip_para(u1,tmp_values1,path6_1,
                                                                       ret_data_scr,WAN1_Flag, WANEnable_Switch,WAN_Enable)
                    
                    if ret6_1 == ERR_SUCCESS:
                        ret_data_scr = ret_data6_1
                    else:
                        ret_data_scr = ret_data6_1
                        return ret_res, ret_data_scr
                    
                    v6config_path = path6_1
                    # 设置六v6相关配置
                    if dict_v6config != {}:
                        ret_v6, ret_data_v6, reboot_Yes = _ipv6_config(u1,ret_data_prefix_info,
                                                dict_v6prefixinformation,
                                                dict_v6config,
                                                dict_dhcpv6server,
                                                dict_routeradvertisement,
                                                v6config_path,
                                                ret_data_scr)
            
                        if ret_v6 == ERR_SUCCESS:
                            ret_data_scr = ret_data_v6
                        else:
                            ret_data_scr = ret_data_v6
                            return ret_res, ret_data_scr
                    
                    # 将WAN连接使能单独下发
                    ret_wan_enable, ret_data_wan_enable,reboot_Yes = _wan_enable(u1,WAN_Enable,ret_data_scr)
                    
                    if ret_wan_enable == ERR_SUCCESS:
                        ret_data_scr = ret_data_wan_enable
                    else:
                        ret_data_scr = ret_data_wan_enable
                        return ret_res, ret_data_scr
                    
                    #另一条WAN连接设置
                    if AccessMode2 == 'PPPoE' or AccessMode2 == 'PPPoE_Bridged':
                        tmp_values2 = dict_wanpppconnection2
                        info = u"开始调用SetParameterValues设置WANPPPConnection参数。\n"
                    else:
                        tmp_values2 = dict_wanipconnection2
                        info = u"开始调用SetParameterValues设置WANIPConnection参数。\n"
                    
                    path6_2 = tmp_path4_2 + '.'
                    para_list6_2 = []
                    WAN_Enable = []
                    
                    ret6_2, ret_data6_2,reboot_Yes,WAN_Enable = _set_ppporip_para(u1,tmp_values2,path6_2,
                                                                       ret_data_scr,WAN2_Flag, WANEnable_Switch,WAN_Enable)
                    
                    if ret6_2 == ERR_SUCCESS:
                        ret_data_scr = ret_data6_2
                    else:
                        ret_data_scr = ret_data6_2
                        return ret_res, ret_data_scr
                    
                    
                    # 将WAN连接使能单独下发
                    ret_wan_enable, ret_data_wan_enable,reboot_Yes = _wan_enable(u1,WAN_Enable,ret_data_scr)
                    
                    if ret_wan_enable == ERR_SUCCESS:
                        ret_data_scr = ret_data_wan_enable
                    else:
                        ret_data_scr = ret_data_wan_enable
                        return ret_res, ret_data_scr
                
                # 一条新建，一条修改
                else:
                    
                    if WAN1_Flag != None and WAN2_Flag == None:
                        
                        One_VlanID_Two_WAN_Flag = 1
                        path2_list = modify_path_1.split('.')[0:-3]
                        path2_1_list = modify_path_1.split('.')[0:-1]
                        add_path_list = modify_path_1.split('.')[0:-2]
                        
                        match_server = X_CT_COM_ServiceList1
                        
                        modify_connectiontype = ConnectionType1
                        add_connectiontype = ConnectionType2
                        
                        if AccessMode1 == 'PPPoE' or AccessMode1 == 'PPPoE_Bridged':
                            modify_values = dict_wanpppconnection1
                            if AccessMode2 == 'PPPoE' or AccessMode2 == 'PPPoE_Bridged':
                                add_values = dict_wanpppconnection2
                            else:
                                add_values = dict_wanipconnection2
                        else:
                            modify_values = dict_wanipconnection1
                            if AccessMode2 == 'PPPoE' or AccessMode2 == 'PPPoE_Bridged':
                                add_values = dict_wanpppconnection2
                            else:
                                add_values = dict_wanipconnection2
                    
                        
                    elif WAN1_Flag == None and WAN2_Flag != None:
                        
                        One_VlanID_Two_WAN_Flag = 1
                        path2_list = modify_path_2.split('.')[0:-3]
                        path2_1_list = modify_path_2.split('.')[0:-1]
                        add_path_list = modify_path_2.split('.')[0:-2]
                        match_server = X_CT_COM_ServiceList2
                        
                        modify_connectiontype = ConnectionType2
                        add_connectiontype = ConnectionType1
                        
                        if AccessMode2 == 'PPPoE' or AccessMode2 == 'PPPoE_Bridged':
                            modify_values = dict_wanpppconnection2
                            if AccessMode1 == 'PPPoE' or AccessMode1 == 'PPPoE_Bridged':
                                add_values = dict_wanpppconnection1
                            else:
                                add_values = dict_wanipconnection1
                        else:
                            modify_values = dict_wanipconnection2
                            if AccessMode1 == 'PPPoE' or AccessMode1 == 'PPPoE_Bridged':
                                add_values = dict_wanpppconnection1
                            else:
                                add_values = dict_wanipconnection1
                        
                    else:
                        
                        ppporip_path1_list =  modify_path_1.split('.')[0:-2]
                        ppporip_path1 = '.'.join(ppporip_path1_list)
                        
                        ppporip_path2_list =  modify_path_2.split('.')[0:-2]
                        ppporip_path2 = '.'.join(ppporip_path2_list)
                        
                        if ppporip_path1 == ppporip_path2:
                            One_VlanID_Two_WAN_Flag = 2
                        else:
                            One_VlanID_Two_WAN_Flag = 1
                            path2_list = modify_path_1.split('.')[0:-3]
                            path2_1_list = modify_path_1.split('.')[0:-1]
                            add_path_list = modify_path_1.split('.')[0:-2]
                            
                            match_server = X_CT_COM_ServiceList1
                            
                            modify_connectiontype = ConnectionType1
                            add_connectiontype = ConnectionType2
                            
                            if AccessMode1 == 'PPPoE' or AccessMode1 == 'PPPoE_Bridged':
                                modify_values = dict_wanpppconnection1
                                if AccessMode2 == 'PPPoE' or AccessMode2 == 'PPPoE_Bridged':
                                    add_values = dict_wanpppconnection2
                                else:
                                    add_values = dict_wanipconnection2
                            else:
                                modify_values = dict_wanipconnection1
                                if AccessMode2 == 'PPPoE' or AccessMode2 == 'PPPoE_Bridged':
                                    add_values = dict_wanpppconnection2
                                else:
                                    add_values = dict_wanipconnection2
                    
                    if One_VlanID_Two_WAN_Flag == 1:
                    
                        info = u"查找到匹配 %s 模式的WAN连接，走修改流程，但需要再添加一条连接。\n" % match_server
                        log.app_info (info)
                        ret_data_scr += info
                    
                        #第三--三步:调用SetParameterValues设置linkconfig参数：
                        path4 = '.'.join(add_path_list) + '.'
                        path2 = '.'.join(path2_list) + '.'
                        path2_1 = '.'.join(path2_1_list) + '.'
                        
                        
                        # 修改Link层
                        if modify_values == dict_wanipconnection1 or modify_values == dict_wanpppconnection1:
                            modify_access = AccessMode1
                        else:
                            modify_access = AccessMode2
                        
                        if modify_access != 'PPPoE_Bridged':
                            ret5, ret_data5,reboot_Yes = _set_link_parameter_values(u1,DeviceType,path2,
                                                                         dict_wanlinkconfig,
                                                                         ret_data_scr)
                            if ret5 == ERR_SUCCESS:
                                ret_data_scr = ret_data5
                            else:
                                ret_data_scr = ret_data5
                                return ret_res, ret_data_scr
                        
                        info = u"开始设置参数值。\n"
                        log.app_info (info)
                        ret_data_scr += info
                        
                        #第三--四步:调用SetParameterValues设置WANPPPConnection参数：
                        path6_1 = path2_1
                        para_list6_1 = []
                        WAN_Enable = []
                        
                        # 修改WAN连接
                        ret6_1, ret_data6_1,reboot_Yes,WAN_Enable = _set_ppporip_para(u1,modify_values,path6_1,
                                                                       ret_data_scr,WAN1_Flag, WANEnable_Switch,WAN_Enable)
                    
                        if ret6_1 == ERR_SUCCESS:
                            ret_data_scr = ret_data6_1
                        else:
                            ret_data_scr = ret_data6_1
                            return ret_res, ret_data_scr
                        
                        #设置六v6相关配置  只有ConnectionType 为IP_Routed的连接才设置v6配置
                        v6config_path = path6_1
                        if dict_v6config != {} and modify_connectiontype == 'IP_Routed':
                            # 
                            ret_v6, ret_data_v6, reboot_Yes = _ipv6_config(u1,ret_data_prefix_info,
                                                dict_v6prefixinformation,
                                                dict_v6config,
                                                dict_dhcpv6server,
                                                dict_routeradvertisement,
                                                v6config_path,
                                                ret_data_scr)
            
                            if ret_v6 == ERR_SUCCESS:
                                ret_data_scr = ret_data_v6
                            else:
                                ret_data_scr = ret_data_v6
                                return ret_res, ret_data_scr
                    
                        # 将WAN连接使能单独下发
                        ret_wan_enable, ret_data_wan_enable,reboot_Yes = _wan_enable(u1,WAN_Enable,ret_data_scr)
                    
                        if ret_wan_enable == ERR_SUCCESS:
                            ret_data_scr = ret_data_wan_enable
                        else:
                            ret_data_scr = ret_data_wan_enable
                            return ret_res, ret_data_scr
                    
                        
                        # 同一条vlan下多建一条WAN连接 add by shenlige 2013-11-11
                        ret4_2, ret_data4_2 = u1.add_object(
                                    ObjectName=path4)
                    
                    
                        if (ret4_2 == ERR_SUCCESS):
                            instanceNum1_2 = ret_data4_2["InstanceNumber"]
                            tmp_path4_2 = path4 + instanceNum1_2
                            info = u"新建实例成功,返回实例号：%s 。\n" % instanceNum1_2
                            log.app_info (info)
                            ret_data_scr += info
                            rebootFlag = int(ret_data4_2["Status"])
                            if (rebootFlag == 1):
                                reboot_Yes = 1
                        else:
                            #对于失败的情况,直接返回失败
                            info = u"新建实例实例失败，退出执行，错误原因：%s 。\n" % ret_data4_2
                            log.app_err (info)
                            ret_data_scr += info
                            return ret_res, ret_data_scr
                    
                    
                        # 设置另一条WAN连接值
                        path6_2 = tmp_path4_2 + '.'
                        para_list6_2 = []
                        WAN_Enable = []
                        
                        info = u"开始设置参数值。\n"
                        log.app_info (info)
                        ret_data_scr += info
                        
                        ret6_2, ret_data6_2,reboot_Yes,WAN_Enable = _set_ppporip_para(u1,add_values,path6_2,
                                                                       ret_data_scr,WAN2_Flag, WANEnable_Switch,WAN_Enable)
                    
                        if ret6_2 == ERR_SUCCESS:
                            ret_data_scr = ret_data6_2
                        else:
                            ret_data_scr = ret_data6_2
                            return ret_res, ret_data_scr
                        
                        # 设置v6相关配置  有ConnectionType 为IP_Routed的连接才设置v6配置
                        v6config_path = path6_2
                        if dict_v6config != {} and add_connectiontype == 'IP_Routed':
                            
                            ret_v6, ret_data_v6, reboot_Yes = _ipv6_config(u1,ret_data_prefix_info,
                                                dict_v6prefixinformation,
                                                dict_v6config,
                                                dict_dhcpv6server,
                                                dict_routeradvertisement,
                                                v6config_path,
                                                ret_data_scr)
            
                            if ret_v6 == ERR_SUCCESS:
                                ret_data_scr = ret_data_v6
                            else:
                                ret_data_scr = ret_data_v6
                                return ret_res, ret_data_scr

                        
                    # 将WAN连接使能单独下发
                        ret_wan_enable, ret_data_wan_enable,reboot_Yes = _wan_enable(u1,WAN_Enable,ret_data_scr)
                    
                        if ret_wan_enable == ERR_SUCCESS:
                            ret_data_scr = ret_data_wan_enable
                        else:
                            ret_data_scr = ret_data_wan_enable
                            return ret_res, ret_data_scr

                    else:
                        info = u"查找到两条均匹配的WAN连接，走修改流程。\n"
                        log.app_info (info)
                        ret_data_scr += info
                    
                                        #第三--三步:调用SetParameterValues设置linkconfig参数：
                        path2_list = modify_path_1.split('.')[0:-3]
                        path2_1_list = modify_path_1.split('.')[0:-1]
                        path2_2_list = modify_path_2.split('.')[0:-1]
                    
                        path2 = '.'.join(path2_list) + '.'
                        path2_1 = '.'.join(path2_1_list) + '.'
                        path2_2 = '.'.join(path2_2_list) + '.'
                        
                        # 修改Link层
                        if AccessMode1 != 'PPPoE_Bridged':
                            ret5, ret_data5,reboot_Yes = _set_link_parameter_values(u1,DeviceType,path2,
                                                                         dict_wanlinkconfig,
                                                                         ret_data_scr)
                            if ret5 == ERR_SUCCESS:
                                ret_data_scr = ret_data5
                            else:
                                ret_data_scr = ret_data5
                                return ret_res, ret_data_scr
                    
                        # 修改SetParameterValues设置WANPPPConnection参数
                        if AccessMode1 == 'PPPoE' or AccessMode1 == 'PPPoE_Bridged':
                            tmp_values1 = dict_wanpppconnection1
                            info = u"开始调用SetParameterValues设置WANPPPConnection参数。\n"
                            log.app_info (info)
                            ret_data_scr += info
                        else:
                            tmp_values1 = dict_wanipconnection1
                            info = u"开始调用SetParameterValues设置WANIPConnection参数。\n"
                            log.app_info (info)
                            ret_data_scr += info
                
                        #第三--四步:调用SetParameterValues设置WANPPPConnection参数：
                        path6_1 = path2_1
                        para_list6_1 = []
                        WAN_Enable = []
                    
                        ret6_1, ret_data6_1,reboot_Yes,WAN_Enable = _set_ppporip_para(u1,tmp_values1,path6_1,
                                                                       ret_data_scr,WAN1_Flag, WANEnable_Switch,WAN_Enable)
                    
                        if ret6_1 == ERR_SUCCESS:
                            ret_data_scr = ret_data6_1
                        else:
                            ret_data_scr = ret_data6_1
                            return ret_res, ret_data_scr
                    
                        # v6相关设置  只有ConnectionType 为IP_Routed的连接才设置v6配置
                        v6config_path = path6_1
                        if dict_v6config != {} and ConnectionType1 == 'IP_Routed':
                            ret_v6, ret_data_v6, reboot_Yes = _ipv6_config(u1,ret_data_prefix_info,
                                                dict_v6prefixinformation,
                                                dict_v6config,
                                                dict_dhcpv6server,
                                                dict_routeradvertisement,
                                                v6config_path,
                                                ret_data_scr)
            
                            if ret_v6 == ERR_SUCCESS:
                                ret_data_scr = ret_data_v6
                            else:
                                ret_data_scr = ret_data_v6
                                return ret_res, ret_data_scr
                    
                        # WAN连接使能单独下发  
                        ret_wan_enable, ret_data_wan_enable,reboot_Yes = _wan_enable(u1,WAN_Enable,ret_data_scr)
                    
                        if ret_wan_enable == ERR_SUCCESS:
                            ret_data_scr = ret_data_wan_enable
                        else:
                            ret_data_scr = ret_data_wan_enable
                            return ret_res, ret_data_scr
                        
                        #修改另一条
                        if AccessMode2 == 'PPPoE' or AccessMode2 == 'PPPoE_Bridged':
                            tmp_values2 = dict_wanpppconnection2
                            info = u"开始调用SetParameterValues设置WANPPPConnection参数。\n"
                            log.app_info (info)
                            ret_data_scr += info
                        else:
                            tmp_values2 = dict_wanipconnection2
                            info = u"开始调用SetParameterValues设置WANIPConnection参数。\n"
                            log.app_info (info)
                            ret_data_scr += info
                                
                        path6_2 = path2_2
                        WAN_Enable = []
                    
                        ret6_2, ret_data6_2,reboot_Yes,WAN_Enable = _set_ppporip_para(u1,tmp_values2,path6_2,
                                                                       ret_data_scr,WAN2_Flag, WANEnable_Switch,WAN_Enable)
                    
                        if ret6_2 == ERR_SUCCESS:
                            ret_data_scr = ret_data6_2
                        else:
                            ret_data_scr = ret_data6_2
                            return ret_res, ret_data_scr
                        
                        # v6相关设置 有ConnectionType 为IP_Routed的连接才设置v6配置
                        v6config_path = path6_2
                        if dict_v6config != {} and ConnectionType2 == 'IP_Routed':
                            ret_v6, ret_data_v6, reboot_Yes = _ipv6_config(u1,ret_data_prefix_info,
                                                dict_v6prefixinformation,
                                                dict_v6config,
                                                dict_dhcpv6server,
                                                dict_routeradvertisement,
                                                v6config_path,
                                                ret_data_scr)
            
                            if ret_v6 == ERR_SUCCESS:
                                ret_data_scr = ret_data_v6
                            else:
                                ret_data_scr = ret_data_v6
                                return ret_res, ret_data_scr
                        
                        # WAN连接使能单独下发  
                        ret_wan_enable, ret_data_wan_enable,reboot_Yes = _wan_enable(u1,WAN_Enable,ret_data_scr)
                    
                        if ret_wan_enable == ERR_SUCCESS:
                            ret_data_scr = ret_data_wan_enable
                        else:
                            ret_data_scr = ret_data_wan_enable
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


def _set_link_parameter_values(sn_obj,DeviceType,path2,dict_wanlinkconfig,ret_data_scr,add=False):
    
    ret_res = ERR_FAIL
    rebootFlag = None
    
    if DeviceType == 'ADSL':
        
        if add == False:
            info = u"走X_CT-COM_ServiceList相同的流程(修改WAN连接),开始调用SetParameterValues修改WANDSLLinkConfig参数。\n"
        else:
            info = u"开始调用SetParameterValues设置WANDSLLinkConfig参数。\n"
        path5 = path2 + 'WANDSLLinkConfig.'
    elif DeviceType == 'LAN':
        
        if add == False:
            info = u"走X_CT-COM_ServiceList相同的流程(修改WAN连接),开始调用SetParameterValues修改WANEthernetLinkConfig参数。\n"
        else:
            info = u"开始调用SetParameterValues设置WANEthernetLinkConfig参数。\n"
   
        path5 = path2 + 'WANEthernetLinkConfig.'
    elif DeviceType == 'EPON':
        
        if add == False:
            info = u"走X_CT-COM_ServiceList相同的流程(修改WAN连接),开始调用SetParameterValues修改X_CT-COM_WANEponLinkConfig参数。\n"
        else:
            info = u"开始调用SetParameterValues设置X_CT-COM_WANEponLinkConfig参数。\n"
     
        path5 = path2 + 'X_CT-COM_WANEponLinkConfig.'                
    elif DeviceType == 'VDSL':
        
        if add == False:
            info = u"走X_CT-COM_ServiceList相同的流程(修改WAN连接),开始调用SetParameterValues修改VDSL/ADSL兼容网关的WANDSLLinkConfig参数。\n"
        else:
            info = u"开始调用SetParameterValues设置VDSL/ADSL兼容网关的WANDSLLinkConfig参数。\n"
      
        path5 = path2 + 'WANDSLLinkConfig.'
    elif DeviceType == 'GPON':
        
        if add == False:
            info = u"走X_CT-COM_ServiceList相同的流程(修改WAN连接),开始调用SetParameterValues修改X_CT-COM_WANGponLinkConfig参数。\n"
        else:
            info = u"开始调用SetParameterValues设置X_CT-COM_WANGponLinkConfig参数。\n"
      
        path5 = path2 + 'X_CT-COM_WANGponLinkConfig.'
    else:
        
        if add == False:
            info = u"走X_CT-COM_ServiceList相同的流程(修改WAN连接),开始调用SetParameterValues修改WANDSLLinkConfig参数。\n"
        else:
            info = u"开始调用SetParameterValues设置WANDSLLinkConfig参数。\n"
     
        path5 = path2 + 'WANDSLLinkConfig.'

    log.app_info (info)
    ret_data_scr += info
    para_list5 = []

    for i in dict_wanlinkconfig:
        if dict_wanlinkconfig[i][0] == 1:
            # 对于Linkconfig的PVC或VLAN节点删除,不做修改
            # GCW 20130418 修改WAN连接参数时，对X_CT-COM_Mode节点也不修改
            # v6工单修改link层的vlan modify by shenlige 20131211
            """
            if i == 'DestinationAddress' or i == 'VLANIDMark' or \
               i == 'X_CT-COM_VLANIDMark' or i == "X_CT-COM_Mode":
                continue
            """
            tmp_path = path5 + i
            para_list5.append(dict(Name=tmp_path, Value=dict_wanlinkconfig[i][1]))

    # 不能修改PVC或vlan
    if para_list5 == []:
        info = u"参数列表为空,请检查。\n"
        log.app_info (info)
        ret_data_scr += info
        return ret_res, ret_data_scr,rebootFlag

    #sleep(3)  # must be ;otherwise exception
    ret5, ret_data5 = sn_obj.set_parameter_values(ParameterList=para_list5)
    if (ret5 == ERR_SUCCESS):
        info = u"设置参数成功。\n"
        log.app_info (info)
        ret_data_scr += info
        rebootFlag = int(ret_data5["Status"])
        if (rebootFlag == 1):
            reboot_Yes = 1
        else:
            reboot_Yes = 0
        return ERR_SUCCESS,ret_data_scr,reboot_Yes
    else:
        #对于失败的情况，直接退出
        info = u"设置参数失败,错误原因：%s 。\n" % ret_data5
        log.app_err (info)
        ret_data_scr += info
        return ret_res, ret_data_scr,rebootFlag
    



def _set_ppporip_para(sn_obj,tmp_values,path6_x,ret_data_scr,WAN_Flag, WANEnable_Switch,WAN_Enable):
    
    ret_res = ERR_FAIL
    rebootFlag = None
    
    para_list6_x = []
    for i in tmp_values:
        if tmp_values[i][0] == 1:
            # 判断X_CT-COM_ServiceList包含与被包含的关系做区分处理.
            # 标志位1表示X_CT-COM_ServiceList值需以工单中的为准,重新下发,2表示不下发
            if WAN_Flag == None:
                pass
            elif WAN_Flag == 1:
                pass
            else:
                if i == 'X_CT-COM_ServiceList':
                    continue
            #如果WAN连接使能需单独下发,则将使能的动作单独保存
            if WANEnable_Switch == False and i == 'Enable':
                WAN_Enable.append(dict(Name=path6_x + i, Value=tmp_values[i][1]))
                continue

            tmp_path = path6_x + i
            para_list6_x.append(dict(Name=tmp_path, Value=tmp_values[i][1]))
                    
    if para_list6_x == []:
        return ret_res, ret_data_scr,rebootFlag,WAN_Enable
                
    #sleep(3)  # must be ;otherwise exception
    ret6, ret_data6 = sn_obj.set_parameter_values(ParameterList=para_list6_x)
    if (ret6 == ERR_SUCCESS):
        info = u"设置参数成功。\n"
        log.app_info (info)
        ret_data_scr += info
        rebootFlag = int(ret_data6["Status"])
        if (rebootFlag == 1):
            reboot_Yes = 1
        else:
            reboot_Yes = 0
        return ERR_SUCCESS,ret_data_scr,reboot_Yes,WAN_Enable
    else:
        #对于失败的情况，直接返回失败
        info = u"设置参数失败，错误原因：%s 。\n" % ret_data6
        log.app_info (info)
        ret_data_scr += info
        return ret_res, ret_data_scr,rebootFlag,WAN_Enable
    


def _wan_enable(sn_obj,WAN_Enable,ret_data_scr):
    
    ret_res = ERR_FAIL
    rebootFlag = None
    #将WAN连接使能单独下发
    if WAN_Enable != []:
        info = u"开始调用SetParameterValues设置WAN连接使能参数。\n"
        log.app_info (info)
        ret_data_scr += info
        #sleep(3)  # must be ;otherwise exception
        ret_wan_enable, ret_data_wan_enable = sn_obj.set_parameter_values(ParameterList=WAN_Enable)
        if (ret_wan_enable == ERR_SUCCESS):
            info = u"设置WAN连接使能参数成功。\n"
            log.app_info (info)
            ret_data_scr += info
            rebootFlag = int(ret_data_wan_enable["Status"])
            if (rebootFlag == 1):
                reboot_Yes = 1
            else:
                reboot_Yes = 0
            return ERR_SUCCESS,ret_data_scr,reboot_Yes
        else:
            #对于失败的情况，直接返回错误
            info = u"设置WAN连接使能参数失败，错误原因：%s 。\n" % ret_data_wan_enable
            log.app_err (info)
            ret_data_scr += info
            return ret_res, ret_data_scr,rebootFlag


def _ipv6_config(sn_obj,ret_data_prefix_info,
                 dict_v6prefixinformation,
                 dict_v6config,
                 dict_dhcpv6server,
                 dict_routeradvertisement,
                 v6config_path,
                 ret_data_scr):
    
    ret_res = ERR_FAIL
    
    # IPv6相关参数下发 shenlige 2013-11-7
    LAN_IPv6Config_Path = "InternetGatewayDevice.LANDevice.1.X_CT-COM_IPv6Config."
    LAN_DHCPv6_Path = "InternetGatewayDevice.LANDevice.1.X_CT-COM_DHCPv6Server."
    LAN_RouterAdv_Path = "InternetGatewayDevice.LANDevice.1.X_CT-COM_RouterAdvertisement."
                
    para_list_v6 = []  #保存LAN侧 v6相关设置
    # PrefixInformation相关
    tmp_prefix_info = []
    re_prefix = "InternetGatewayDevice\.LANDevice\.1\.X_CT-COM_IPv6Config\.PrefixInformation\.\d\.$"
    
    for i in xrange(len(ret_data_prefix_info['ParameterList'])):
        tmp_path_prefix_1 = ret_data_prefix_info['ParameterList'][i]['Name'] 
        m_prefix = re.match(re_prefix,tmp_path_prefix_1)
        
        if m_prefix is not None:
            tmp_prefix_info.append(tmp_path_prefix_1)
    
    
    for i in tmp_prefix_info:
        tmp_path_prefix_1 = i 
                    
        for j in dict_v6prefixinformation:
            if dict_v6prefixinformation[j][0] == 1:
                tmp_path_prefix = tmp_path_prefix_1 + j
                if j == 'DelegatedWanConnection':
                    tmp_value = v6config_path
                else:
                    tmp_value = dict_v6prefixinformation[j][1]
                
                para_list_v6.append(dict(Name=tmp_path_prefix,Value=tmp_value))
                
    # X_CT-COM_IPv6Config相关不包括PrefixInformation
    for i in dict_v6config:
        if dict_v6config[i][0] == 1:
            tmp_path_v6config = LAN_IPv6Config_Path + i
            if i == 'IPv6DNSWANConnection':
                tmp_value = v6config_path
            else:
                tmp_value = dict_v6config[i][1]
            para_list_v6.append(dict(Name=tmp_path_v6config,Value=tmp_value))
                
    # X_CT-COM_DHCPv6Server相关
    for i in dict_dhcpv6server:
        if dict_dhcpv6server[i][0] == 1:
            tmp_path_dhcpv6 = LAN_DHCPv6_Path + i
            para_list_v6.append(dict(Name=tmp_path_dhcpv6,Value=dict_dhcpv6server[i][1]))
                
    # X_CT-COM_RouterAdvertisement相关
    for i in dict_routeradvertisement:
        if dict_routeradvertisement[i][0] == 1:
            tmp_path_dhcpv6 = LAN_RouterAdv_Path + i
            para_list_v6.append(dict(Name=tmp_path_dhcpv6,Value=dict_routeradvertisement[i][1]))
                
    info = u"开始设置v6相关LAN侧配置。\n"
    log.app_info (info)
    ret_data_scr += info
    
    rebootFlag = None         
    ret7, ret_data7 = sn_obj.set_parameter_values(ParameterList=para_list_v6)
    if (ret7 == ERR_SUCCESS):
        info = u"设置参数成功。\n"
        log.app_info (info)
        ret_data_scr += info
        rebootFlag = int(ret_data7["Status"])
        if (rebootFlag == 1):
            reboot_Yes = 1
        else:
            reboot_Yes = 0
        return    ERR_SUCCESS,ret_data_scr,reboot_Yes
    else:
        #对于失败的情况，直接返回失败
        info = u"设置参数失败，错误原因：%s 。\n" % ret_data7
        log.app_err (info)
        ret_data_scr += info
        return ret_res, ret_data_scr,rebootFlag

def _find_wan_server_and_connecttype(sn_obj,
                                     AccessMode,
                                     dict_wanpppconnection,
                                     dict_wanipconnection,
                                     ret_data_root,
                                     ret_data_scr):
    ret_res = ERR_FAIL
    path2_1_list = []
    if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':
                       
        reg_Username = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANPPPConnection.\d+\.Username"
        reg_X_CT_COM_ServiceList = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANPPPConnection.\d+\.X_CT-COM_ServiceList"
        reg_ConnectionType = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANPPPConnection.\d+\.ConnectionType"
            
    elif AccessMode == 'DHCP' or AccessMode == 'Static':
                        
        reg_Username = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANIPConnection.\d+\.Username"
        reg_X_CT_COM_ServiceList = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANIPConnection.\d+\.X_CT-COM_ServiceList"
        reg_ConnectionType = "InternetGatewayDevice\.WANDevice\.1\.WANConnectionDevice.\d+\.WANIPConnection.\d+\.ConnectionType"
                    
                
    ret_connectiontype = []
    ret_serverlist = []
    
    serverlist_items = []     # 保存查询到的serverlist 路径值
    connect_type_items = []   # 保存查询到的connecttype 路径值
    
    for i in xrange(len(ret_data_root['ParameterList'])):
                    
        tmp_path_getvalue = ret_data_root['ParameterList'][i]['Name']
                    
        m_username = re.match(reg_Username,tmp_path_getvalue)
        m_serverlist = re.match(reg_X_CT_COM_ServiceList,tmp_path_getvalue)
        m_connectiontype = re.match(reg_ConnectionType,tmp_path_getvalue)
                    
        if m_username is not None:
            path2_1_list.append(tmp_path_getvalue)
                    
        if m_serverlist is not None:
            path2_1_list.append(tmp_path_getvalue)
            ret_serverlist.append(tmp_path_getvalue)
                    
        if m_connectiontype is not None:
            path2_1_list.append(tmp_path_getvalue)
            ret_connectiontype.append(tmp_path_getvalue)
                
    if len(ret_connectiontype) != len(ret_serverlist):
        info = u"GetParameterNames查找到WAN连接的X_CT_COM_ServiceList和ConnectionType节点个数不等，工单异常退出。\n"
        log.app_info (info)
        ret_data_scr += info 
        return ret_res, serverlist_items,connect_type_items,ret_data_scr 
                
    ret_data_getvalue = []
                
    if path2_1_list != []:
                    
        info = u"开始调用GetParameterValues查找WAN连接实例下的Username、X_CT_COM_ServiceList和ConnectionType值。\n"
        log.app_info (info)
        ret_data_scr += info
                    
        ret_get_value, ret_data_getvalue = sn_obj.get_parameter_values(ParameterNames=path2_1_list)
                    
        if (ret_get_value == ERR_SUCCESS):
            info = u"查找WAN连接实例下的Username、X_CT_COM_ServiceList和ConnectionType值成功,返回:%s 。\n" % ret_data_getvalue
            log.app_info (info)
            ret_data_scr += info
                        
        else:
                        
            info = u"获取WAN连接实例下的Username、X_CT_COM_ServiceList和ConnectionType值失败，错误信息：%s 。\n" % ret_data_getvalue
            log.app_err (info)
            ret_data_scr += info
            return ret_res, serverlist_items,connect_type_items,ret_data_scr            
                        
    else:
        pass
                    
    if ret_data_getvalue != []:
                    
        getvalue_list = ret_data_getvalue["ParameterList"]
    else:
        getvalue_list = []
                                           
    for item in getvalue_list:
                            
        tmp_m_serverlist = re.match(reg_X_CT_COM_ServiceList,item['Name'])
        tmp_m_connecttype = re.match(reg_ConnectionType,item['Name'])
                            
        if tmp_m_serverlist is not None:
            serverlist_items.append(item)
                            
        if tmp_m_connecttype is not None:
            connect_type_items.append(item)
                        
    return ERR_SUCCESS, serverlist_items,connect_type_items,ret_data_scr

