#coding:utf-8

# -----------------------------rpc --------------------------
import os
from TR069.lib.common.error import *
from TR069.lib.users.user import UserRpc as User
from time import sleep
import TR069.lib.common.logs.log as log 
from _Common import *
import  TR069.lib.worklists.worklistcfg as worklistcfg 

def WLANMulti(obj, sn, Num, dict_root, dict_WEPKey,
              dict_PreSharedKey,
              change_account=0,
              rollbacklist=[]):
    """      
    """
    ret_res = ERR_FAIL # 脚本返回值,成功或失败.缺省失败    
    ret_data_scr = "" # 返回结果日志
    
    #绑定tr069模板类型，暂时只定义为上行方式
    DeviceType = 'ADSL'
    

    ROOT_PATH = "InternetGatewayDevice.LANDevice.1.WLANConfiguration."
    for nwf in [1]:
        try:
            u1=User(sn, ip=worklistcfg.AGENT_HTTP_IP, port=worklistcfg.AGENT_HTTP_PORT, page=worklistcfg.WORKLIST2AGENT_PAGE, sender=KEY_SENDER_WORKLIST, worklist_id=obj.id_)
            reboot_Yes = 0
            
            #第一步：调用GetParameterNames方法，查找当前有几个无线实例
            info = u"开始调用GetParameterNames方法，查找当前无线实例\n"
            log.app_info (info)
            ret_data_scr += info
            
            para_list = []
            path = ROOT_PATH
            ret_root, ret_data1_root = u1.get_parameter_names(ParameterPath=path, NextLevel='1')
            #sleep(2)  # must be ;otherwise exception
            if (ret_root == ERR_SUCCESS):
                info = u"查找当前无线实例成功\n"
                log.app_info (info)
                ret_data_scr += info
                # GCW　20130329　解决部分CPE同时将当前路径返回的情况,将其删除
                ret_data1_root = DelOwnParameterNames(ret_data1_root, path)
            else:
                #对于失败的情况，如何处理?
                info = u"查找当前无线实例失败,返回错误:%s\n" % ret_data1_root
                log.app_err (info)
                ret_data_scr += info
                return ret_res, ret_data_scr  
                
            #第二步：直接增加N个实例。如果有个数超出范围的问题，则由CPE处理判断
            para_list = []
            path = ROOT_PATH
            path2 = []
            #将查到的实例号路径追加到列表中
            for i in xrange(len(ret_data1_root['ParameterList'])):
                path2.append(ret_data1_root['ParameterList'][i]['Name'])
            
            # 新建实例个数等于传参进来的个数减去查到已经存在的个数,但如要Num为0或者小于已有实例个数,则不需新建
            if (int(Num) > len(ret_data1_root['ParameterList'])):
                info = u"开始调用AddObject,增加无线实例\n"
                log.app_info (info)
                ret_data_scr += info
                
                for i in xrange(int(Num)-len(ret_data1_root['ParameterList'])):
                    ret_addobject, ret_data_addobject = u1.add_object(
                                       ObjectName=path)
                    #sleep(2)  # must be ;otherwise exception
                    if (ret_addobject == ERR_SUCCESS):
                        instanceNum1 = ret_data_addobject["InstanceNumber"]
                        path2.append(path + instanceNum1 + '.')
                        # GCW 20130327 增加回退机制
                        rollbacklist.append(path + instanceNum1 + '.')
                        info = u"增加无线实例成功,返回实例号：%s\n" % instanceNum1
                        log.app_info (info)
                        ret_data_scr += info
                        
                        rebootFlag = int(ret_data_addobject["Status"])
                        if (rebootFlag == 1):
                            reboot_Yes = 1
                    else:
                        #对于失败的情况，直接返回失败
                        info = u"增加无线实例失败，失败信息：%s\n" % ret_data_addobject
                        log.app_err (info)
                        ret_data_scr += info
                        return ret_res, ret_data_scr
            else:
                info = u"已经开通的无线实例个数大于或等于 %s\n" % str(Num)
                log.app_info (info)
                ret_data_scr += info
                
            # 第三步,使能X_CT-COM_APModuleEnable
            para_list = []
            info = u"开始调用SetParameterValues对各个无线实例的X_CT-COM_APModuleEnable进行使能\n"
            log.app_info (info)
            ret_data_scr += info
            
            for i in xrange(len(path2)):
                tmp_path = path2[i] + 'X_CT-COM_APModuleEnable'
                para_list.append(dict(Name=tmp_path, Value='1'))
            ret_root, ret_data_root = u1.set_parameter_values(ParameterList=para_list)
            #sleep(2)  # must be ;otherwise exception
            if (ret_root == ERR_SUCCESS):
                info = u"对所有无线实例的X_CT-COM_APModuleEnable进行使能成功\n"
                log.app_info (info)
                ret_data_scr += info
                rebootFlag = int(ret_data_root["Status"])
                if (rebootFlag == 1):
                    reboot_Yes = 1
            else:
                #对于失败的情况,直接返回错误
                info = u"对所有无线实例的X_CT-COM_APModuleEnable进行使能失败,返回错误:%s\n" % ret_data_root
                log.app_err (info)
                ret_data_scr += info
                return ret_res, ret_data_scr  

            # 第四步：对队列各个参数进行配置
            for i in xrange(len(path2)):
                info = u"对第%s个无线实例的参数进行配置\n" % str(i+1)
                log.app_info (info)
                ret_data_scr += info
                # 根据电信的抓包,SSID1不修改,SSID2为WEP,SSID3和SSID4为不加密
                if i == 0:
                    # 对WLAN1不做任何修改
                    info = u"根据业务流程,对第%s个无线实例的参数不做修改\n" % str(i+1)
                    log.app_info (info)
                    ret_data_scr += info
                    continue
                elif i == 1:
                    # WEP加密
                    para_list = []
                    path = path2[i]
                    for j in dict_root:
                        if dict_root[j][0] == 1:
                            tmp_path = path + j
                            para_list.append(dict(Name=tmp_path, Value=dict_root[j][1]))
                    if para_list == []:
                        info = u"参数为空,请检查\n"
                        log.app_err (info)
                        ret_data_scr += info
                        return ret_res, ret_data_scr  
                elif i == 2:
                    # 不加密码
                    para_list = []
                    path = path2[i]
                    tmp_path_1 = path + 'Enable'
                    tmp_path_2 = path + 'BeaconType'
                    para_list.append(dict(Name=tmp_path_1, Value='1'))
                    para_list.append(dict(Name=tmp_path_2, Value='None'))
                    # 继续循环,以便将WLAN4的参数一起追加下发
                    info = u"根据业务流程,对第%s个无线实例的参数进行保存,与下一个无线实例参数一起下发\n" % str(i+1)
                    log.app_info (info)
                    ret_data_scr += info
                    continue
                elif i == 3:
                    # 不加密
                    path = path2[i]
                    tmp_path_1 = path + 'Enable'
                    tmp_path_2 = path + 'BeaconType'
                    para_list.append(dict(Name=tmp_path_1, Value='1'))
                    para_list.append(dict(Name=tmp_path_2, Value='None'))
                
                #设置值
                ret_root, ret_data_root = u1.set_parameter_values(ParameterList=para_list)
                #sleep(2)  # must be ;otherwise exception
                if (ret_root == ERR_SUCCESS):
                    info = u"对第%s个无线实例的参数进行配置成功\n" % str(i+1)
                    log.app_info (info)
                    ret_data_scr += info
                    rebootFlag = int(ret_data_root["Status"])
                    if (rebootFlag == 1):
                        reboot_Yes = 1
                else:
                    #对于失败的情况，直接返回错误
                    info = u"对第%s个无线实例的参数进行配置失败,返回错误:%s\n" % (str(i+1), ret_data_root)
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr  
                
                # 如果是WLAN2,则设置WEP密钥
                if i == 1:
                    info =  u"对第%s个无线实例的WEP密钥进行配置\n" % str(i+1)
                    log.app_info (info)
                    ret_data_scr += info
                    if dict_root['WEPKeyIndex'][0] != 1:
                        info = u"传参时,字典中KEY索引没有打开,请检查\n"
                        log.app_err (info)
                        ret_data_scr += info
                        return ret_res, ret_data_scr    #KEY索引没有打开，不建议再判断索引值范围。
                    path_WEPKey = path2[i] + 'WEPKey.' + dict_root['WEPKeyIndex'][1] + '.WEPKey'
                    para_list = []
                    para_list.append(dict(Name=path_WEPKey, Value=dict_WEPKey['WEPKey'][1]))
                    #设置值
                    ret_WEPKey, ret_data_WEPKey = u1.set_parameter_values(ParameterList=para_list)
                    #sleep(1)  # must be ;otherwise exception
                    if (ret_WEPKey == ERR_SUCCESS):
                        info =  u"对第%s个无线实例的WEP密钥进行配置成功\n" % str(i+1)
                        log.app_info (info)
                        ret_data_scr += info
                        rebootFlag = int(ret_data_WEPKey["Status"])
                        if (rebootFlag == 1):
                            reboot_Yes = 1
                    else:
                        #对于失败的情况，直接返回错误
                        info =  u"对第%s个无线实例的WEP密钥进行配置失败,返回错误%s\n" % (str(i+1), ret_data_WEPKey)
                        log.app_info (info)
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

if __name__ == '__main__':
    pass
    test_script(sn="20130121009")