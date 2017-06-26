#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: _Common
#  function: ChangeAccount,修改电信维护帐号密码
#            ParseLANName,重构GUI或RF传参过来的LAN1,WLan2等格式的参数
#  Author: ATT development group
#  version: V1.0
#  date: 2013.03.21
#  change log:
#  
# ***************************************************************************

import os
import random
from TR069.lib.common.error import *
from TR069.lib.common.event import *
from TR069.lib.users.user import UserRpc as User
from TR069.lib.users.user import wait_next_inform, update_cpe_info
from time import sleep
import TR069.lib.common.logs.log as log 
import  TR069.lib.worklists.worklistcfg as worklistcfg 


def ChangeAccount(obj, sn, change_account=1):
    """
    功能描述: 更改电信维护密码
    """
    ret_res = ERR_FAIL # 脚本返回值,成功或失败.缺省失败
    ret_data_scr = ""  # 返回结果日志
    u1=User(sn, ip=worklistcfg.AGENT_HTTP_IP, port=worklistcfg.AGENT_HTTP_PORT, page=worklistcfg.WORKLIST2AGENT_PAGE, sender=KEY_SENDER_WORKLIST, worklist_id=obj.id_)
    
    # 调用修改电信维护密码,参照贝曼随机生成
    para_list = []
    password = random.randrange(10000000,99999999)
    password = "telecomadmin" + str(password)
    para_list.append(dict(Name='InternetGatewayDevice.DeviceInfo.X_CT-COM_TeleComAccount.Enable', 
                                         Value='1'))
    para_list.append(dict(Name='InternetGatewayDevice.DeviceInfo.X_CT-COM_TeleComAccount.Password', 
                                         Value=password))
    for nwf in [1]:
        try:
            # 贝曼的报文显示延时2S即下发修改帐号OK.但我们这个平台延时需较长才能组包完成.
            if change_account == 1:
                #sleep(10) 
                info = u"调用SetParameterValues设置参数,修改电信维护密码\n"
                log.app_info (info)
                ret_data_scr += info
                
                ret, ret_data = u1.set_parameter_values(ParameterList=para_list)
                if (ret == ERR_SUCCESS):
                    info = u"修改电信维护密码成功.密码为:%s\n" % password
                    log.app_info (info)
                    ret_data_scr += info
                else:
                    #对于失败的情况，直接返回失败
                    info = u"修改电信维护密码失败，退出执行，错误原因：%s\n" % ret_data
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
            else:
                info = u"无需修改电信维护密码\n"
                log.app_info (info)
                ret_data_scr += info
            ret_res = ERR_SUCCESS
        except Exception, e:
            log.app_err (str(e))
            ret_data_scr += str(e)+'\n'
            return ret_res, ret_data_scr  
    
    return ret_res, ret_data_scr        

def ParseLANName(LanName):
    """
    功能描述: 重构GUI或RF传参过来的LAN1,WLan2等格式的参数
    
    参数：
        LanName:字符串,需绑定的LAN或WLAN接口,以逗号分隔.不区分大小写.
    
    返回值：tr069的LAN或WLAN接口的路径
    
    Example:
        ParseLANName('LAn1,Wlan2,lan3,LAN4')
    """
    ret_res = ERR_FAIL # 脚本返回值,成功或失败.缺省失败
    ret_value = ""    
    tmp_value = ""
    for i in LanName.split(","):
        if (i.upper() == 'LAN1' or
            i.upper() == 'InternetGatewayDevice.LANDevice.1.LANEthernetInterfaceConfig.1'.upper()) :
            tmp_value += 'InternetGatewayDevice.LANDevice.1.LANEthernetInterfaceConfig.1' + ','
        elif (i.upper() == 'LAN2' or
              i.upper() == 'InternetGatewayDevice.LANDevice.1.LANEthernetInterfaceConfig.2'.upper()) :
            tmp_value += 'InternetGatewayDevice.LANDevice.1.LANEthernetInterfaceConfig.2' + ','
        elif (i.upper() == 'LAN3' or
              i.upper() == 'InternetGatewayDevice.LANDevice.1.LANEthernetInterfaceConfig.3'.upper()) :
            tmp_value += 'InternetGatewayDevice.LANDevice.1.LANEthernetInterfaceConfig.3' + ','
        elif (i.upper() == 'LAN4' or
              i.upper() == 'InternetGatewayDevice.LANDevice.1.LANEthernetInterfaceConfig.4'.upper()) :
            tmp_value += 'InternetGatewayDevice.LANDevice.1.LANEthernetInterfaceConfig.4' + ','
        elif (i.upper() == 'WLAN1' or
              i.upper() == 'InternetGatewayDevice.LANDevice.1.WLANConfiguration.1'.upper()) :
            tmp_value += 'InternetGatewayDevice.LANDevice.1.WLANConfiguration.1' + ','
        elif (i.upper() == 'WLAN2' or
              i.upper() == 'InternetGatewayDevice.LANDevice.1.WLANConfiguration.2'.upper()):
            tmp_value += 'InternetGatewayDevice.LANDevice.1.WLANConfiguration.2' + ','
        elif (i.upper() == 'WLAN3' or
              i.upper() == 'InternetGatewayDevice.LANDevice.1.WLANConfiguration.4'.upper()):
            tmp_value += 'InternetGatewayDevice.LANDevice.1.WLANConfiguration.3' + ','
        elif (i.upper() == 'WLAN4' or
              i.upper() == 'InternetGatewayDevice.LANDevice.1.WLANConfiguration.4'.upper()):
            tmp_value += 'InternetGatewayDevice.LANDevice.1.WLANConfiguration.4' + ','
        elif i == "":
            ret_res = ERR_SUCCESS
            tmp_value = ""
            return ret_res, tmp_value
        else:
            return ret_res, tmp_value
    
    # 去掉最后一个逗号
    for i in tmp_value.split(','):
        if ret_value == "":
            ret_value += i
        elif i == '':
            break
        else:
            ret_value += ',' + i
   
    ret_res = ERR_SUCCESS
    return ret_res, ret_value

