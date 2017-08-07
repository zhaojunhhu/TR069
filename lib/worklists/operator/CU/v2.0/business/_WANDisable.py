# coding:utf-8

# -----------------------------rpc --------------------------
import os
from TR069.lib.common.error import *
from TR069.lib.users.user import UserRpc as User
from time import sleep
import TR069.lib.common.logs.log as log
import _Common

reload(_Common)
from _Common import *
import TR069.lib.worklists.worklistcfg as worklistcfg


def WANDisable(obj, sn, DeviceType, AccessMode,
               PVC_OR_VLAN,
               dict_wanpppconnection,
               dict_wanipconnection,
               change_account=1):
    """
    """
    ret_res = ERR_FAIL  # 脚本返回值,成功或失败.缺省失败
    ret_data_scr = ""  # 返回结果日志

    ROOT_PATH = "InternetGatewayDevice.WANDevice.1.WANConnectionDevice."
    for nwf in [1]:
        try:
            u1 = User(sn, ip=worklistcfg.AGENT_HTTP_IP, port=worklistcfg.AGENT_HTTP_PORT,
                      page=worklistcfg.WORKLIST2AGENT_PAGE, sender=KEY_SENDER_WORKLIST, worklist_id=obj.id_)
            reboot_Yes = 0

            # 第一步：调用GetParameterNames方法，查询WAN连接
            info = u"开始调用GetParameterNames方法，查询WAN连接\n"
            log.app_info(info)
            ret_data_scr += info

            # sleep(3)  # must be ;otherwise exception
            ret_root, ret_data_root = u1.get_parameter_names(ParameterPath=ROOT_PATH, NextLevel=1)
            if ret_root == ERR_SUCCESS:
                info = u"查询WAN连接成功\n"
                log.app_info(info)
                ret_data_scr += info
                # GCW　20130329　解决部分CPE同时将当前路径返回的情况,将其删除
                ret_data_root = DelOwnParameterNames(ret_data_root, ROOT_PATH)
            else:
                # 对于失败的情况，直接返回失败
                info = u"查询WAN连接失败,错误信息:%s\n" % ret_data_root
                log.app_err(info)
                ret_data_scr += info
                return ret_res, ret_data_scr

            # 第二步：逐个查找,对于A上行,查PVC,其他的则查VLAN
            # path2 = []
            path2 = ''  # 保存查到有相同的PVC或关键参数值的WAN连接路径
            path2_1 = ''  # 保存WANPPPConnection或WANIPConnection节点路径保存,后面修改参数时有用
            WAN_Flag = None
            # 直接调GetParameterValues  查PVC或VLAN
            for i in xrange(len(ret_data_root['ParameterList'])):
                tmp_path2 = ret_data_root['ParameterList'][i]['Name']
                # A上行是关心PVC，LAN上行是关心VLAN，PON上行也是关心VLAN
                if DeviceType == 'ADSL':
                    tmp_path2 = tmp_path2 + 'WANDSLLinkConfig.DestinationAddress'
                    info = u"开始调用GetParameterValues,查询第%s个WAN连接的PVC节点DestinationAddress值\n" % str(i + 1)
                elif DeviceType == 'LAN':
                    tmp_path2 = tmp_path2 + 'WANEthernetLinkConfig.X_CU_VLANIDMark'
                    info = u"开始调用GetParameterValues,查询第%s个WAN连接的VLAN节点X_CU_VLANIDMark值\n" % str(i + 1)
                elif DeviceType == 'EPON':
                    tmp_path2 = tmp_path2 + 'X_CU_VLAN'
                    info = u"开始调用GetParameterValues,查询第%s个WAN连接的VLAN节点X_CU_VLAN值\n" % str(i + 1)
                elif DeviceType == 'VDSL':
                    tmp_path2 = tmp_path2 + 'WANDSLLinkConfig.X_CU_VLAN'
                    info = u"开始调用GetParameterValues,查询第%s个WAN连接的VLAN节点X_CU_VLAN值\n" % str(i + 1)
                elif DeviceType == 'GPON':
                    tmp_path2 = tmp_path2 + 'X_CU_VLAN'
                    info = u"开始调用GetParameterValues,查询第%s个WAN连接的VLAN节点X_CU_VLAN值\n" % str(i + 1)
                else:
                    tmp_path2 = tmp_path2 + 'WANDSLLinkConfig.DestinationAddress'
                    info = u"开始调用GetParameterValues,查询第%s个WAN连接的PVC节点DestinationAddress值\n" % str(i + 1)
                log.app_info(info)
                ret_data_scr += info

                # sleep(3)
                ret2, ret_data2 = u1.get_parameter_values(ParameterNames=tmp_path2)
                if ret2 == ERR_SUCCESS:
                    info = u"查询成功,返回:%s\n" % ret_data2
                    log.app_info(info)
                    ret_data_scr += info
                    # 当返回的PVC与要绑定的相同时,标记WAN_Flag,走修改流程
                    if ret_data2['ParameterList'] == []:
                        pass
                    else:
                        # 如果查到PVC或VLAN相同，则标记
                        if ret_data2['ParameterList']:
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
                    # 对于失败的情况，直接返回错误
                    info = u"查询失败,错误信息%s\n" % ret_data2
                    log.app_err(info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr

            # 如果一直没有查到相同的,则没有对WAN_Flag标志位做过修改,则说明没有匹配的WAN连接实例
            if WAN_Flag == None:
                WAN_Flag = 1

            # 查不到匹配的PVC或VLAN,不做任何事情
            if WAN_Flag == 1:
                info = u"查不到匹配的PVC或VLAN,不执行删除WANConnectionDevice实例的操作\n"
                log.app_info(info)
                ret_data_scr += info
                pass
            elif WAN_Flag == 0:
                # 当查到有相匹配的PVC时的处理流程，则还需查WANPPPConnection下的三个节点是否一致
                # 如果完全一致,直接删除WAN连接实例,否则待完善
                # 不同的WAN连接模式,其节点路径不同
                if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':
                    info = u"开始调用GetParameterNames查询WANPPPConnection实例\n"
                    tmp_path3 = path2 + 'WANPPPConnection.'
                    # GCW 20130418 应该只区分是路由还是桥接
                    if AccessMode == "PPPoE_Bridged":
                        tmp_ConnectionType = "PPPoE_Bridged"
                    else:
                        tmp_ConnectionType = "IP_Routed"
                    tmp_X_CU_LanInterface = dict_wanpppconnection['X_CU_LanInterface'][1]
                    tmp_X_CU_ServiceList = dict_wanpppconnection['X_CU_ServiceList'][1]
                elif AccessMode == 'DHCP' or AccessMode == 'Static':
                    info = u"开始调用GetParameterNames查询WANIPConnection实例\n"
                    tmp_path3 = path2 + 'WANIPConnection.'
                    # GCW 20130418 应该只区分是路由还是桥接
                    tmp_ConnectionType = "IP_Routed"
                    tmp_X_CU_LanInterface = dict_wanipconnection['X_CU_LanInterface'][1]
                    tmp_X_CU_ServiceList = dict_wanipconnection['X_CU_ServiceList'][1]
                log.app_info(info)
                ret_data_scr += info

                # sleep(3)
                ret_tmp_path3 = []
                ret3, ret_data3 = u1.get_parameter_names(ParameterPath=tmp_path3, NextLevel=1)
                if ret3 == ERR_SUCCESS:
                    info = u"查询成功,返回%s\n" % ret_data3
                    log.app_info(info)
                    ret_data_scr += info
                    # GCW　20130329　解决部分CPE同时将当前路径返回的情况,将其删除
                    ret_data3 = DelOwnParameterNames(ret_data3, tmp_path3)
                    # 返回有路径,则保存
                    if ret_data3['ParameterList']:
                        for tmp_index in xrange(len(ret_data3['ParameterList'])):
                            ret_tmp_path3.append(ret_data3['ParameterList'][tmp_index]['Name'])
                else:
                    # 对于失败的情况，直接退出
                    info = u"查询失败,返回错误信息:%s\n" % ret_data3
                    log.app_err(info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                # 第2.2步,对于PPPOE查找X_CU_ServiceList和Username值.
                # 由于贝曼有些版本只查X_CU_ServiceList,或者查到Username相同与否不影响判断结果,
                # 所以目前只支持查X_CU_ServiceList
                for i in xrange(len(ret_tmp_path3)):
                    info = u"开始调用GetParameterValues查找第%s个WAN连接实例下的参数值\n" % str(i + 1)
                    log.app_err(info)
                    ret_data_scr += info

                    tmp_path3_2 = []
                    tmp_path3_2.append(ret_tmp_path3[i] + 'ConnectionType')
                    tmp_path3_2.append(ret_tmp_path3[i] + 'X_CU_ServiceList')

                    if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':

                        if dict_wanpppconnection['X_CU_LanInterface'][0] == 1:
                            tmp_path3_2.append(ret_tmp_path3[i] + 'X_CU_LanInterface')

                    elif AccessMode == 'DHCP' or AccessMode == 'Static':

                        if dict_wanipconnection['X_CU_LanInterface'][0] == 1:
                            tmp_path3_2.append(ret_tmp_path3[i] + 'X_CU_LanInterface')

                    # sleep(3)
                    ret3_2, ret_data3_2 = u1.get_parameter_values(ParameterNames=tmp_path3_2)
                    if ret3_2 == ERR_SUCCESS:
                        info = u"查找第%s个WAN连接实例下的参数值成功,返回:%s\n" % (str(i + 1), ret_data3_2)
                        log.app_info(info)
                        ret_data_scr += info

                        # 判断值是否相等,相等则直接删除WAN实例,否则就返回错误
                        WAN_Flag_1 = 0

                        for j in xrange(len(tmp_path3_2)):

                            if 'ConnectionType' in ret_data3_2['ParameterList'][j]['Name'].split("."):
                                if ret_data3_2['ParameterList'][j]['Value'] == tmp_ConnectionType:
                                    WAN_Flag_1 = 1
                                else:
                                    WAN_Flag_1 = 0
                                    break
                            elif 'X_CU_LanInterface' in ret_data3_2['ParameterList'][j]['Name'].split("."):
                                # 只要包含关系,就可认为是查到相等
                                # GCW 20130410 解决页面删除了绑定的LAN后导致此节点值为空的情况，不能执行split
                                # tmp_value = []
                                # tmp_value = ret_data3_2['ParameterList'][j]['Value'].split(',')
                                tmp_value = ret_data3_2['ParameterList'][j]['Value']
                                # GCW 20130413 手动页面删除绑定或工单中传参绑定为空时的异常处理。
                                if tmp_value == "" or tmp_value == None:
                                    if tmp_X_CU_LanInterface == "":
                                        # 两者均为空，则匹配成功
                                        WAN_Flag_1 = 1
                                    else:
                                        # 两者只要有一个不为空，则匹配为不相等
                                        WAN_Flag_1 = 0
                                        break
                                else:
                                    if tmp_X_CU_LanInterface == "":
                                        # 两者只要有一个不为空，则匹配为不相等
                                        WAN_Flag_1 = 0
                                        break
                                    else:
                                        if tmp_X_CU_LanInterface in tmp_value:
                                            WAN_Flag_1 = 1
                                        else:
                                            WAN_Flag_1 = 0
                                            break
                            elif 'X_CU_ServiceList' in ret_data3_2['ParameterList'][j]['Name'].split("."):
                                # 只要包含关系,就可认为是查到相等
                                # tmp_value = []
                                # tmp_value = ret_data3_2['ParameterList'][j]['Value'].split(',')
                                tmp_value = ret_data3_2['ParameterList'][j]['Value']
                                if tmp_X_CU_ServiceList in tmp_value:
                                    WAN_Flag_1 = 1
                                else:
                                    WAN_Flag_1 = 0
                                    break
                        # 如果有一个不匹配,则认为没有开通IGMP的WAN连接，无法删除
                        if WAN_Flag_1 == 0:
                            info = u"查到与工单中有不匹配的参数,无法删除WAN连接实例\n"
                            log.app_err(info)
                            ret_data_scr += info
                            # GCW 20130419 IPTV取消工单，如果查不到匹配的WAN连接也可以认为成功
                            # return ret_res, ret_data_scr
                        else:
                            # 删除WAN连接实例
                            info = u"准备删除WANConnectionDevice实例\n"
                            log.app_info(info)
                            ret_data_scr += info

                            tmp_path = ret_tmp_path3[i].split('.')
                            path = ''
                            for i in xrange(len(tmp_path) - 3):
                                path = path + tmp_path[i] + '.'

                            # sleep(3)  # must be ;otherwise exception
                            ret3, ret_data3 = u1.delete_object(
                                ObjectName=path)
                            if ret3 == ERR_SUCCESS:
                                info = u"删除WANConnectionDevice实例成功\n"
                                log.app_info(info)
                                ret_data_scr += info

                                rebootFlag = int(ret_data3["Status"])
                                if rebootFlag == 1:
                                    reboot_Yes = 1
                            else:
                                # 对于失败的情况，直接退出
                                info = u"删除WANConnectionDevice实例失败，错误原因：%s\n" % ret_data3
                                log.app_err(info)
                                ret_data_scr += info
                                return ret_res, ret_data_scr

            # 如果需要重启,则下发Reboot方法,目前采用静等待130S
            if reboot_Yes == 1:

                # sleep(130)
                ret, ret_data = reboot_wait_next_inform(u1)
                if ret != ERR_SUCCESS:
                    ret_data_scr += ret_data
                    break

            # 第七步：调用修改联通维护密码,目前密码固定为CUAdmin
            ret, ret_data = ChangeAccount_CU(obj, sn, change_account)
            if ret == ERR_FAIL:
                ret_data_scr += ret_data
                return ret, ret_data_scr
            else:
                ret_data_scr += ret_data

            ret_res = ERR_SUCCESS
        except Exception, e:
            log.app_err(str(e))
            ret_data_scr += str(e) + '\n'
            return ret_res, ret_data_scr

    return ret_res, ret_data_scr
