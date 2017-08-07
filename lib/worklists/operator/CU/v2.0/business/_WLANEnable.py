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


def WLANEnable(obj, sn, dict_ssid,
               change_account=1,
               rollbacklist=[]):
    """                        
    """
    ret_res = ERR_FAIL  # 脚本返回值,成功或失败.缺省失败
    ret_data_scr = ""  # 返回结果日志

    # 入参处理
    tmp_ssid = []
    for i in dict_ssid:
        if dict_ssid[i][0] == 1:
            tmp_ssid.append([dict_ssid[i][1], dict_ssid[i][2]])
    if tmp_ssid == []:
        info = u"工单传参数错误,请检查\n"
        log.app_info(info)
        ret_data_scr += info
        return ret_res, ret_data_scr

    WLAN_ROOT_PATH = "InternetGatewayDevice.LANDevice.1.WLANConfiguration."
    for nwf in [1]:
        try:
            u1 = User(sn, ip=worklistcfg.AGENT_HTTP_IP, port=worklistcfg.AGENT_HTTP_PORT,
                      page=worklistcfg.WORKLIST2AGENT_PAGE, sender=KEY_SENDER_WORKLIST, worklist_id=obj.id_)
            reboot_Yes = 0
            # 第一步：调用GetParameterNames方法，查找当前有几个无线实例
            info = u"开始调用GetParameterNames方法，查找当前无线实例个数\n"
            log.app_info(info)
            ret_data_scr += info

            para_list = []
            path = WLAN_ROOT_PATH
            ret_root, ret_data1_root = u1.get_parameter_names(ParameterPath=path, NextLevel='1')
            # sleep(2)  # must be ;otherwise exception
            if ret_root == ERR_SUCCESS:
                info = u"查找当前无线实例个数成功。\n"
                log.app_info(info)
                ret_data_scr += info
                # GCW　20130329　解决部分CPE同时将当前路径返回的情况,将其删除
                ret_data1_root = DelOwnParameterNames(ret_data1_root, path)
            else:
                # 对于失败的情况，直接返回失败
                info = u"查找当前无线实例失败.失败信息:%s \n。" % ret_data1_root
                log.app_err(info)
                ret_data_scr += info
                return ret_res, ret_data_scr

            para_list = []

            # 判断当前要启用或禁用的无线实例（SSID）是否存在，不存在则报错退出
            for i in xrange(len(tmp_ssid)):

                tmp_para_path = path + tmp_ssid[i][0]
                tmp_flag = False

                for j in xrange(len(ret_data1_root['ParameterList'])):

                    if ret_data1_root['ParameterList'][j]['Name'] in tmp_para_path:
                        para_list.append(dict(Name=tmp_para_path, Value=tmp_ssid[i][1]))
                        tmp_flag = True
                        break

                if tmp_flag == False:
                    # 对于失败的情况，直接返回失败
                    info = u"未查找到节点为 %s 的无线实例，请确认。\n" % tmp_para_path
                    log.app_err(info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr

            info = u"开始调用SetParameterValues设置无线实例启用或禁用。。。\n"
            log.app_info(info)
            ret_data_scr += info

            # 设置值
            ret_root, ret_data_root = u1.set_parameter_values(ParameterList=para_list)
            # sleep(2)  # must be ;otherwise exception
            if ret_root == ERR_SUCCESS:
                info = u"设置无线实例启用或禁用成功。\n"
                log.app_info(info)
                ret_data_scr += info
                rebootFlag = int(ret_data_root["Status"])
                if rebootFlag == 1:
                    reboot_Yes = 1
            else:
                # 对于失败的情况，直接返回错误
                info = u"设置无线实例启用或禁用失败，详细信息: \n" % ret_data_root
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
