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

import _IPV6VOIP
reload(_IPV6VOIP)
from _IPV6VOIP import IPV6VOIP

def test_script(obj):
    """
    """
    sn = obj.sn # 取得SN号
    DeviceType = "EPON"  # 绑定tr069模板类型.只支持ADSL\LAN\EPON三种
    
    AccessMode1_1 = 'PPPoE_Bridged'    # 用于双栈WAN， WAN接入模式,可选PPPoE_Bridge,PPPoE,DHCP,Static
    
    AccessMode1_2 = ''
    
    AccessMode2 = 'PPPoE_Bridged'    # 用于IPTV， WAN接入模式,可选PPPoE_Bridge,PPPoE,DHCP,Static
   
    AccessMode3 = 'DHCP'      # 用于 VOIP，
    
    rollbacklist = []  # 存储工单失败时需回退删除的实例.目前缺省是不开启回退
    # 初始化日志
    obj.dict_ret.update(str_result=u"开始执行工单:%s........\n" %
                        os.path.basename(os.path.dirname(__file__)))
    
    # INTERNET data
    PVC_OR_VLAN1 = obj.dict_data.get("PVC_OR_VLAN1")[0]  # ADSL上行只关心PVC值,LAN和EPON上行则关心VLAN值
    
    X_CT_COM_LanInterface1 = obj.dict_data.get("X_CT_COM_LanInterface1")[0]
    
    #X_CT_COM_ServiceList1 = obj.dict_data.get("X_CT_COM_ServiceList1")[0]
    ret, X_CT_COM_LanInterface1 = ParseLANName(X_CT_COM_LanInterface1)
    
    if ret == ERR_FAIL:
        info = u'输入的X_CT_COM_LanInterface参数错误'
        obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + info)
        info = u"工单:%s执行结束\n" % os.path.basename(os.path.dirname(__file__))
        obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + info)    
        return ret    

    # 强制将使能动作与参数一起下发
    WANEnable_Switch1 = False
    
    
    # IPTV data
    
    PVC_OR_VLAN2 = obj.dict_data.get("PVC_OR_VLAN2")[0]  # ADSL上行只关心PVC值,LAN和EPON上行则关心VLAN值
    X_CT_COM_MulticastVlan = obj.dict_data.get("X_CT_COM_MulticastVlan")[0] # 新增公共组播VLAN的下发
    
    # WANPPPConnection节点参数
    # 注意:X_CT-COM_IPMode节点有些V4版本没有做,所以不能使能为1.实际贝曼工单也是没有下发的
    LAN2 = 'InternetGatewayDevice.LANDevice.1.LANEthernetInterfaceConfig.2'    # 绑字到LAN2
    
    
    WANEnable_Switch2 = 1
    
    
    # VOIP data
    PVC_OR_VLAN3 = obj.dict_data.get("PVC_OR_VLAN3")[0]    # ADSL上行只关心PVC值,LAN和EPON上行则关心VLAN值

    ProxyServer = obj.dict_data.get("ProxyServer")[0]
    ProxyServerPort = obj.dict_data.get("ProxyServerPort")[0]
    RegistrarServer = obj.dict_data.get("RegistrarServer")[0]
    RegistrarServerPort = obj.dict_data.get("RegistrarServerPort")[0]
    OutboundProxy = obj.dict_data.get("OutboundProxy")[0]
    OutboundProxyPort = obj.dict_data.get("OutboundProxyPort")[0]
    X_CT_COM_Standby_ProxyServer = obj.dict_data.get("X_CT_COM_Standby_ProxyServer")[0]
    X_CT_COM_Standby_ProxyServerPort = obj.dict_data.get("X_CT_COM_Standby_ProxyServerPort")[0]
    X_CT_COM_Standby_RegistrarServer = obj.dict_data.get("X_CT_COM_Standby_RegistrarServer")[0]
    X_CT_COM_Standby_RegistrarServerPort = obj.dict_data.get("X_CT_COM_Standby_RegistrarServerPort")[0]
    X_CT_COM_Standby_OutboundProxy = obj.dict_data.get("X_CT_COM_Standby_OutboundProxy")[0]
    X_CT_COM_Standby_OutboundProxyPort = obj.dict_data.get("X_CT_COM_Standby_OutboundProxyPort")[0]
    AuthUserName1 = obj.dict_data.get("AuthUserName1")[0]
    AuthPassword1 = obj.dict_data.get("AuthPassword1")[0]
    AuthUserName2 = obj.dict_data.get("AuthUserName2")[0]
    AuthPassword2 = obj.dict_data.get("AuthPassword2")[0]
    
    WANEnable_Switch3 = False
 
    
    # PVC_OR_VLAN 
    if PVC_OR_VLAN1 == "":
        PVC_OR_VLAN1_flag = 0
    else:
        PVC_OR_VLAN1_flag = 1
    
    if PVC_OR_VLAN2 == "":
        PVC_OR_VLAN2_flag = 0
    else:
        PVC_OR_VLAN2_flag = 1
    
    if PVC_OR_VLAN3 == "":
        PVC_OR_VLAN3_flag = 0
    else:
        PVC_OR_VLAN3_flag = 1
    
    # INTERNET dict data
    dict_wanlinkconfig1 = {'Enable':[1, '1'],
                          'Mode':[PVC_OR_VLAN1_flag, '2'],
                          'VLANIDMark':[PVC_OR_VLAN1_flag, PVC_OR_VLAN1]}
    
    # WANPPPConnection节点参数
    # 注意:X_CT-COM_IPMode节点有些V4版本没有做,所以不能使能为1.实际贝曼工单也是没有下发的

    dict_wanpppconnection1_1 = {'Enable':[1, '1'],
                              'ConnectionType':[1, 'PPPoE_Bridged'],
                              'Name':[0, 'Null'], 
                              'Username':[0, 'Null'], 
                              'Password':[0, 'Null'],
                              'X_CT-COM_LanInterface':[1, X_CT_COM_LanInterface1],
                              'X_CT-COM_LanInterface-DHCPEnable':[0, 'Null'], 
                              'X_CT-COM_ServiceList':[1, "INTERNET"],
                              'X_CT-COM_IPMode':[1, '3'],
                              'X_CT-COM_IPv6IPAddressOrigin':[0,'Null'],
                              'X_CT-COM_IPv6PrefixOrigin':[0,'Null'],
                              'X_CT-COM_IPv6PrefixDelegationEnabled':[0,'Null'],
                              'X_CT-COM_MulticastVlan':[0, 'Null']}
    
    dict_wanipconnection1_1 = {}
    dict_wanpppconnection1_2 = {}
    dict_wanipconnection1_2 = {}
    
    dict_v6config = {}
    
    dict_v6prefixinformation = {}
    
    dict_dhcpv6server = {}
    
    dict_routeradvertisement = {}

    # IPTV dict data
    
    dict_wanlinkconfig2 = {'Enable':[0, 'Null'],
                          'Mode':[PVC_OR_VLAN2_flag, '2'],
                          'VLANIDMark':[PVC_OR_VLAN2_flag, PVC_OR_VLAN2]}
    
    if X_CT_COM_MulticastVlan == "":
        X_CT_COM_MulticastVlan_flag = 0
    else:
        X_CT_COM_MulticastVlan_flag = 1
   
    
    dict_wanpppconnection2 = {
                              'ConnectionType':[1, 'PPPoE_Bridged'], 
                              'Name':[0, 'Null'],
                              'Username':[0, 'Null'], 
                              'Password':[0, 'Null'],
                              'X_CT-COM_LanInterface':[1, LAN2], 
                              'X_CT-COM_ServiceList':[1, 'OTHER'],
                              'X_CT-COM_LanInterface-DHCPEnable':[0, 'Null'], 
                              'X_CT-COM_IPMode':[0, 'Null'],
                              'X_CT-COM_MulticastVlan':[X_CT_COM_MulticastVlan_flag, X_CT_COM_MulticastVlan],
                              'Enable':[1, '1']}

    dict_wanipconnection2 = {}
    
    dict_root = {'IGMPEnable':[1, '1'], 
                 'ProxyEnable':[0, 'Null'], 
                 'SnoopingEnable':[0, 'Null']}


    # VOIP dict data
    dict_wanlinkconfig3 = {'Enable':[0, 'Null'],
                          'Mode':[PVC_OR_VLAN3_flag, '2'],
                          'VLANIDMark':[PVC_OR_VLAN3_flag, PVC_OR_VLAN3]}
    
    dict_wanipconnection3 = {'Enable':[0, '1'],
                            'ConnectionType':[0, 'IP_Routed'], 
                            'Name':[0, 'Null'],
                            'NATEnabled':[0, 'Null'], 
                            'AddressingType':[0, 'DHCP'],
                            'ExternalIPAddress':[0, '10.10.10.10'], 
                            'SubnetMask':[0, '255.255.255.0'],
                            'DefaultGateway':[0, '10.10.10.1'], 
                            'DNSEnabled':[0, 'Null'],
                            'DNSServers':[0, '10.10.10.2'], 
                            'X_CT-COM_LanInterface':[0, "Null"], 
                            'X_CT-COM_ServiceList':[1, 'TR069,VOIP']}   
    
    dict_wanpppconnection3 = {}
    # voice 相关
    dict_voiceservice = {"VoiceProfile.1.X_CT-COM_ServerType":[1,'1'],
                         "VoiceProfile.1.SIP.ProxyServer":[1, ProxyServer],
                         "VoiceProfile.1.SIP.ProxyServerPort":[1, ProxyServerPort],
                         "VoiceProfile.1.SIP.ProxyServerTransport":[0, "Null"],
                         "VoiceProfile.1.SIP.RegistrarServer":[1, RegistrarServer],
                         "VoiceProfile.1.SIP.RegistrarServerPort":[1, RegistrarServerPort],
                         "VoiceProfile.1.SIP.RegistrarServerTransport":[0, "Null"],
                         "VoiceProfile.1.SIP.OutboundProxy":[1, OutboundProxy],
                         "VoiceProfile.1.SIP.OutboundProxyPort":[1, OutboundProxyPort],
                         "VoiceProfile.1.SIP.X_CT-COM_Standby-ProxyServer":[1, X_CT_COM_Standby_ProxyServer],
                         "VoiceProfile.1.SIP.X_CT-COM_Standby-ProxyServerPort":[1, X_CT_COM_Standby_ProxyServerPort],
                         "VoiceProfile.1.SIP.X_CT-COM_Standby-ProxyServerTransport":[0, "Null"],
                         "VoiceProfile.1.SIP.X_CT-COM_Standby-RegistrarServer":[1, X_CT_COM_Standby_RegistrarServer],
                         "VoiceProfile.1.SIP.X_CT-COM_Standby-RegistrarServerPort":[1, X_CT_COM_Standby_RegistrarServerPort],
                         "VoiceProfile.1.SIP.X_CT-COM_Standby-RegistrarServerTransport":[0, "Null"],
                         "VoiceProfile.1.SIP.X_CT-COM_Standby-OutboundProxy":[1, X_CT_COM_Standby_OutboundProxy],
                         "VoiceProfile.1.SIP.X_CT-COM_Standby-OutboundProxyPort":[1, X_CT_COM_Standby_OutboundProxyPort],
                         "VoiceProfile.1.SIP.UserAgentDomain":[0, "Null"],
                         "VoiceProfile.1.SIP.UserAgentPort":[0, "Null"],
                         "VoiceProfile.1.SIP.UserAgentTransport":[0, "Null"],
                         "VoiceProfile.1.SIP.VLANIDMark":[0, "Null"],
                         "VoiceProfile.1.SIP.X_CT-COM_802-1pMark":[0, "Null"],
                         "VoiceProfile.1.SIP.DSCPMark":[0, "Null"],  
                         "VoiceProfile.1.SIP.X_CT-COM_HeartbeatSwitch":[0, "Null"],
                         "VoiceProfile.1.SIP.X_CT-COM_HeartbeatCycle":[0, "Null"],
                         "VoiceProfile.1.SIP.X_CT-COM_HeartbeatCount":[0, "Null"],  
                         "VoiceProfile.1.SIP.X_CT-COM_SessionUpdateTimer":[0, "Null"],
                         "VoiceProfile.1.SIP.RegisterRetryInterval":[0, "Null"],
                         "VoiceProfile.1.SIP.RegisterExpires":[0, "Null"],
                         "VoiceProfile.1.SIP.ImplicitRegistrationEnable":[0, "Null"],                            
                         "VoiceProfile.1.Line.1.SIP.AuthUserName":[1, AuthUserName1],
                         "VoiceProfile.1.Line.1.SIP.AuthPassword":[1, AuthPassword1],
                         "VoiceProfile.1.Line.2.SIP.AuthUserName":[1, AuthUserName2],
                         "VoiceProfile.1.Line.2.SIP.AuthPassword":[1, AuthPassword2],
                         "VoiceProfile.1.Line.1.Enable":[1, "Enabled"],
                         "VoiceProfile.1.Line.2.Enable":[2, "Enabled"]}
  
    
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
    
    
    # 开通PPPoE_Bridged的OTHER桥IPTV,并绑定到LAN2
    ret, ret_data = IPV6IPTVEnable(obj, sn, WANEnable_Switch2, DeviceType,
                         AccessMode2, PVC_OR_VLAN2, dict_root,
                         dict_wanlinkconfig2, dict_wanpppconnection2,
                         dict_wanipconnection2, change_account=0,
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

    # 执行VOIP开通工单
    ret, ret_data = IPV6VOIP(obj, sn, WANEnable_Switch3, DeviceType, 
                        AccessMode3, PVC_OR_VLAN3,
                        dict_voiceservice,
                        dict_wanlinkconfig3, 
                        dict_wanpppconnection3, dict_wanipconnection3,
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