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
import  TR069.lib.worklists.worklistcfg as worklistcfg 


def WAN(obj, sn, DeviceType, AccessMode, change_or_enable, dict_pvcorvlan, change_account=1):
    """
    """
    ret_res = ERR_FAIL # 脚本返回值,成功或失败.缺省失败
    ret_data_scr = "" # 返回结果日志
    
    ROOT_PATH = "InternetGatewayDevice.WANDevice.1.WANConnectionDevice."
    
    # 将传参数过来的字典中有效的PVC或VLAN提取出来
    tmp_pvcorvlan = []
    for i in dict_pvcorvlan:
        if dict_pvcorvlan[i][0] == 1:
            tmp_pvcorvlan.append([dict_pvcorvlan[i][1], dict_pvcorvlan[i][2]])
    if tmp_pvcorvlan == []:
        info = u"工单传参数错误,请检查\n"
        log.app_info(info)
        ret_data_scr += info
        return ret_res, ret_data_scr
    
    for nwf in [1]:
        try:
            u1=User(sn, ip=worklistcfg.AGENT_HTTP_IP, port=worklistcfg.AGENT_HTTP_PORT, page=worklistcfg.WORKLIST2AGENT_PAGE, sender=KEY_SENDER_WORKLIST, worklist_id=obj.id_)
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

            # 第二步：逐个查找
            path2 = []
            para_list = []
            
            for i in xrange(len(ret_data_root['ParameterList'])):
                tmpflag = None
                tmp_path2 = ret_data_root['ParameterList'][i]['Name']
                # 下面的临时变量可以根据上行方式，WAN连接类型进行修改
                if DeviceType == 'ADSL':
                    tmp_path2_1 = tmp_path2 + 'WANDSLLinkConfig.DestinationAddress'
                    info = u"开始调用GetParameterValues,查询第%s个WAN连接的PVC节点DestinationAddress值\n" % str(i+1)
                elif DeviceType == 'LAN':
                    tmp_path2_1 = tmp_path2 + 'WANEthernetLinkConfig.X_CT-COM_VLANIDMark'
                    info = u"开始调用GetParameterValues,查询第%s个WAN连接的VLAN节点X_CT-COM_VLANIDMark值\n" % str(i+1)
                elif DeviceType == 'EPON':
                    tmp_path2_1 = tmp_path2 + 'X_CU_VLAN'
                    info = u"开始调用GetParameterValues,查询第%s个WAN连接的VLAN节点X_CU_VLAN值\n" % str(i+1)
                elif DeviceType == 'VDSL':
                    tmp_path2_1 = tmp_path2 + 'WANDSLLinkConfig.X_CT-COM_VLAN'
                    info = u"开始调用GetParameterValues,查询第%s个WAN连接的VLAN节点X_CT-COM_VLAN值\n" % str(i+1)
                elif DeviceType == 'GPON':
                    tmp_path2_1 = tmp_path2 + 'X_CU_VLAN'
                    info = u"开始调用GetParameterValues,查询第%s个WAN连接的VLAN节点X_CU_VLAN值\n" % str(i+1)
                else:
                    tmp_path2_1 = tmp_path2 + 'WANDSLLinkConfig.DestinationAddress'
                    info = u"开始调用GetParameterValues,查询第%s个WAN连接的PVC节点DestinationAddress值\n" % str(i+1)
                log.app_err(info)
                ret_data_scr += info
                
                # sleep(3)
                ret2, ret_data2 = u1.get_parameter_values(ParameterNames=tmp_path2_1)
                if ret2 == ERR_SUCCESS:
                    info = u"查询成功,返回:%s \n" % ret_data2
                    log.app_err(info)
                    ret_data_scr += info
                    # 当返回的PVC或VLAN与需要查找的相等时，处理;查到为空则继续往下
                    if ret_data2['ParameterList']:
                        for j in xrange(len(tmp_pvcorvlan)):    
                            # 如果查到PVC相同，则标记;
                            if ret_data2['ParameterList'][0]['Value'] == tmp_pvcorvlan[j][0]:
                                # 查到有匹配PVC
                                tmpflag = True
                                tmp_enable_or_change_value = tmp_pvcorvlan[j][1]
                                # 将相应的PVC和Enable状态值删除
                                tmp_pvcorvlan.remove(tmp_pvcorvlan[j])
                                break
                            else:
                                # 查不到匹配的PVC
                                tmpflag = False
                                
                        if tmpflag != None:
                            # 查实例号.
                            if AccessMode == 'PPPoE' or AccessMode == "PPPoE_Bridged" :
                                tmp_path2_2 = tmp_path2 + 'WANPPPConnection.'
                                info = u"开始调用GetParameterValues查找WANPPPConnection节点下的实例号\n"
                            else:
                                tmp_path2_2 = tmp_path2 + 'WANIPConnection.'
                                info = u"开始调用GetParameterValues查找WANIPConnection节点下的实例号\n"
                            log.app_info(info)
                            ret_data_scr += info
                            
                            # sleep(3)
                            ret3, ret_data3 = u1.get_parameter_names(ParameterPath=tmp_path2_2, NextLevel=1)
                            if ret3 == ERR_SUCCESS:
                                # GCW　20130329　解决部分CPE同时将当前路径返回的情况,将其删除
                                ret_data3 = DelOwnParameterNames(ret_data3, tmp_path2_2)
                                
                                # 当返回的PVC或VLAN与要绑定的相同时，待完善
                                # GCW 20130410 解决当查到为空时，无tmp_path2_3值而导致异常
                                tmp_path2_3 = []
                                if ret_data3['ParameterList'] == []:
                                    info = u"查找成功,返回为空。\n"
                                else:
                                    # 如果查到PVC相同，则标记，(手动可能多实例的情况)
                                    # tmp_path2_3 = []  # 移到外层定义，避免在if中无定义上起后面问题
                                    for i in xrange(len(ret_data3['ParameterList'])):
                                        tmp_path2_3.append(ret_data3['ParameterList'][i]['Name'])
                                    info = u"查找成功,返回为:%s \n" % tmp_path2_3
                                log.app_info(info)
                                ret_data_scr += info
                        if tmpflag == True:
                            # 如果是启用禁用PVC,则将使能路径和值追加,如果是修改PVC,则将WAN实例和PVC值追加
                            if change_or_enable == 'Enable':
                                for i in xrange(len(tmp_path2_3)):
                                    para_list.append(dict(Name=tmp_path2_3[i] + 'Enable', Value=tmp_enable_or_change_value))
                            elif change_or_enable == 'Change':
                                para_list.append(dict(Name=tmp_path2_1, Value=tmp_enable_or_change_value))
                            else:
                                info = u"参数错误.目前只支持启用禁用PVC(VLAN)或修改PVC(VLAN).\n"
                                log.app_info(info)
                                ret_data_scr += info
                                return ret_res, ret_data_scr
                else:
                    # 对于失败的情况，直接返回错误
                    info = u"查询失败,错误信息%s \n" % ret_data2
                    log.app_err(info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                
            # 只要还有一个PVC没有查到，则失败，退出
            if len(tmp_pvcorvlan) != 0:
                info = u"有未查到的PVC或VLAN,请检查\n"
                log.app_info(info)
                ret_data_scr += info
                return ret_res, ret_data_scr

            # 第四步，禁用或启用相应的PVC
            info = u"开始调用SetParameterValues设置相应WAN连接的参数\n"
            log.app_info(info)
            ret_data_scr += info
            # sleep(3)
            ret4, ret_data4 = u1.set_parameter_values(ParameterList=para_list)
            if ret4 == ERR_SUCCESS:
                info = u"设置参数成功\n"
                log.app_info(info)
                ret_data_scr += info
                rebootFlag = int(ret_data4["Status"])
                if rebootFlag == 1:
                    reboot_Yes = 1
            else:
                # 对于失败的情况，直接返回错误
                info = u"设置参数失败，错误原因：%s\n" % ret_data4
                log.app_info(info)
                ret_data_scr += info
                return ret_res, ret_data_scr
            
            # 如果需要重启,则下发Reboot方法,目前采用静等待130S
            if reboot_Yes == 1:

                # sleep(130)
                ret, ret_data = reboot_wait_next_inform(u1)
                if ret != ERR_SUCCESS:
                    ret_data_scr += ret_data
                    break
                
            # 调用修改联通维护密码,目前密码固定为CUAdmin
            ret, ret_data = ChangeAccount_CU(obj, sn, change_account)
            if ret == ERR_FAIL:
                ret_data_scr += ret_data
                return ret, ret_data_scr
            else:
                ret_data_scr += ret_data
                
            ret_res = ERR_SUCCESS
        except Exception, e:
            log.app_err(str(e))
            ret_data_scr += str(e)+'\n'
            return ret_res, ret_data_scr
    
    return ret_res, ret_data_scr          

if __name__ == '__main__':
    pass
    test_script(sn="20130121009")
