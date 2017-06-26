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

def IPTVEnable(obj, sn, WANEnable_Switch, DeviceType,
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
            WAN_Flag = None 
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
                    tmp_path2 = tmp_path2 + 'WANDSLLinkConfig.X_CT-COM_VLAN'
                    info = u"开始调用GetParameterValues,查询第%s个WAN连接的VLAN节点X_CT-COM_VLAN值\n" % str(i+1)
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
                    # 当返回的PVC与要绑定的相同时,标记WAN_Flag,走修改流程
                    if ret_data2['ParameterList'] == []:
                        pass
                    else:
                        # 如果查到PVC或VLAN相同，则标记
                        if ret_data2['ParameterList'] != []:
                            if ret_data2['ParameterList'][0]['Value'] == PVC_OR_VLAN:
                                # 查到有匹配PVC
                                WAN_Flag = 0
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
            
            # 如果一直没有查到相同的,则没有对WAN_Flag标志位做过修改,则走新建流程
            if WAN_Flag == None:
                WAN_Flag = 1
            
            # 查不到匹配的PVC或VLAN,则走新建流程,否则还需再查WANPPPConnection节点下的值
            if WAN_Flag == 0:
                #当查到有相匹配的PVC时的处理流程，则还需查WANPPPConnection下的三个节点是否一致
                #如果完全一致,则直接使能IGMP,否则需重新设置WANPPPConnection下的值(注意原有是INTERNET,重新下发是INTERNET,OTHER的情况)
                #return ret_res
                
                # 不同的WAN连接模式,其节点路径不同
                if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':
                    tmp_path3 = path2 + 'WANPPPConnection.'
                    # GCW 20130418 应该只区分是路由还是桥接
                    if AccessMode == "PPPoE_Bridged":
                        tmp_ConnectionType = "PPPoE_Bridged"
                    else:
                        tmp_ConnectionType = "IP_Routed"
                    tmp_X_CT_COM_LanInterface =  dict_wanpppconnection['X_CT-COM_LanInterface'][1]
                    tmp_X_CT_COM_ServiceList = dict_wanpppconnection['X_CT-COM_ServiceList'][1]
                    info = u"查到匹配的PVC或VLAN,开始调用GetParameterNames查询WANPPPConnection节点参数\n"
                elif AccessMode == 'DHCP' or AccessMode == 'Static':
                    tmp_path3 = path2 + 'WANIPConnection.'
                    # GCW 20130418 应该只区分是路由还是桥接
                    tmp_ConnectionType = "IP_Routed"
                    tmp_X_CT_COM_LanInterface = dict_wanipconnection['X_CT-COM_LanInterface'][1]
                    tmp_X_CT_COM_ServiceList = dict_wanipconnection['X_CT-COM_ServiceList'][1]
                    info = u"查到匹配的PVC或VLAN,开始调用GetParameterNames查询WANIPConnection节点参数\n"
                log.app_info (info)
                ret_data_scr += info
                
                #sleep(3)
                ret_tmp_path3 = []
                ret3, ret_data3 = u1.get_parameter_names(ParameterPath=tmp_path3, NextLevel=1)
                if (ret3 == ERR_SUCCESS):
                    info = u"查询成功,返回:%s\n" % ret_data3
                    log.app_info (info)
                    ret_data_scr += info
                    # GCW　20130329　解决部分CPE同时将当前路径返回的情况,将其删除
                    ret_data3 = DelOwnParameterNames(ret_data3, tmp_path3)
                    #返回有路径,则保存
                    if ret_data3['ParameterList'] != []:
                        for tmp_index in xrange(len(ret_data3['ParameterList'])):
                            ret_tmp_path3.append(ret_data3['ParameterList'][tmp_index]['Name'])
                else:
                    #对于失败的情况，直接退出
                    info = u"查询失败,返回:%s\n" % ret_data3
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                # 第2.2步,对于PPPOE查找X_CT-COM_ServiceList和Username值.
                # 由于贝曼有些版本只查X_CT-COM_ServiceList,或者查到Username相同与否不影响判断结果,
                # 所以目前只支持查X_CT-COM_ServiceList
                for i in xrange(len(ret_tmp_path3)):
                    info = u"开始调用GetParameterValues查询第%s个WAN连接的参数\n" % str(i+1)
                    log.app_info (info)
                    ret_data_scr += info
                    
                    tmp_path3_2 = []
                    tmp_path3_2.append(ret_tmp_path3[i] + 'ConnectionType')
                    tmp_path3_2.append(ret_tmp_path3[i] + 'X_CT-COM_LanInterface')
                    tmp_path3_2.append(ret_tmp_path3[i] + 'X_CT-COM_ServiceList')
                    #sleep(3)
                    ret3_2, ret_data3_2 = u1.get_parameter_values(ParameterNames=tmp_path3_2)
                    if (ret3_2 == ERR_SUCCESS):
                        info = u"查询成功\n"
                        log.app_info (info)
                        ret_data_scr += info
                        # 判断值是否相等,相等则不修改,直接走IGMP使能
                        # 解决部分CPE不按顺序返回ConnectionType\X_CT-COM_LanInterface\X_CT-COM_ServiceList节点值的情况 gcw 20130516
                        WAN_Flag_1 = 1
                        for j in xrange(3):
                            
                            if 'ConnectionType' in ret_data3_2['ParameterList'][j]['Name'].split("."):
                                if ret_data3_2['ParameterList'][j]['Value'] == tmp_ConnectionType:
                                    #WAN_Flag_1 = 1
                                    pass
                                else:
                                    # 路由和桥的区别时，需重新走新建WAN连接流程  GCW 20130506
                                    WAN_Flag_1 = 3
                                    break
                            elif 'X_CT-COM_LanInterface' in ret_data3_2['ParameterList'][j]['Name'].split("."):
                                if ret_data3_2['ParameterList'][j]['Value'] == tmp_X_CT_COM_LanInterface:
                                    #WAN_Flag_1 = 1
                                    pass
                                else:
                                    WAN_Flag_1 = 0
                                    #break
                            elif 'X_CT-COM_ServiceList' in ret_data3_2['ParameterList'][j]['Name'].split("."):
                                if ret_data3_2['ParameterList'][j]['Value'] == tmp_X_CT_COM_ServiceList:
                                    #WAN_Flag_1 = 1
                                    pass
                                else:
                                    WAN_Flag_1 = 0
                                    #break
                        #如果有一个不匹配,则修改WANPPPConnection节点下的值
                        if WAN_Flag_1 == 0:
                            #对于查到是INTERNET,而待下发的是OTHER的话,贝曼的处理是重新修改为"INTERNET,OTHER"
                            # GCW 20130401 以下处理虽然符合贝曼,但不合理.重新定义为以传参为准.
                            #for j in xrange(3):
                            #    if 'X_CT-COM_ServiceList' in ret_data3_2['ParameterList'][j]['Name'].split("."):
                            #        if ret_data3_2['ParameterList'][j]['Value'] != tmp_X_CT_COM_ServiceList:
                            #            tmp_X_CT_COM_ServiceList = 'INTERNET,OTHER'
                            
                            if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':
                                tmp_values = dict_wanpppconnection
                                info = u"查询到的值与用户工单中传参过来的有不相等情况,开始调用SetParameterValues修改WANPPPConnection参数\n"
                            else:
                                tmp_values = dict_wanipconnection
                                info = u"查询到的值与用户工单中传参过来的有不相等情况,开始调用SetParameterValues修改WANIPConnection参数\n"
                            log.app_info (info)
                            ret_data_scr += info
                            
                            #第三--四步:调用SetParameterValues设置WANPPPConnection参数：
                            path6 = ret_tmp_path3[i]
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
                            if para_list6 == []:
                                info = u"参数为空,请检查\n"
                                log.app_err (info)
                                ret_data_scr += info
                                return ret_res, ret_data_scr
                            
                            #sleep(3)  # must be ;otherwise exception
                            ret6, ret_data6 = u1.set_parameter_values(ParameterList=para_list6)
                            if (ret6 == ERR_SUCCESS):
                                info = u"修改参数成功\n"
                                log.app_info (info)
                                ret_data_scr += info
                                rebootFlag = int(ret_data6["Status"])
                                if (rebootFlag == 1):
                                    reboot_Yes = 1
                            else:
                                #对于失败的情况，直接返回失败
                                info = u"修改参数失败，错误原因：%s\n" % ret_data6
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
                        elif WAN_Flag_1 == 3:
                            WAN_Flag = 1   # 重置WAN_Flag标志位，走新建WAN连接流程
                        else:
                            info = u"查询到的值与用户工单中传参过来的相等,无需修改WAN连接参数\n"
                            log.app_info (info)
                            ret_data_scr += info
                    else:
                        info = u"查询失败,请检查\n"
                        log.app_err (info)
                        ret_data_scr += info
                        return ret_res, ret_data_scr
                
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
                    info = u"新建实例成功,返回实例号：%s\n" % instanceNum1
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
                    info = u"新建实例失败，错误原因：%s\n" % ret_data3
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                
                #第三--二步：新建WANIPConnection或WANPPPConnection实例
                #只有是桥模式和路由PPPOE时,才新建WANPPPConnection实例.暂时不考虑桥
                if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':
                    path4 = ROOT_PATH + instanceNum1 + '.WANPPPConnection.'
                    info = u"开始调用AddObject新建WANPPPConnection实例\n"
                    log.app_info (info)
                    ret_data_scr += info
                else:
                    path4 = ROOT_PATH + instanceNum1 + '.WANIPConnection.'
                    info = u"开始调用AddObject新建WANIPConnection实例\n"
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
                    #对于失败的情况，直接退出
                    info = u"新建实例失败，错误原因：%s\n" % ret_data4
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
                    info = u"参数为空,请检查\n"
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
                    info = u"参数为空,请检查\n"
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