def rollback(sn, rollbacklist, obj):
    ret_res = ERR_FAIL # 脚本返回值,成功或失败.缺省失败
    ret_data_scr = ""

    enable = obj.rollback
    
    u1=User(sn, ip=worklistcfg.AGENT_HTTP_IP, port=worklistcfg.AGENT_HTTP_PORT, page=worklistcfg.WORKLIST2AGENT_PAGE, sender=KEY_SENDER_WORKLIST, worklist_id=obj.id_)
    for att in [1]:
        if enable == False or enable == "False" :
            break
        try:
            if len(rollbacklist) == 0:
                break
            info = u"开始执行回退操作......\n"
            log.app_info (info)
            ret_data_scr += info
            for i in rollbacklist:
                #sleep(5)
                ret, ret_data = u1.delete_object(ObjectName=i)
                if ret == ERR_SUCCESS:
                    
                    info = u"删除实例 %s 成功\n" % i
                    log.app_info (info)
                    ret_data_scr += info
                else:
                    info = u"删除实例 %s 失败,错误信息:%s\n" % (i, ret_data)
                    log.app_err (info)
                    ret_data_scr += info
                    continue   # 删除实例失败时，仍然继续去执行删除后面的实例．
        except Exception, e:
            log.app_err (str(e))
            ret_data_scr += str(e)+'\n'
            return ret_res, ret_data_scr
        

    ret_res = ERR_SUCCESS
    return ret_res, ret_data_scr

def DelOwnParameterNames(ret_of_get_parameter_names, path):
    """
    删除GetParameterNames方法查询path时,删除返回的字典中包含的path本身.
    """
    if ret_of_get_parameter_names['ParameterList'] != []:
        tmp_index = ""
        for index in xrange(len(ret_of_get_parameter_names['ParameterList'])):
            if ret_of_get_parameter_names['ParameterList'][index]['Name'] == path:
                tmp_index = index
        if tmp_index != "":
            del ret_of_get_parameter_names['ParameterList'][tmp_index]
            
    return ret_of_get_parameter_names


def reboot_wait_next_inform(u1):
    """
    u1 = UserRpc
    """
    
    ret_datas = ""
    sn = u1.sn

    for nwf in [1]:
    
        info = u"need reboot, begin reboot\n"
        log.app_info (info)
        ret_datas += info

        ret, ret_data = u1.reboot()        
        if (ret == ERR_SUCCESS):
            info = u"reboot success, wait max %s seconds.......\n" %(worklistcfg.REBOOT_WAIT_NEXT_INFORM_TIMEOUT)                        
        else:
            info = u"reboot fail: %s\n" % ret_data

        ret_datas += info
        log.app_info (info)

        # nwf 2013-07-12
        #sleep(130)
        ret, ret_data = wait_next_inform(sn, worklistcfg.REBOOT_WAIT_NEXT_INFORM_TIMEOUT)
        if (ret == ERR_SUCCESS):
            info = "wait_next_inform success."
        else:
            info = "wait_next_inform fail: %s\n" %ret_data
            
        ret_datas += info
        log.app_info (info)

    return ret, ret_datas


def get_random_8str(old):

    new_str = ""
    
    # nwf 2013-07-09;  password =old + xxxxxxxx[8]
    str8 = str(random.randrange(10000000,99999999))
    
    old8 = old[-8:]
    if (old8.isdigit() and (len(old8) == 8)):
        old8_pre = old[:-8]            

        # nwf 2013-07-26; random is the same as old?
        for nwf in range(3):
            if (old8 == str8):
                str8 = str(random.randrange(10000000,99999999))
            else:
                break        
        new_str = old8_pre + str8   # replace
    else:           
        new_str = old + str8        # concat
        
    return new_str



def update_username_password_to_acs(sn, Username="", Password="", ConnectionRequestUsername="", ConnectionRequestPassword=""):
    """
    obj = MsgWorklistExecute
    worklist修改了认证密码 需要通知到ACS，否则后续的RPC认证会失败
    """
    
    d1 = {}
    if (Username):
        d1["acs_auth_cpe_username"] = Username
    if (Password):
        d1["acs_auth_cpe_password"] = Password
    if (ConnectionRequestUsername):
        d1["cpe_auth_acs_username"] = ConnectionRequestUsername
    if (ConnectionRequestPassword):
        d1["cpe_auth_acs_password"] = ConnectionRequestPassword        

    info = u"修改的用户名 密码信息=%s" %d1
    log.app_info (info)
            
    ret, ret_data = update_cpe_info(sn, d1)    

    return ret, ret_data