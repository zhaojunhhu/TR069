#coding:utf-8

# -----------------------------rpc --------------------------
import os
import sys

#debug
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

import _IPV6WANSetUP
reload(_IPV6WANSetUP)
from _IPV6WANSetUP import V6WANSetUP

import _IPV6IPTVEnable
reload(_IPV6IPTVEnable)
from _IPV6IPTVEnable import IPV6IPTVEnable


import _SmartTV
reload(_SmartTV)
from _SmartTV import SmartTV

def test_script(obj):
    """
    """
    sn = obj.sn # 取得SN号
    DeviceType = "GPON"  # 绑定tr069模板类型.只支持ADSL\LAN\GPON三种
    
    AccessMode1_1 = 'PPPoE'    # 用于双栈WAN， WAN接入模式,可选PPPoE_Bridge,PPPoE,DHCP,Static
    
    AccessMode1_2 = ''
       
    rollbacklist = []  # 存储工单失败时需回退删除的实例.目前缺省是不开启回退
    # 初始化日志
    obj.dict_ret.update(str_result=u"开始执行工单:%s........\n" %
                        os.path.basename(os.path.dirname(__file__)))
    
    # INTERNET data
    PVC_OR_VLAN1 = obj.dict_data.get("PVC_OR_VLAN1")[0]  # ADSL上行只关心PVC值,LAN和GPON上行则关心VLAN值
    Username = obj.dict_data.get("Username")[0]
    Password = obj.dict_data.get("Password")[0]
    X_CT_COM_LanInterface1 = obj.dict_data.get("X_CT_COM_LanInterface1")[0]
    
    #X_CT_COM_ServiceList1 = obj.dict_data.get("X_CT_COM_ServiceList1")[0]
    ret, X_CT_COM_LanInterface1 = ParseLANName(X_CT_COM_LanInterface1)
    
    if ret == ERR_FAIL:
        info = u'输入的X_CT_COM_LanInterface参数错误'
        obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + info)
        info = u"工单:%s执行结束\n" % os.path.basename(os.path.dirname(__file__))
        obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + info)    
        return ret    
    
    
    IPv6IPAddressOrigin = obj.dict_data.get("IPv6IPAddressOrigin")[0]
    IPv6PrefixOrigin    = obj.dict_data.get("IPv6PrefixOrigin")[0]
    
    
    IPv6PrefixMode = obj.dict_data.get("IPv6PrefixMode")[0]
    IPv6Prefix = obj.dict_data.get("IPv6Prefix")[0]
    
    IPv6DNSConfigType = obj.dict_data.get("IPv6DNSConfigType")[0]
    IPv6DNSServers = obj.dict_data.get("IPv6DNSServers")[0]
    
    DHCPv6ServerEnable = obj.dict_data.get("DHCPv6ServerEnable")[0]
    DHCPv6ServerMinAddress = obj.dict_data.get("DHCPv6ServerMinAddress")[0]
    DHCPv6ServerMaxAddress = obj.dict_data.get("DHCPv6ServerMaxAddress")[0]
    
    RouterAdvEnable = obj.dict_data.get("RouterAdvEnable")[0]
    AdvManagedFlag = obj.dict_data.get("AdvManagedFlag")[0]
    AdvOtherConfigFlag = obj.dict_data.get("AdvOtherConfigFlag")[0]
    
    # 强制将使能动作与参数一起下发
    WANEnable_Switch1 = False
    
    # SmartTV data
    PVC_OR_VLAN2 = obj.dict_data.get("PVC_OR_VLAN2")[0]
    
    # PVC_OR_VLAN 
    if PVC_OR_VLAN1 == "":
        PVC_OR_VLAN1_flag = 0
    else:
        PVC_OR_VLAN1_flag = 1
    
    # INTERNET dict data
    dict_wanlinkconfig1 = {'Enable':[1, '1'],
                          'Mode':[PVC_OR_VLAN1_flag, '2'],
                          'VLANIDMark':[PVC_OR_VLAN1_flag, PVC_OR_VLAN1]}
    
    # WANPPPConnection节点参数
    # 注意:X_CT-COM_IPMode节点有些V4版本没有做,所以不能使能为1.实际贝曼工单也是没有下发的

    dict_wanpppconnection1_1 = {'Enable':[1, '1'],
                              'ConnectionType':[1, 'IP_Routed'],
                              'Name':[0, 'Null'], 
                              'Username':[1, Username], 
                              'Password':[1, Password],
                              'X_CT-COM_LanInterface':[1, X_CT_COM_LanInterface1],
                              'X_CT-COM_LanInterface-DHCPEnable':[0, 'Null'], 
                              'X_CT-COM_ServiceList':[1, "INTERNET"],
                              'X_CT-COM_IPMode':[1, '3'],
                              'X_CT-COM_IPv6IPAddressOrigin':[1,IPv6IPAddressOrigin],
                              'X_CT-COM_IPv6PrefixOrigin':[1,IPv6PrefixOrigin],
                              'X_CT-COM_IPv6PrefixDelegationEnabled':[1,"1"],
                              'X_CT-COM_MulticastVlan':[0, 'Null']}
    
    dict_wanipconnection1_1 = {}
    dict_wanpppconnection1_2 = {}
    dict_wanipconnection1_2 = {}
    
    dict_v6config = {'DomainName':[0,'Null'],
                     'IPv6DNSConfigType':[1,IPv6DNSConfigType],
                     'IPv6DNSWANConnection':[1,''],
                     'IPv6DNSServers':[1,IPv6DNSServers]}
    
    dict_v6prefixinformation = {'Mode':[1,IPv6PrefixMode],
                                'Prefix':[1,IPv6Prefix],
                                'DelegatedWanConnection':[1,''],
                                'PreferredLifeTime':[0,'Null'],
                                'ValidLifeTime':[0,'Null']}
    
    dict_dhcpv6server = {'Enable':[1,DHCPv6ServerEnable],
                         'MinAddress':[1,DHCPv6ServerMinAddress],
                         'MaxAddress':[1,DHCPv6ServerMaxAddress]}
    
    dict_routeradvertisement = {'Enable':[1,RouterAdvEnable],
                                'AdvManagedFlag':[1,AdvManagedFlag],
                                'AdvOtherConfigFlag':[1,AdvOtherConfigFlag]}
    
    # smart TV data
    X_CT_COM_VLAN = PVC_OR_VLAN2 + '/' + PVC_OR_VLAN2
    X_CT_COM_Mode = '1'
    
 
    # WANIPConnection节点参数
    
    # 查询或开通PPPoE的IP_Routed上网
    ret, ret_data = V6WANSetUP(obj,sn, WANEnable_Switch1, DeviceType,
                       AccessMode1_1, PVC_OR_VLAN1, AccessMode1_2, dict_wanlinkconfig1,
                       dict_wanpppconnection1_1, dict_wanipconnection1_1,
                       dict_wanpppconnection1_2,dict_wanipconnection1_2,
                       dict_v6config,dict_v6prefixinformation,
                       dict_dhcpv6server,dict_routeradvertisement,
                       change_account=0,
                       rollbacklist=rollbacklist)
    
    # 将工单脚本执行结果返回到OBJ的结果中
    obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + ret_data)
    
    # 如果执行失败，统一调用回退机制（缺省是关闭的）
    if ret == ERR_FAIL:
        info = u'开通上网失败\n'
        obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + info)
        ret_rollback, ret_data_rollback = rollback(sn, rollbacklist, obj)
        obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + ret_data_rollback)
        info = u"工单:%s执行结束\n" % os.path.basename(os.path.dirname(__file__))
        obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + info)    
        return ret
    
    # 开通智能电视
    ret, ret_data = SmartTV(obj, sn, X_CT_COM_Mode , X_CT_COM_VLAN, 'LAN2')
    
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
    
    dict_data= {"PVC_OR_VLAN1":("PVC:0/65","1"),
                "Username":("tw1","2"),"Password":("tw1","3"),
                "IPv6IPAddressOrigin":("AutoConfigured","5"),
                "IPv6PrefixOrigin":("PrefixDelegation","6"),
                "IPv6PrefixMode":("WANDelegated","7"),
                "IPv6Prefix":("2001:1:2:3::/64","8"),
                "IPv6DNSConfigType":("WANConnection","9"),
                "IPv6DNSServers":("fe80::1","10"),
                "DHCPv6ServerEnable":("1","11"),
                "DHCPv6ServerMinAddress":("0:0:0:1","12"),
                "DHCPv6ServerMaxAddress":("ffff:ffff:ffff:fffe","13"),
                "RouterAdvEnable":("1","14"),
                "AdvManagedFlag":("1","15"),
                "AdvOtherConfigFlag":("1","16"),
                
                "PVC_OR_VLAN2":("","17"),
                    
                "PVC_OR_VLAN3":("","18"),
                "ProxyServer":("172.24.55.67","19"),
                "ProxyServerPort":("5060","20"),
                "RegistrarServer":("172.24.55.67","21"),
                "RegistrarServerPort":("5060","22"),
                "OutboundProxy":("0.0.0.0","23"),
                "OutboundProxyPort":("5060","24"),
                "X_CT_COM_Standby_ProxyServer":("172.24.55.67","25"),
                "X_CT_COM_Standby_ProxyServerPort":("5060","26"),
                "X_CT_COM_Standby_RegistrarServer":("172.24.55.67","27"),
                "X_CT_COM_Standby_RegistrarServerPort":("5060","28"),
                "X_CT_COM_Standby_OutboundProxy":("0.0.0.0","29"),
                "X_CT_COM_Standby_OutboundProxyPort":("5060","30"),
                "AuthUserName1":("55511021","31"),
                "AuthPassword1":("55511021","32")}
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