#coding:utf-8


# -----------------------------rpc --------------------------
import os
import sys

DEBUG_UNIT = False
if (DEBUG_UNIT):
    g_prj_dir = os.path.dirname(__file__)
    parent1 = os.path.dirname(g_prj_dir)
    parent2 = os.path.dirname(parent1)
    parent3 = os.path.dirname(parent2)
    parent4 = os.path.dirname(parent3)  # tr069v3\lib
    parent5 = os.path.dirname(parent4)  # tr069v3\
    sys.path.insert(0, parent4)
    sys.path.insert(0, os.path.join(parent4, 'common'))
    sys.path.insert(0, os.path.join(parent4, 'worklist'))
    sys.path.insert(0, os.path.join(parent4, 'usercmd'))
    sys.path.insert(0, os.path.join(parent5, 'vendor'))
from TR069.lib.common.event import *
from TR069.lib.common.error import *
from time import sleep
import TR069.lib.common.logs.log as log 

g_prj_dir = os.path.dirname(__file__)
parent1 = os.path.dirname(g_prj_dir)
parent2 = os.path.dirname(parent1) # dir is system
try:
    i = sys.path.index(parent2)
    if (i !=0):
        # stratege= boost priviledge
        sys.path.pop(i)
        sys.path.insert(0, parent2)
except Exception,e: 
    sys.path.insert(0, parent2)

import _Common
reload(_Common)
from _Common import *
import _WLANMulti
reload(_WLANMulti)
from _WLANMulti import WLANMulti
import _WLANMultiWANSetUP
reload(_WLANMultiWANSetUP)
from _WLANMultiWANSetUP import WLANMultiWANSetUP

