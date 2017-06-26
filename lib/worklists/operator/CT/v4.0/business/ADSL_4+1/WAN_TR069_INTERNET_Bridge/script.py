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


import _AddAnWAN
reload(_AddAnWAN)
from _AddAnWAN import AddAnWAN

def test_script(obj):
    """
    """
    
    sn = obj.sn # 取得SN号
    DeviceType = "ADSL"  # 绑定tr069模板类型.只支持ADSL\LAN\EPON三种
    
     
    AccessMode = 'PPPoE_Bridged'    # 用于双栈WAN， WAN接入模式,可选PPPoE_Bridge,PPPoE,DHCP,Static
    
    
    rollbacklist = []  # 存储工单失败时需回退删除的实例.目前缺省是不开启回退
    # 初始化日志
    obj.dict_ret.update(str_result=u"开始执行工单:%s........\n" %
                        os.path.basename(os.path.dirname(__file__)))
    
    # INTERNET data
    PVC_OR_VLAN = obj.dict_data.get("PVC_OR_VLAN")[0]  # ADSL上行只关心PVC值,LAN和EPON上行则关心VLAN值
    
    X_CT_COM_LanInterface = obj.dict_data.get("X_CT_COM_LanInterface")[0]
    
    ret, X_CT_COM_LanInterface = ParseLANName(X_CT_COM_LanInterface)
    
    if ret == ERR_FAIL:
        info = u'输入的X_CT_COM_LanInterface参数错误'
        obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + info)
        info = u"工单:%s执行结束\n" % os.path.basename(os.path.dirname(__file__))
        obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + info)    
        return ret    

    # 强制将使能动作与参数一起下发
    WANEnable_Switch = False
    
    
    
    # PVC_OR_VLAN 
    if PVC_OR_VLAN == "":
        PVC_OR_VLAN_flag = 0
    else:
        PVC_OR_VLAN_flag = 1
    
   
    
    dict_wanlinkconfig = {'Enable':[1, '1'],
                          'DestinationAddress':[PVC_OR_VLAN_flag, PVC_OR_VLAN], 
                          'LinkType':[1, 'EoA'],
                          'X_CT-COM_VLAN':[0, 'Null']}
    
    
    dict_wanpppconnection = {'Enable':[1, '1'],
                              'ConnectionType':[1, 'PPPoE_Bridged'],
                              'Name':[0, 'Null'], 
                              'Username':[0, 'Null'], 
                              'Password':[0, 'Null'],
                              'X_CT-COM_LanInterface':[1, X_CT_COM_LanInterface],
                              'X_CT-COM_LanInterface-DHCPEnable':[0, 'Null'], 
                              'X_CT-COM_ServiceList':[1, "INTERNET"],
                              'X_CT-COM_IPMode':[1, '1'],
                              'X_CT-COM_MulticastVlan':[0, 'Null'],
                              'NATEnabled':[0,'Null']}
    
    dict_wanipconnection = {}
    
    ret, ret_data = AddAnWAN(obj, sn, WANEnable_Switch, DeviceType, 
                        AccessMode, PVC_OR_VLAN,
                        dict_wanlinkconfig, 
                        dict_wanpppconnection, dict_wanipconnection,
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
    
    dict_data= {"PVC_OR_VLAN":("PVC:0/65","1")}
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