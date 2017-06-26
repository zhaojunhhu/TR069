#coding:utf-8

# -----------------------------rpc --------------------------
import os
from TR069.lib.common.error import *
from TR069.lib.users.user import UserRpc as User
from time import sleep
import TR069.lib.common.logs.log as log 
from _Common import *
import  TR069.lib.worklists.worklistcfg as worklistcfg 

def Eagleeyes(obj, sn,DeviceType, AccessMode,
              PortMappingEnabled,
              dict_PortMapping,
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
                #对于失败的情况，直接返回错误
                info = u"查询WAN连接失败,错误信息:%s\n" % ret_data_root
                log.app_err (info)
                ret_data_scr += info
                return ret_res, ret_data_scr
                
            #第二步：逐个查找
            path2 = []
            for i in xrange(len(ret_data_root['ParameterList'])):
                tmp_path2 = ret_data_root['ParameterList'][i]['Name']
                #如果需绑定到PPPoE，则查WANPPPConnection节点。同理，如果以后是想绑定到静态WAN连接，则可以查另外的节点，可开放
                #A上行是关心PVC，LAN上行是关心VLAN，PON上行也是关心VLAN
                if AccessMode == 'PPPoE' or AccessMode == 'PPPoE_Bridged':
                    tmp_path2 = tmp_path2 + 'WANPPPConnection.'
                    info = u"开始调用GetParameterNames查找第%s条WAN连接WANPPPConnection实例\n" % str(i+1)
                elif AccessMode == 'DHCP' or AccessMode == 'Static':
                    tmp_path2 = tmp_path2 + 'WANIPConnection.'
                    info = u"开始调用GetParameterNames查找第%s条WAN连接WANIPConnection实例\n" % str(i+1)
                else:
                    info = u"参数错误,目前只支持PPPoE_Bridged\PPPoE\DHCP\Static\n"
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                
                log.app_info (info)
                ret_data_scr += info
                #sleep(3)
                ret2, ret_data2 = u1.get_parameter_names(ParameterPath=tmp_path2, NextLevel=1)
                if (ret2 == ERR_SUCCESS):
                    info = u"查找第%s条WAN连接实例成功\n" % str(i+1)
                    log.app_info (info)
                    ret_data_scr += info
                    # GCW　20130329　解决部分CPE同时将当前路径返回的情况,将其删除
                    ret_data2 = DelOwnParameterNames(ret_data2, tmp_path2)
                    #以下是只考虑返回值只有一个的情况.当然，空的时候则是什么也不做
                    if ret_data2['ParameterList'] == []:
                        pass
                    else:
                        for tmp_index in xrange(len(ret_data2['ParameterList'])):
                            path2.append(ret_data2['ParameterList'][tmp_index]['Name'])
                else:
                    #对于失败的情况，直接返回错误
                    info = u"查找第%s条WAN连接实例失败,错误信息: %s\n" % (str(i+1), ret_data2)
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
            #如果查到当前的WAN连接下，均没有WANPPPConnection实例，则说明不能绑定到PPPOE下，退出。
            #同理，如果是绑定到静态WAN连接，而WAN连接下没有实例号，则退出
            if path2 == []:
                info = u"遍历WAN连接实例结束,但无发现可用的Connection实例号,请检查\n"
                log.app_err (info)
                ret_data_scr += info
                return ret_res, ret_data_scr
            else:
                pass
            
            #第三步，然后对path2中的值进行循环查找，只要一查到INTERNET,则退出
            INTERNET_FLAG = False
            for i in xrange(len(path2)):
                info = u"开始调用GetParameterValues查找第%s个WAN连接实例下的ConnectionType和X_CT-COM_ServiceList值\n" % str(i+1)
                log.app_info (info)
                ret_data_scr += info
                # GCW 20130418 增加是路由还是桥的查找判断
                tmp_path3 = []
                tmp_path3.append(path2[i] + 'ConnectionType')
                tmp_path3.append(path2[i] + 'X_CT-COM_ServiceList')
                #sleep(3)
                ret3, ret_data3 = u1.get_parameter_values(ParameterNames=tmp_path3)
                if (ret3 == ERR_SUCCESS):
                    info = u"查找第%s个WAN连接实例下的ConnectionType和X_CT-COM_ServiceList值成功,返回:%s\n" % (str(i+1), ret_data3)
                    log.app_info (info)
                    ret_data_scr += info
                    #如果查到有INTERNET,同退出当前循环
                    # GCW 20130410 修改为包含于的关系即可
                    # GCW 20130418 增加对路由或桥的判断
                    if AccessMode == "PPPoE_Bridged":
                        ConnectionType = "PPPoE_Bridged"
                    else:
                        ConnectionType = "IP_Routed"
                    # 只有桥对桥，路由对路由对比才有意义。
                    if ConnectionType == ret_data3['ParameterList'][0]['Value'] or \
                       ConnectionType == ret_data3['ParameterList'][1]['Value']:
                        # 全球眼固定是绑定到包含INTERNET的WAN连接的
                        if 'INTERNET' in ret_data3['ParameterList'][0]['Value'] or \
                           'INTERNET' in ret_data3['ParameterList'][1]['Value']:
                            INTERNET_FLAG = True
                            #记录包含INTERNET的节点路径
                            path3 = path2[i]
                            break 
                else:
                    #对于失败的情况，直接返回错误
                    info = u"查找第%s个WAN连接实例下的X_CT-COM_ServiceList值失败,返回:%s\n" % (str(i+1), ret_data3)
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
            
            #如果一直都没有查到，怎么办？目前是直接返回失败
            if INTERNET_FLAG == False:
                info = u"经遍历查找,查无匹配的X_CT-COM_ServiceList包含INTERNET值的%s 连接,执行失败.\n" % AccessMode
                log.app_err (info)
                ret_data_scr += info
                return ret_res, ret_data_scr
            
            #第四步，调用GetParameterNames方法，查找端口映射中是否有实例
            info = u"开始调用GetParameterNames方法，查找端口映射中是否有实例\n"
            log.app_info (info)
            ret_data_scr += info
            #sleep(3)
            PortMapping_flag = 0
            GetParameterNames_path4 = path3 + 'PortMapping.'
            ret4, ret_data4 = u1.get_parameter_names(ParameterPath=GetParameterNames_path4, NextLevel=1)
            if (ret4 == ERR_SUCCESS):
                # GCW　20130329　解决部分CPE同时将当前路径返回的情况,将其删除
                ret_data4 = DelOwnParameterNames(ret_data4, GetParameterNames_path4)
                #如果查到有实例，则需查找是否所有参数一致,一致则不做任何修改,不一致则修改
                if ret_data4['ParameterList'] == []:
                    info = u"端口映射中没有实例\n"
                    log.app_info (info)
                    ret_data_scr += info
                    PortMapping_flag = 0  # 表示查无实例,后面需要新建
                else:
                    # 查到有实例,还需要判断是否与工单参数中的相同,相同才删除实例,否则也是不删
                    info = u"端口映射中已有实例\n"
                    log.app_info (info)
                    ret_data_scr += info
                    for j in xrange(len(ret_data4['ParameterList'])):
                        path = ret_data4['ParameterList'][j]['Name']
                        #sleep(3)
                        info = u"查找%s 下的参数，检查端口映射规则是否与工单中的完全一致\n" % path
                        log.app_info (info)
                        ret_data_scr += info
                        # 将字典中的追加,查找值然后进行比对
                        tmp_path = [] # 保存路径
                        tmp_Value = [] # 保存成对的参数,值
                        
                        for k in dict_PortMapping:
                            if dict_PortMapping[k][0] == 1:
                                tmp_path.append(path + k)
                                tmp_Value.append([k,dict_PortMapping[k][1]])
                        
                        ret4_2, ret_data4_2 = u1.get_parameter_values(ParameterNames=tmp_path)
                        if (ret4_2 == ERR_SUCCESS):
                            tmp = len(ret_data4_2['ParameterList'])                          
                            
                            # 判断所有值是否相等
                            for k in xrange(len(ret_data4_2['ParameterList'])):
                                tmpaa = ret_data4_2['ParameterList'][k]['Name']
                                for l in xrange(len(tmp_Value)):
                                    if tmp_Value[l][0] in ret_data4_2['ParameterList'][k]['Name'].split("."):
                                        if ret_data4_2['ParameterList'][k]['Value'] == tmp_Value[l][1]:
                                            PortMapping_flag = 1
                                            break
                                        else:
                                            PortMapping_flag = 0
                                            break
                                # GCW 20130410 参数不一致时，仍认为端口映射规则相同的问题
                                if PortMapping_flag == 0:
                                    break
                        else:
                            info = u"查找失败，退出工单执行\n"
                            log.app_info (info)
                            ret_data_scr += info
                            return ret_res, ret_data_scr
                        if PortMapping_flag == 1:
                            info = u"查找成功，且所有参数一致\n"
                            log.app_info (info)
                            ret_data_scr += info
                            path_4 = ret_data4['ParameterList'][j]['Name']
                            break
                        else:
                            info = u"查找成功，但此端口映射中的规则与工单中要求的不一致。\n"
                            log.app_info (info)
                            ret_data_scr += info
            else:
                #对于失败的情况，直接返回错误
                info = u"查找端口映射中是否有实例失败,错误信息:%s\n" % ret_data4
                log.app_info (info)
                ret_data_scr += info
                return ret_res, ret_data_scr
            
            # 如果是开通业务,则需新增实例并下发参数,如果是取消业务,则直接删除实例
            if PortMappingEnabled == 'Enable':
                #第五步，调用AddObject新建实例
                if PortMapping_flag == 0:
                    info = u"本工单是开通业务,且端口映射中查无实例或实例中参数不等,开始调用AddObject新建实例\n"
                    log.app_info (info)
                    ret_data_scr += info
                    path5 = GetParameterNames_path4
                    #sleep(3)  # must be ;otherwise exception
                    ret5, ret_data5 = u1.add_object(
                                        ObjectName=path5)
                    if (ret5 == ERR_SUCCESS):
                        instanceNum1 = ret_data5["InstanceNumber"]
                        info = u"新建端口映射实例成功,返回实例号：%s\n" % instanceNum1
                        log.app_info (info)
                        ret_data_scr += info
                        # GCW 20130327 增加回退机制
                        rollbacklist.append(path5 + instanceNum1 + '.')
                        rebootFlag = int(ret_data5["Status"])
                        if (rebootFlag == 1):
                            reboot_Yes = 1
                    else:
                        #对于失败的情况，直接返回错误
                        info = u"新建端口映射实例失败，错误原因：%s\n" % ret_data5
                        log.app_err (info)
                        ret_data_scr += info
                        return ret_res, ret_data_scr
                    
                    #第六步：调用SetParameterValues设置参数
                    info = u"开始调用SetParameterValues设置端口映射参数\n"
                    log.app_info (info)
                    ret_data_scr += info
                    path6 = path5 + instanceNum1 + '.'
                    para_list6 = []
                    for i in dict_PortMapping:
                        if dict_PortMapping[i][0] == 1:
                            tmp_path = path6 + i
                            para_list6.append(dict(Name=tmp_path, Value=dict_PortMapping[i][1]))
                    if para_list6 == []:
                        return ret_res, ret_data_scr
                    #sleep(3)  # must be ;otherwise exception
                    ret6, ret_data6 = u1.set_parameter_values(ParameterList=para_list6)
                    
                    if (ret6 == ERR_SUCCESS):
                        info = u"设置端口映射参数成功\n"
                        log.app_info (info)
                        ret_data_scr += info
                        rebootFlag = int(ret_data6["Status"])
                        if (rebootFlag == 1):
                            reboot_Yes = 1
                    else:
                        #对于失败的情况，直接返回错误
                        info = u"设置端口映射参数失败,错误信息:%s\n" % ret_data6
                        log.app_err (info)
                        ret_data_scr += info
                        return ret_res, ret_data_scr
                else:
                    info = u"本工单是开通业务,但已有端口映射规则且所有参数均相等。不再新建。\n"
                    log.app_info (info)
                    ret_data_scr += info
            elif PortMappingEnabled == 'Disable':
                #第五步，调用删除实例
                if PortMapping_flag == 1:
                    # 删除WAN连接实例
                    #log.app_info (u"删除PortMapping实例\n")
                    info = u"本工单是取消业务,在端口映射中查到实例且参数完全一致,开始调用DelObject删除PortMapping实例\n"
                    log.app_info (info)
                    ret_data_scr += info
                    path = path_4
                    #sleep(3)  # must be ;otherwise exception
                    ret5, ret_data5 = u1.delete_object(
                                        ObjectName=path)
                    if (ret5 == ERR_SUCCESS):
                        info = u"删除PortMapping实例成功\n"
                        log.app_info (info)
                        ret_data_scr += info
                        rebootFlag = int(ret_data5["Status"])
                        if (rebootFlag == 1):
                            reboot_Yes = 1
                    else:
                        #对于失败的情况，直接退出
                        info = u"删除PortMapping实例失败，错误原因：%s\n" % ret_data5
                        log.app_err (info)
                        ret_data_scr += info
                        return ret_res, ret_data_scr
                else:
                    info = u"本工单是取消业务,但查无所有参数均相等的实例可删除。\n"
                    log.app_info (info)
                    ret_data_scr += info
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