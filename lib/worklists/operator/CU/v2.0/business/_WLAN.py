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


def WLAN(obj, sn, Num, dict_root,
         dict_WEPKey, dict_PreSharedKey,
         change_account=1,
         rollbacklist=[]):
    """                        
    """
    ret_res = ERR_FAIL  # 脚本返回值,成功或失败.缺省失败
    ret_data_scr = ""  # 返回结果日志

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
                info = u"查找当前无线实例个数成功\n"
                log.app_info(info)
                ret_data_scr += info
                # GCW　20130329　解决部分CPE同时将当前路径返回的情况,将其删除
                ret_data1_root = DelOwnParameterNames(ret_data1_root, path)
            else:
                # 对于失败的情况，直接返回失败
                info = u"查找当前无线实例失败.失败信息:%s\n" % ret_data1_root
                log.app_err(info)
                ret_data_scr += info
                return ret_res, ret_data_scr

            # 第二步：判断是否需要增加实例,如果不需要,则直接进入下一步的修改设置
            para_list = []
            path = WLAN_ROOT_PATH
            path2 = []
            # 将查到的实例号路径追加到列表中
            for i in xrange(len(ret_data1_root['ParameterList'])):
                path2.append(ret_data1_root['ParameterList'][i]['Name'])

            # 新建实例个数等于传参进来的个数减去查到已经存在的个数,但如要Num为0或者小于已有实例个数,则不需新建
            if int(Num) > len(ret_data1_root['ParameterList']):
                info = u"开始调用AddObject,增加无线实例\n"
                log.app_info(info)
                ret_data_scr += info
                for i in xrange(int(Num) - len(ret_data1_root['ParameterList'])):
                    ret_addobject, ret_data_addobject = u1.add_object(
                        ObjectName=path)

                    # sleep(2)  # must be ;otherwise exception
                    if ret_addobject == ERR_SUCCESS:
                        instanceNum1 = ret_data_addobject["InstanceNumber"]
                        path2.append(path + instanceNum1 + '.')
                        info = u"增加无线实例成功,返回实例号：%s\n" % instanceNum1
                        log.app_info(info)
                        ret_data_scr += info
                        # GCW 20130327 增加回退机制
                        rollbacklist.append(path + instanceNum1 + '.')
                        rebootFlag = int(ret_data_addobject["Status"])
                        if rebootFlag == 1:
                            reboot_Yes = 1
                    else:
                        # 对于失败的情况，直接返回失败
                        info = u"增加无线实例失败，失败信息：%s\n" % ret_data_addobject
                        log.app_err(info)
                        ret_data_scr += info
                        return ret_res, ret_data_scr
            else:
                info = u"已经开通的无线实例个数大于或等于 %s\n" % str(Num)
                log.app_info(info)
                ret_data_scr += info

            # 第三步：对队列各个参数进行配置
            for i in xrange(len(path2)):
                info = u"开始调用SetParameterValues对第%s个无线实例进行配置\n" % str(i + 1)
                log.app_info(info)
                ret_data_scr += info
                if dict_root['BeaconType'][1] == 'None':
                    # 不加密的情况
                    para_list = []
                    path = path2[i]
                    for j in dict_root:
                        if dict_root[j][0] == 1:
                            tmp_path = path + j
                            para_list.append(dict(Name=tmp_path, Value=dict_root[j][1]))
                    if para_list == []:
                        return ret_res, ret_data_scr
                elif dict_root['BeaconType'][1] == 'Basic':
                    # WEP加密的情况
                    para_list = []
                    path = path2[i]
                    for j in dict_root:
                        if dict_root[j][0] == 1:
                            tmp_path = path + j
                            para_list.append(dict(Name=tmp_path, Value=dict_root[j][1]))
                    if para_list == []:
                        return ret_res, ret_data_scr
                elif dict_root['BeaconType'][1] == 'WPA':
                    # WPA加密的情况
                    para_list = []
                    path = path2[i]
                    for j in dict_root:
                        if dict_root[j][0] == 1:
                            tmp_path = path + j
                            para_list.append(dict(Name=tmp_path, Value=dict_root[j][1]))

                    # dict_PreSharedKey节点下的密钥也一起下发
                    path_PreSharedKey = path + 'PreSharedKey.1.'
                    for j in dict_PreSharedKey:
                        if dict_PreSharedKey[j][0] == 1:
                            tmp_path = path_PreSharedKey + j
                            para_list.append(dict(Name=tmp_path, Value=dict_PreSharedKey[j][1]))
                    if para_list == []:
                        info = u"选择了WPA加密,但没有使能密钥的传参\n"
                        log.app_err(info)
                        ret_data_scr += info
                        return ret_res, ret_data_scr
                else:
                    # 其它的待完善.同时，需考虑在elif中兼容其它的方式
                    pass

                # 设置值
                ret_root, ret_data_root = u1.set_parameter_values(ParameterList=para_list)
                # sleep(2)  # must be ;otherwise exception
                if ret_root == ERR_SUCCESS:
                    info = u"第%s个无线实例的参数配置成功\n" % str(i + 1)
                    log.app_info(info)
                    ret_data_scr += info
                    rebootFlag = int(ret_data_root["Status"])
                    if rebootFlag == 1:
                        reboot_Yes = 1
                else:
                    # 对于失败的情况，直接返回错误
                    info = u"第%s个无线实例的参数配置失败,失败信息：%s\n" % (str(i + 1), ret_data_root)
                    log.app_err(info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr

                # 如果是WEP加密，则还需要设置KEY
                if dict_root['BeaconType'][1] == 'Basic':
                    info = u"开始调用SetParameterValues对第%s个无线实例的WEP密钥进行配置\n" % str(i + 1)
                    log.app_info(info)
                    ret_data_scr += info
                    if dict_root['WEPKeyIndex'][0] != 1:
                        ret_data_scr += u"选择了WEP加密,但没有使能KEY索引的传参\n"
                        return ret_res, ret_data_scr  # KEY索引没有打开，不建议再判断索引值范围。
                    path_WEPKey = path2[i] + 'WEPKey.' + dict_root['WEPKeyIndex'][1] + '.WEPKey'
                    para_list = []
                    para_list.append(dict(Name=path_WEPKey, Value=dict_WEPKey['WEPKey'][1]))
                    # 设置值
                    ret_WEPKey, ret_data_WEPKey = u1.set_parameter_values(ParameterList=para_list)
                    # sleep(1)  # must be ;otherwise exception
                    if ret_WEPKey == ERR_SUCCESS:
                        info = u"对第%s个无线实例的WEP密钥进行配置成功\n" % str(i + 1)
                        log.app_info(info)
                        ret_data_scr += info
                        rebootFlag = int(ret_data_WEPKey["Status"])
                        if rebootFlag == 1:
                            reboot_Yes = 1
                    else:
                        # 对于失败的情况，直接返回错误
                        info = u"对第%s个无线实例的WEP密钥进行配置失败,失败信息:%s\n" % (str(i + 1), ret_data_WEPKey)
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
