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

def AddAnIPTV(obj, sn, WANEnable_Switch, DeviceType,
               AccessMode, PVC_OR_VLAN,
               dict_root,
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
            info = u"开始调用GetParameterNames方法，查询WAN连接\n"
            log.app_info (info)
            ret_data_scr += info
            #sleep(3)  # must be ;otherwise exception
            ret_root, ret_data_root = u1.get_parameter_names(ParameterPath=ROOT_PATH, NextLevel=1)
            if (ret_root == ERR_SUCCESS):
                info = u"查询WAN连接成功\n"
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
                
            #第二步：逐个查找,对于A上行,查PVC,其他的则查VLAN
            #path2 = []
            path2 = '' # 保存查到有相同的PVC或关键参数值的WAN连接路径
            path2_1 = '' # 保存WANPPPConection或WANIPConection节点路径保存,后面修改参数时有用
            PVC_Flag = None 
            #直接调GetParameterValues  查PVC或VLAN
            for i in xrange(len(ret_data_root['ParameterList'])):
                tmp_path2 = ret_data_root['ParameterList'][i]['Name']
                #A上行是关心PVC，LAN上行是关心VLAN，PON上行也是关心VLAN
                if DeviceType == 'ADSL':
                    tmp_path2 = tmp_path2 + 'WANDSLLinkConfig.DestinationAddress'
                    info = u"开始调用GetParameterValues,查询第%s个WAN连接的PVC节点DestinationAddress值\n" % str(i+1)
                elif DeviceType == 'LAN':
                    tmp_path2 = tmp_path2 + 'WANEthernetLinkConfig.X_CT-COM_VLANIDMark'
                    info = u"开始调用GetParameterValues,查询第%s个WAN连接的VLAN节点X_CT-COM_VLANIDMark值\n" % str(i+1)
                elif DeviceType == 'EPON':
                    tmp_path2 = tmp_path2 + 'X_CT-COM_WANEponLinkConfig.VLANIDMark'
                    info = u"开始调用GetParameterValues,查询第%s个WAN连接的VLAN节点VLANIDMark值\n" % str(i+1)
                elif DeviceType == 'VDSL':
                    tmp_path2 = tmp_path2 + 'X_CT-COM_WANVdslLinkConfig.VLANIDMark'
                    info = u"开始调用GetParameterValues,查询第%s个WAN连接的VLAN节点VLANIDMark值\n" % str(i+1)
                elif DeviceType == 'GPON':
                    tmp_path2 = tmp_path2 + 'X_CT-COM_WANGponLinkConfig.VLANIDMark'
                    info = u"开始调用GetParameterValues,查询第%s个WAN连接的VLAN节点VLANIDMark值\n" % str(i+1)
                else:
                    tmp_path2 = tmp_path2 + 'WANDSLLinkConfig.DestinationAddress'
                    info = u"开始调用GetParameterValues,查询第%s个WAN连接的PVC节点DestinationAddress值\n" % str(i+1)
                log.app_info (info)
                ret_data_scr += info
                
                #sleep(3)
                ret2, ret_data2 = u1.get_parameter_values(ParameterNames=tmp_path2)
                if (ret2 == ERR_SUCCESS):
                    info = u"查询成功,返回:%s\n" % ret_data2
                    log.app_info (info)
                    ret_data_scr += info
                    # 当返回的PVC与要绑定的相同时,标记PVC_Flag,走修改流程
                    if ret_data2['ParameterList'] == []:
                        pass
                    else:
                        # 如果查到PVC或VLAN相同，则标记
                        if ret_data2['ParameterList'] != []:
                            if ret_data2['ParameterList'][0]['Value'] == PVC_OR_VLAN:
                                # 查到有匹配PVC
                                PVC_Flag = 0
                                path2 = ret_data_root['ParameterList'][i]['Name']
                                break
                            else:
                                # 查不到匹配的PVC
                                continue
                        else:
                            continue
                else:
                    #对于失败的情况，直接返回错误
                    info = u"查询失败,错误信息%s\n" % ret_data2
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
            
            WAN_Flag = None 
            if PVC_Flag == 0:
                
                ret_tmp_path2 = []

                # 不同的WAN连接模式,其节点路径不同
                if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':
                    tmp_path2 = path2 + 'WANPPPConnection.'
                    X_CT_COM_ServiceList = dict_wanpppconnection['X_CT-COM_ServiceList'][1]
                    ConnectionType = dict_wanpppconnection['ConnectionType'][1]
                    info = u"开始调用GetParameterNames查找第%s条WAN连接WANPPPConnection实例\n" % str(i+1)
                elif AccessMode == 'DHCP' or AccessMode == 'Static':
                    tmp_path2 = path2 + 'WANIPConnection.'
                    X_CT_COM_ServiceList = dict_wanipconnection['X_CT-COM_ServiceList'][1]
                    ConnectionType = dict_wanipconnection['ConnectionType'][1]
                    info = u"开始调用GetParameterNames查找第%s条WAN连接WANIPConnection实例\n" % str(i+1)
                
                log.app_info (info)
                ret_data_scr += info
                ret_tmp_path2=[]
                #sleep(3)
                ret2, ret_data2 = u1.get_parameter_names(ParameterPath=tmp_path2, NextLevel=1)
                if (ret2 == ERR_SUCCESS):
                    info = u"查找WAN连接实例成功\n"
                    log.app_info (info)
                    ret_data_scr += info
                    # GCW　20130329　解决部分CPE同时将当前路径返回的情况,将其删除
                    ret_data2 = DelOwnParameterNames(ret_data2, tmp_path2)
                    
                    if ret_data2['ParameterList'] != []:
                        for tmp_index in xrange(len(ret_data2['ParameterList'])):
                            ret_tmp_path2.append(ret_data2['ParameterList'][tmp_index]['Name'])
                else:
                    #对于失败的情况，直接退出
                    info = u"查找WAN连接实例失败,错误信息: %s\n" % ret_data2
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                
                # 第2.2步,对于PPPOE查找X_CT-COM_ServiceList和Username值.
                # 由于贝曼有些版本只查X_CT-COM_ServiceList,或者查到Username相同与否不影响判断结果,
                # 所以目前只支持查X_CT-COM_ServiceList
                for i in xrange(len(ret_tmp_path2)):
                    info = u"开始调用GetParameterValues查找第%s个WAN连接实例下的X_CT-COM_ServiceList值\n" % str(i+1)
                    log.app_info (info)
                    ret_data_scr += info
                    
                    tmp_path2_2 = []                    
                    tmp_path2_2.append(ret_tmp_path2[i] + 'X_CT-COM_ServiceList')
                    # GCW 20130410对桥模式单独处理，避免修改PPPOE INTERNET为桥 INTERNET的情况
                    tmp_path2_2.append(ret_tmp_path2[i] + 'ConnectionType')
                    #sleep(3)
                    ret2_2, ret_data2_2 = u1.get_parameter_values(ParameterNames=tmp_path2_2)
                    if (ret2_2 == ERR_SUCCESS):
                        info = u"查找第%s个WAN连接实例下的X_CT-COM_ServiceList和ConnectionType值成功,返回:%s\n" % (str(i+1), ret_data2_2)
                        log.app_info (info)
                        ret_data_scr += info
                        # 判断值是否相等,相等(或被包含)则只修改linkconfig节点的值即可,否则需走后面的正常流程新建WAN连接
                        if AccessMode == "PPPoE_Bridged":
                            ConnectionType = "PPPoE_Bridged"
                        else:
                            ConnectionType = "IP_Routed"
                        
                        # GCW 20130417 路由对路由比较，桥对桥的比较才更合理
                        if ConnectionType == ret_data2_2['ParameterList'][0]['Value'] or \
                           ConnectionType == ret_data2_2['ParameterList'][1]['Value']:
                            # 如果非完全不相等，则需做特殊处理
                            if (ret_data2_2['ParameterList'][0]['Value'] in X_CT_COM_ServiceList \
                                    or ret_data2_2['ParameterList'][1]['Value'] in X_CT_COM_ServiceList) \
                                or (X_CT_COM_ServiceList in ret_data2_2['ParameterList'][0]['Value'] \
                                    or X_CT_COM_ServiceList in ret_data2_2['ParameterList'][1]['Value']):
                                # GCW 20130408 判断X_CT-COM_ServiceList包含与被包含的关系做区分处理.
                                if (ret_data2_2['ParameterList'][0]['Value'] in X_CT_COM_ServiceList \
                                  or ret_data2_2['ParameterList'][1]['Value'] in X_CT_COM_ServiceList):
                                    info = u"当前CPE中的X_CT-COM_ServiceList值包含于工单中要求的X_CT-COM_ServiceList值:%s,\n" % X_CT_COM_ServiceList
                                    info += u"走修改WAN连接的流程,且重新下发X_CT-COM_ServiceList值的修改\n"
                                    log.app_info (info)
                                    ret_data_scr += info
                                    WAN_Flag = 0  #表示CPE当前值包含于工单,走修改WAN流程,且X_CT-COM_ServiceList需下发
                                else:
                                    info = u"当前工单中的X_CT-COM_ServiceList值：%s包含于CPE中的X_CT-COM_ServiceList值，\n" % X_CT_COM_ServiceList
                                    info += u"走修改WAN连接流程,但不下发对X_CT-COM_ServiceList值的修改.\n"
                                    log.app_info (info)
                                    ret_data_scr += info
                                    WAN_Flag = 3  #表示工单中的值包含于当前CPE中,走修改WAN流程,但X_CT-COM_ServiceList不需下发
                                path2_1 = ret_tmp_path2[i]
                                #将上一层路径保存并退出循环,留给下一步直接修改linkconfig参数
                                #ret_tmp_path2[i]类似于InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3.WANPPPConnection.1.
                                a = ret_tmp_path2[i].split('.')
                                for i in xrange(len(a) - 3):
                                    path2 += a[i]
                                    path2 += '.' # 将当前的WANConnectionDevice.节点路径保存,后面修改参数时有用
                                break
                            else:
                                continue
                        else:
                            continue
                    else:
                        info = u"查找第%s个WAN连接实例下的X_CT-COM_ServiceList值失败,返回:%s\n" % (str(i+1), ret_data2_2)
                        log.app_info (info)
                        ret_data_scr += info
                        return ret_res, ret_data_scr 
                
                
                if WAN_Flag == None:
                    info = u"查找不到匹配 %s 模式的WAN连接\n" % X_CT_COM_ServiceList
                    log.app_info (info)
                    ret_data_scr += info
                    WAN_Flag = 1
            
            else:
                #对于未查找到相同PVC的，直接返回错误
                info = u"未查找到PVC或VLAN为 %s 的连接，请确认！" % PVC_OR_VLAN
                log.app_err (info)
                ret_data_scr += info
                return ret_res, ret_data_scr
                
            if WAN_Flag == 1 or WAN_Flag == 2:
                #第三--一步：新建WANConnectionDevice实例
                info = u"走X_CT-COM_ServiceList不相同的流程(新建WAN连接).\n"
                log.app_info (info)
                ret_data_scr += info
                
                # 解决用户新建tr069WAN连接导致CPE与ACS通讯异常的问题,强制不准新建包含TR0069的WAN连接
                
                if (("tr069" in X_CT_COM_ServiceList) or
                    ("TR069" in X_CT_COM_ServiceList)):
                    info = u"工单失败:为避免新建包含tr069模式的WAN连接对原有tr069WAN连接产生影响,所以不再新建.\n"
                    log.app_info (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                
                # 如果查找到相同的PVC，则在该PVC/VLAN下新建一个IPTV连接
                if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':
                    
                    tmp_path3 = path2 + 'WANPPPConnection.'
                    info = u"查到匹配的PVC或VLAN,开始在该PVC或VLAN下新建一条实例。\n"
                
                elif AccessMode == 'DHCP' or AccessMode == 'Static':
                    
                    tmp_path3 = path2 + 'WANIPConnection.'
                    info = u"查到匹配的PVC或VLAN,开始在该PVC或VLAN下新建一条实例。\n"
                log.app_info (info)
                ret_data_scr += info
                
                #sleep(3)  # must be ;otherwise exception
                ret3, ret_data3 = u1.add_object(
                                    ObjectName=tmp_path3)

                if (ret3 == ERR_SUCCESS):
                    instanceNum1 = ret_data3["InstanceNumber"]
                    tmp_path4 = tmp_path3 + instanceNum1 + '.'
                    info = u"新建实例成功,返回实例号：%s\n" % instanceNum1
                    log.app_info (info)
                    ret_data_scr += info
                    rollbacklist.append(tmp_path4)
                    rebootFlag = int(ret_data3["Status"])
                    if (rebootFlag == 1):
                        reboot_Yes = 1
                else:
                    #对于失败的情况，直接退出
                    info = u"新建实例失败，错误原因：%s\n" % ret_data3
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                
                if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':
                    tmp_values = dict_wanpppconnection
                    info = u"开始调用SetParameterValues设置WANPPPConnection参数\n"
                else:
                    tmp_values = dict_wanipconnection
                    info = u"开始调用SetParameterValues设置WANIPConnection参数\n"
                log.app_info (info)
                ret_data_scr += info
                
                #第三--四步:调用SetParameterValues设置WANPPPConnection参数：
                para_list6 = []
                WAN_Enable = []
                for j in tmp_values:
                    if tmp_values[j][0] == 1:
                        #如果WAN连接使能需单独下发,则将使能的动作单独保存
                        if WANEnable_Switch == False and j == 'Enable':
                            WAN_Enable.append(dict(Name=tmp_path4 + j, Value=tmp_values[j][1]))
                            continue
                        
                        tmp_path = tmp_path4 + j
                        para_list6.append(dict(Name=tmp_path, Value=tmp_values[j][1]))
                        
                if para_list6 == []:
                    info = u"参数为空,请检查\n"
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                
                #sleep(3)  # must be ;otherwise exception
                ret6, ret_data6 = u1.set_parameter_values(ParameterList=para_list6)
                if (ret6 == ERR_SUCCESS):
                    info = u"调用SetParameterValues设置参数成功\n"
                    log.app_info (info)
                    ret_data_scr += info
                    rebootFlag = int(ret_data6["Status"])
                    if (rebootFlag == 1):
                        reboot_Yes = 1
                else:
                    #对于失败的情况，直接返回失败
                    info = u"调用SetParameterValues设置参数失败，错误原因：%s\n" % ret_data6
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
                        #对于失败的情况，如何处理?
                        info = u"设置WAN连接使能参数失败，错误原因：%s\n" % ret_data_wan_enable
                        log.app_err (info)
                        ret_data_scr += info
                        return ret_res, ret_data_scr
       
            elif WAN_Flag == 0 or WAN_Flag == 3:
                """
                #当查到有相匹配的X_CT-COM_ServiceList和Username值时的处理流程，不需要新建,只需更改WANIPConnection或WANPPPConnection节点下的参数即可
                #第三--三步:调用SetParameterValues设置linkconfig参数：
                if DeviceType == 'ADSL':
                    info = u"走X_CT-COM_ServiceList相同的流程(修改WAN连接),开始调用SetParameterValues修改WANDSLLinkConfig参数\n"
                    path5 = path2 + 'WANDSLLinkConfig.'
                elif DeviceType == 'LAN':
                    info = u"走X_CT-COM_ServiceList相同的流程(修改WAN连接),开始调用SetParameterValues修改WANEthernetLinkConfig参数\n"
                    path5 = path2 + 'WANEthernetLinkConfig.'
                elif DeviceType == 'EPON':
                    info = u"走X_CT-COM_ServiceList相同的流程(修改WAN连接),开始调用SetParameterValues修改X_CT-COM_WANEponLinkConfig参数\n"
                    path5 = path2 + 'X_CT-COM_WANEponLinkConfig.'                
                elif DeviceType == 'VDSL':
                    info = u"走X_CT-COM_ServiceList相同的流程(修改WAN连接),开始调用SetParameterValues修改X_CT-COM_WANVdslLinkConfig参数\n"
                    path5 = path2 + 'X_CT-COM_WANVdslLinkConfig.'
                elif DeviceType == 'GPON':
                    info = u"走X_CT-COM_ServiceList相同的流程(修改WAN连接),开始调用SetParameterValues修改X_CT-COM_WANGponLinkConfig参数\n"
                    path5 = path2 + 'X_CT-COM_WANGponLinkConfig.'
                else:
                    info = u"走X_CT-COM_ServiceList相同的流程(修改WAN连接),开始调用SetParameterValues修改WANDSLLinkConfig参数\n"
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
                    info = u"参数列表为空,请检查\n"
                    log.app_info (info)
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
                    info = u"设置参数失败,错误原因：%s\n" % ret_data5
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                """
                # 修改SetParameterValues设置WANPPPConnection参数
                if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':
                    tmp_values = dict_wanpppconnection
                    info = u"开始调用SetParameterValues设置WANPPPConnection参数\n"
                    log.app_info (info)
                    ret_data_scr += info
                else:
                    tmp_values = dict_wanipconnection
                    info = u"开始调用SetParameterValues设置WANIPConnection参数\n"
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
                    info = u"设置参数成功\n"
                    log.app_info (info)
                    ret_data_scr += info
                    rebootFlag = int(ret_data6["Status"])
                    if (rebootFlag == 1):
                        reboot_Yes = 1
                else:
                    #对于失败的情况，直接返回失败
                    info = u"设置参数失败，错误原因：%s\n" % ret_data6
                    log.app_info (info)
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

                #sleep(130)
                ret, ret_data = reboot_wait_next_inform(u1)
                if (ret != ERR_SUCCESS):
                    ret_data_scr += ret_data
                    break
               
            #第七步：调用SetParameterValues设置X_CT-COM_IPTV参数：            
            para_list7 = []
            path = 'InternetGatewayDevice.Services.X_CT-COM_IPTV.'
            for i in dict_root:
                if dict_root[i][0] == 1:
                    tmp_path = path + i
                    para_list7.append(dict(Name=tmp_path, Value=dict_root[i][1]))
            if para_list7 == []:
                info = u"X_CT-COM_IPTV参数为空,请检查\n"
                log.app_err (info)
                ret_data_scr += info
                return ret_res, ret_data_scr
            info = u"开始调用SetParameterValues设置X_CT-COM_IPTV节点参数\n"
            log.app_info (info)
            ret_data_scr += info
            
            #sleep(3)  # must be ;otherwise exception
            ret7, ret_data7 = u1.set_parameter_values(ParameterList=para_list7)
            if (ret7 == ERR_SUCCESS):
                info = u"设置参数成功\n"
                log.app_info (info)
                ret_data_scr += info
                rebootFlag = int(ret_data7["Status"])
                if (rebootFlag == 1):
                    reboot_Yes = 1
            else:
                #对于失败的情况，如何处理?
                info = u"设置参数失败，错误原因：%s\n" % ret_data7
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