def test_script(obj):
    """
    """
    sn = obj.sn # 取得SN号
    DeviceType = "ADSL"  # 绑定tr069模板类型.只支持ADSL\LAN\EPON三种
    rollbacklist = []  # 存储工单失败时需回退删除的实例.目前缺省是不开启回退
    # 初始化日志
    obj.dict_ret.update(str_result=u"开始执行工单:%s........\n" %
                        os.path.basename(os.path.dirname(__file__)))
    
    # data传参
    WEPKeyIndex = obj.dict_data.get("WEPKeyIndex")[0]
    WEPEncryptionLevel = obj.dict_data.get("WEPEncryptionLevel")[0]
    WEPKey = obj.dict_data.get("WEPKey")[0]    
    # WAN部分参数
    PVC_OR_VLAN1 = obj.dict_data.get("PVC_OR_VLAN1")[0]
    PVC_OR_VLAN2 = obj.dict_data.get("PVC_OR_VLAN2")[0]
    PVC_OR_VLAN3 = obj.dict_data.get("PVC_OR_VLAN3")[0]
    PVC_OR_VLAN4 = obj.dict_data.get("PVC_OR_VLAN4")[0]
    Username1 = obj.dict_data.get("Username1")[0]
    Password1 = obj.dict_data.get("Password1")[0]
    Username2 = obj.dict_data.get("Username2")[0]
    Password2 = obj.dict_data.get("Password2")[0]
    WANEnable_Switch = obj.dict_data.get("WANEnable_Switch")[0]
    
    # WLAN个数
    Num = 4
    BeaconType = 'Basic' 
    BasicAuthenticationMode = 'Both'
    
    # LANDevice.{i}.WLANConfiguration.{i}.节点参数
    dict_root = {'X_CT-COM_SSIDHide':[0, 'Null'],
                 'X_CT-COM_RFBand':[0, 'Null'], 
                 'X_CT-COM_ChannelWidth':[0, 'Null'],
                 'X_CT-COM_GuardInterval':[0, 'Null'], 
                 'X_CT-COM_RetryTimeout':[0, 'Null'],
                 'X_CT-COM_Powerlevel':[0, 'Null'], 
                 'X_CT-COM_PowerValue':[0, 'Null'],
                 'X_CT-COM_APModuleEnable':[0, 'Null'], 
                 'X_CT-COM_WPSKeyWord':[0, 'Null'],
                 'Enable':[1, '1'], 
                 'Channel':[0, 'Null'],
                 'SSID':[0, 'Null'],
                 'BeaconType':[1, BeaconType], 
                 'Standard':[0, 'Null'],
                 'WEPKeyIndex':[1, WEPKeyIndex],
                 'KeyPassphrase':[0, 'Null'], 
                 'WEPEncryptionLevel':[1, WEPEncryptionLevel],
                 'BasicAuthenticationMode':[1, BasicAuthenticationMode], 
                 'WPAEncryptionModes':[0, 'Null'],
                 'WPAAuthenticationMode':[0, 'Null'], 
                 'IEEE11iEncryptionModes':[0, 'Null'],
                 'IEEE11iAuthenticationMode':[0, 'Null'], 
                 'BasicDataTransmitRates':[0, 'Null'],
                 'OperationalDataTransmitRates':[0, 'Null']}
    
    # WLANConfiguration.{i}.WEPKey.{i}.节点参数(WEP关心)
    dict_WEPKey = {'WEPKey':[1, WEPKey]}
    
    # WLANConfiguration.{i}.PreSharedKey.{i}.节点参数(WPA关心)
    dict_PreSharedKey = {}
    
    # 无线设置(第一个不修改,第二个设置为WEP,第三和第四个设置为不加密)
    ret, ret_data = WLANMulti(obj, sn, Num, dict_root,
                        dict_WEPKey, dict_PreSharedKey={}, 
                        change_account=0,
                        rollbacklist=rollbacklist)
    
    # 将工单脚本执行结果返回到OBJ的结果中
    obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + ret_data)
    
    # 如果执行失败，统一调用回退机制（缺省是关闭的）
    if ret == ERR_FAIL:
        ret_rollback, ret_data_rollback = rollback(sn, rollbacklist, obj)
        obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + ret_data_rollback)
        info = u"工单:%s执行结束\n" % os.path.basename(os.path.dirname(__file__))
        obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + info)    
        return ret
    
    # 直接新建四条WAN连接
    # 第一条IP_Routed,PPPOE,INTERNET 绑定LAN1和WLAN1
    # 第二条IP_Routed,PPPOE,INTERNET 绑定LAN2和WLAN3
    # 第三条PPPoE_Bridged INTERNET 绑定LAN3和WLAN3
    # 第四条PPPoE_Bridged INTERNET 绑定LAN4和WLAN4
    
    LAN1 = 'InternetGatewayDevice.LANDevice.1.LANEthernetInterfaceConfig.1'
    LAN2 = 'InternetGatewayDevice.LANDevice.1.LANEthernetInterfaceConfig.2'
    LAN3 = 'InternetGatewayDevice.LANDevice.1.LANEthernetInterfaceConfig.3'
    LAN4 = 'InternetGatewayDevice.LANDevice.1.LANEthernetInterfaceConfig.4'
    WLAN1 = 'InternetGatewayDevice.LANDevice.1.WLANConfiguration.1'
    WLAN2 = 'InternetGatewayDevice.LANDevice.1.WLANConfiguration.2'
    WLAN3 = 'InternetGatewayDevice.LANDevice.1.WLANConfiguration.3'
    WLAN4 = 'InternetGatewayDevice.LANDevice.1.WLANConfiguration.4'
    
    # 第一条WAN的 WANDSLLinkConfig节点参数
    if PVC_OR_VLAN1 == "":
        PVC_OR_VLAN1_flag = 0
    else:
        PVC_OR_VLAN1_flag = 1
        
    dict_wanlinkconfig1 = {'Enable':[1, '1'],
                           'DestinationAddress':[PVC_OR_VLAN1_flag, PVC_OR_VLAN1], 
                           'LinkType':[1, 'EoA'],
                           'X_CT-COM_VLAN':[0, 'Null']}
    
    # 第一条WAN的WANPPPConnection节点参数
    # 注意:X_CT-COM_IPMode节点有些V4版本没有做,所以不能使能为1.实际贝曼工单也是没有下发的
    dict_wanpppconnection1 = {'Enable':[1, '1'],
                              'ConnectionType':[1, 'IP_Routed'], 
                              'Name':[0, 'Null'],
                              'Username':[1, Username1], 
                              'Password':[1, Password1],
                              'X_CT-COM_LanInterface':[1, LAN1+','+WLAN1], 
                              'X_CT-COM_ServiceList':[1, 'INTERNET'],
                              'X_CT-COM_LanInterface-DHCPEnable':[0, 'Null'], 
                              'X_CT-COM_IPMode':[0, 'Null']}
    
    # 第二条WAN的 WANDSLLinkConfig节点参数
    if PVC_OR_VLAN2 == "":
        PVC_OR_VLAN2_flag = 0
    else:
        PVC_OR_VLAN2_flag = 1
        
    dict_wanlinkconfig2 = {'Enable':[1, '1'],
                           'DestinationAddress':[PVC_OR_VLAN2_flag, PVC_OR_VLAN2], 
                           'LinkType':[1, 'EoA'],
                           'X_CT-COM_VLAN':[0, 'Null']}
    
    # 第二条WAN的WANPPPConnection节点参数
    dict_wanpppconnection2 = {'Enable':[1, '1'],
                              'ConnectionType':[1, 'IP_Routed'], 
                              'Name':[0, 'Null'],
                              'Username':[1, Username2], 
                              'Password':[1, Password2],
                              'X_CT-COM_LanInterface':[1, LAN2+','+WLAN2], 
                              'X_CT-COM_ServiceList':[1, 'INTERNET'],
                              'X_CT-COM_LanInterface-DHCPEnable':[0, 'Null'], 
                              'X_CT-COM_IPMode':[0, 'Null']}
    
    # 第三条WAN的 WANDSLLinkConfig节点参数
    if PVC_OR_VLAN3 == "":
        PVC_OR_VLAN3_flag = 0
    else:
        PVC_OR_VLAN3_flag = 1
        
    dict_wanlinkconfig3 = {'Enable':[1, '1'],
                           'DestinationAddress':[PVC_OR_VLAN3_flag, PVC_OR_VLAN3], 
                           'LinkType':[1, 'EoA'],
                           'X_CT-COM_VLAN':[0, 'Null']}
    
    # 第三条WAN的WANPPPConnection节点参数
    dict_wanpppconnection3 = {'Enable':[1, '1'],
                              'ConnectionType':[1, 'PPPoE_Bridged'], 
                              'Name':[0, 'Null'],
                              'Username':[0, 'Null'], 
                              'Password':[0, 'Null'],
                              'X_CT-COM_LanInterface':[1, LAN3+','+WLAN3], 
                              'X_CT-COM_ServiceList':[1, 'INTERNET'],
                              'X_CT-COM_LanInterface-DHCPEnable':[0, 'Null'], 
                              'X_CT-COM_IPMode':[0, 'Null']}
    
    # 第四条WAN的 WANDSLLinkConfig节点参数
    if PVC_OR_VLAN4 == "":
        PVC_OR_VLAN4_flag = 0
    else:
        PVC_OR_VLAN4_flag = 1
        
    dict_wanlinkconfig4 = {'Enable':[1, '1'],
                           'DestinationAddress':[PVC_OR_VLAN4_flag, PVC_OR_VLAN4], 
                           'LinkType':[1, 'EoA'],
                           'X_CT-COM_VLAN':[0, 'Null']}
    
    # 第四条WAN的WANPPPConnection节点参数
    dict_wanpppconnection4 = {'Enable':[1, '1'],
                              'ConnectionType':[1, 'PPPoE_Bridged'], 
                              'Name':[0, 'Null'],
                              'Username':[0, 'Null'], 
                              'Password':[0, 'Null'],
                              'X_CT-COM_LanInterface':[1, LAN4+','+WLAN4], 
                              'X_CT-COM_ServiceList':[1, 'INTERNET'],
                              'X_CT-COM_LanInterface-DHCPEnable':[0, 'Null'], 
                              'X_CT-COM_IPMode':[0, 'Null']}

    # 第一条PPPoE WAN连接开通
    ret, ret_data = WLANMultiWANSetUP(obj, sn, WANEnable_Switch,
                                DeviceType, 'PPPoE',
                                PVC_OR_VLAN1, dict_wanlinkconfig1,
                                dict_wanpppconnection1,
                                dict_wanipconnection={},
                                change_account=0,
                                rollbacklist=rollbacklist)
    
    # 将工单脚本执行结果返回到OBJ的结果中
    obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + ret_data)
    
    # 如果执行失败，统一调用回退机制（缺省是关闭的）
    if ret == ERR_FAIL:
        ret_rollback, ret_data_rollback = rollback(sn, rollbacklist, obj)
        obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + ret_data_rollback)
        info = u"工单:%s执行结束\n" % os.path.basename(os.path.dirname(__file__))
        obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + info)    
        return ret
    
    
    # 第二条PPPoE WAN连接开通
    sleep(2)
    ret, ret_data = WLANMultiWANSetUP(obj, sn, WANEnable_Switch,
                                DeviceType, 'PPPoE',
                                PVC_OR_VLAN2, dict_wanlinkconfig2,
                                dict_wanpppconnection2,
                                dict_wanipconnection={},
                                change_account=0,
                                rollbacklist=rollbacklist)
    
    # 将工单脚本执行结果返回到OBJ的结果中
    obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + ret_data)
    
    # 如果执行失败，统一调用回退机制（缺省是关闭的）
    if ret == ERR_FAIL:
        ret_rollback, ret_data_rollback = rollback(sn, rollbacklist, obj)
        obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + ret_data_rollback)
        info = u"工单:%s执行结束\n" % os.path.basename(os.path.dirname(__file__))
        obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + info)    
        return ret
    
    
    # 第三条PPPoE_Bridged WAN连接开通
    sleep(2)
    ret, ret_data = WLANMultiWANSetUP(obj, sn, WANEnable_Switch,
                                DeviceType, 'PPPoE_Bridged',
                                PVC_OR_VLAN3, dict_wanlinkconfig3,
                                dict_wanpppconnection3,
                                dict_wanipconnection={},
                                change_account=0,
                                rollbacklist=rollbacklist)
    
    # 将工单脚本执行结果返回到OBJ的结果中
    obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + ret_data)
    
    # 如果执行失败，统一调用回退机制（缺省是关闭的）
    if ret == ERR_FAIL:
        ret_rollback, ret_data_rollback = rollback(sn, rollbacklist, obj)
        obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + ret_data_rollback)
        info = u"工单:%s执行结束\n" % os.path.basename(os.path.dirname(__file__))
        obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + info)    
        return ret
    
    
    # 第四条PPPoE_Bridged WAN连接开通
    sleep(2)
    ret, ret_data = WLANMultiWANSetUP(obj, sn, WANEnable_Switch,
                                DeviceType, 'PPPoE_Bridged',
                                PVC_OR_VLAN4, dict_wanlinkconfig4,
                                dict_wanpppconnection4,
                                dict_wanipconnection={},
                                change_account=1,
                                rollbacklist=rollbacklist)
    
    # 将工单脚本执行结果返回到OBJ的结果中
    obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + ret_data)
    
    # 如果执行失败，统一调用回退机制（缺省是关闭的）
    if ret == ERR_FAIL:
        ret_rollback, ret_data_rollback = rollback(sn, rollbacklist, obj)
        obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + ret_data_rollback)
    
    info = u"工单:%s执行结束\n" % os.path.basename(os.path.dirname(__file__))
    obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + info)    
    return ret

if __name__ == '__main__':
    log_dir = g_prj_dir
    log.start(name="nwf", directory=log_dir, level="DebugWarn")
    log.set_file_id(testcase_name="tr069")    
    
    obj = MsgWorklistExecute(id_="1")
    obj.sn = "201303051512"
    
    dict_data= {"WEPKeyIndex":("1","1"),"WEPEncryptionLevel":("40-bit","2"),
               "WEPKey":("0123456789","3"),
               "PVC_OR_VLAN1":("PVC:0/71","4"),
               "Username1":("TW71","6"),
                "Password1":("TW71","7"),"PVC_OR_VLAN2":("PVC:0/72","8"),
                "Username2":("TW72","10"),
                "Password2":("TW72","11"),"PVC_OR_VLAN3":("PVC:0/73","12"),
                "PVC_OR_VLAN4":("PVC:0/74","14"),
                "WANEnable_Switch":("1","16")}
    obj.dict_data = dict_data
    try:
        ret = test_script(obj)
        if ret == ERR_SUCCESS:
            print u"测试成功"
        else:
            print u"测试失败"
        print "****************************************"
        print obj.dict_ret["str_result"]
    except Exception, e:
        print u"测试异常"