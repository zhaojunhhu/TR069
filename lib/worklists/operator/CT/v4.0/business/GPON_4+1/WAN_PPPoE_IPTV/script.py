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
import _WANSetUP
reload(_WANSetUP)
from _WANSetUP import WANSetUP
import _IPTVEnable
reload(_IPTVEnable)
from _IPTVEnable import IPTVEnable

def test_script(obj):
    """
    """
    sn = obj.sn # 取得SN号
    DeviceType = "GPON"  # 绑定tr069模板类型.只支持ADSL\LAN\GPON三种
    rollbacklist = []  # 存储工单失败时需回退删除的实例.目前缺省是不开启回退
    # 初始化日志
    obj.dict_ret.update(str_result=u"开始执行工单:%s........\n" %
                        os.path.basename(os.path.dirname(__file__)))
    
    # data传参
    PVC_OR_VLAN1 = obj.dict_data.get("PVC_OR_VLAN1")[0]  # ADSL上行只关心PVC值,LAN和GPON上行则关心VLAN值
    Username = obj.dict_data.get("Username")[0]
    Password = obj.dict_data.get("Password")[0]
    X_CT_COM_LanInterface1 = obj.dict_data.get("X_CT_COM_LanInterface1")[0]
    X_CT_COM_ServiceList1 = obj.dict_data.get("X_CT_COM_ServiceList1")[0]
    PVC_OR_VLAN2 = obj.dict_data.get("PVC_OR_VLAN2")[0]  # ADSL上行只关心PVC值,LAN和GPON上行则关心VLAN值
    X_CT_COM_MulticastVlan = obj.dict_data.get("X_CT_COM_MulticastVlan")[0] # 新增公共组播VLAN的下发
    
    # 强制将使能动作与参数一起下发
    WANEnable_Switch = '1'    
    AccessMode1 = 'PPPoE'    # WAN接入模式,可选PPPoE_Bridge,PPPoE,DHCP,Static
    AccessMode2 = 'PPPoE_Bridged'    # WAN接入模式,可选PPPoE_Bridge,PPPoE,DHCP,Static
    

    # 对X_CT_COM_LanInterface重新解析,兼容LAN1,lan1格式
    ret, X_CT_COM_LanInterface1 = ParseLANName(X_CT_COM_LanInterface1)
    if ret == ERR_FAIL:
        info = u'输入的X_CT_COM_LanInterface参数错误'
        obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + info)
        info = u"工单:%s执行结束\n" % os.path.basename(os.path.dirname(__file__))
        obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + info)    
        return ret

    # IPTV节点参数
    dict_root = {'IGMPEnable':[1, '1'], 
                 'ProxyEnable':[0, 'Null'], 
                 'SnoopingEnable':[0, 'Null']}

    # X_CT-COM_WANGPONLinkConfig节点参数
    if PVC_OR_VLAN1 == "":
        PVC_OR_VLAN1_flag = 0
    else:
        PVC_OR_VLAN1_flag = 1
        
    dict_wanlinkconfig1 = {'Enable':[1, '1'],
                          'Mode':[PVC_OR_VLAN1_flag, '2'],
                          'VLANIDMark':[PVC_OR_VLAN1_flag, PVC_OR_VLAN1]}
    # X_CT-COM_WANGPONLinkConfig节点参数
    if PVC_OR_VLAN2 == "":
        PVC_OR_VLAN2_flag = 0
    else:
        PVC_OR_VLAN2_flag = 1
        
    dict_wanlinkconfig2 = {'Enable':[1, '1'],
                          'Mode':[PVC_OR_VLAN2_flag, '2'],
                          'VLANIDMark':[PVC_OR_VLAN2_flag, PVC_OR_VLAN2]}
    
    # WANPPPConnection节点参数
    # 注意:X_CT-COM_IPMode节点有些V4版本没有做,所以不能使能为1.实际贝曼工单也是没有下发的
 
    dict_wanpppconnection1 = {'Enable':[1, '1'],
                              'ConnectionType':[1, 'IP_Routed'], 
                              'Name':[0, 'Null'], 
                              'Username':[1, Username], 
                              'Password':[1, Password],
                              'X_CT-COM_LanInterface':[1, X_CT_COM_LanInterface1],
                              'X_CT-COM_ServiceList':[1, X_CT_COM_ServiceList1],
                              'X_CT-COM_LanInterface-DHCPEnable':[0, 'Null'], 
                              'X_CT-COM_IPMode':[0, 'Null'],
                              'X_CT-COM_MulticastVlan':[0, 'Null']}
    
    # WANPPPConnection节点参数
    # 注意:X_CT-COM_IPMode节点有些V4版本没有做,所以不能使能为1.实际贝曼工单也是没有下发的
    LAN2 = 'InternetGatewayDevice.LANDevice.1.LANEthernetInterfaceConfig.2'    # 绑字到LAN2
    
    if X_CT_COM_MulticastVlan == "":
        X_CT_COM_MulticastVlan_flag = 0
    else:
        X_CT_COM_MulticastVlan_flag = 1
       
    dict_wanpppconnection2 = {'Enable':[1, '1'],
                              'ConnectionType':[1, 'PPPoE_Bridged'], 
                              'Name':[0, 'Null'],
                              'Username':[0, 'Null'], 
                              'Password':[0, 'Null'],
                              'X_CT-COM_LanInterface':[1, LAN2], 
                              'X_CT-COM_ServiceList':[1, 'OTHER'],
                              'X_CT-COM_LanInterface-DHCPEnable':[0, 'Null'], 
                              'X_CT-COM_IPMode':[0, 'Null'],
                              'X_CT-COM_MulticastVlan':[X_CT_COM_MulticastVlan_flag, X_CT_COM_MulticastVlan]}
    
    # WANIPConnection节点参数
    dict_wanipconnection = {}
    
    # 查询或开通PPPoE的IP_Routed上网
    ret, ret_data = WANSetUP(obj, sn, WANEnable_Switch, DeviceType,
                       AccessMode1, PVC_OR_VLAN1, dict_wanlinkconfig1,
                       dict_wanpppconnection1, dict_wanipconnection,
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
    ret, ret_data = IPTVEnable(obj, sn, WANEnable_Switch, DeviceType,
                         AccessMode2, PVC_OR_VLAN2, dict_root,
                         dict_wanlinkconfig2, dict_wanpppconnection2,
                         dict_wanipconnection, change_account=1,
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
    obj.sn = "3F3001880F5CAD80F"
    
    dict_data= {"PVC_OR_VLAN1":("65","1"), "Username":("tw1","2"), "Password":("tw1","3"),
                "X_CT_COM_LanInterface1":("LAN4","4"),
                "X_CT_COM_ServiceList1":("INTERNET","5"),
                "PVC_OR_VLAN2":("66","6"), "WANEnable_Switch":("1","7")}
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
