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

def test_script(obj):
    """
    """
    sn = obj.sn # 取得SN号
    DeviceType = "EPON"  # 绑定tr069模板类型.只支持ADSL\LAN\EPON三种
    AccessMode = 'PPPoE'    # WAN接入模式,可选PPPoE_Bridge,PPPoE,DHCP,Static
    rollbacklist = []  # 存储工单失败时需回退删除的实例.目前缺省是不开启回退
    # 初始化日志
    obj.dict_ret.update(str_result=u"开始执行工单:%s........\n" %
                        os.path.basename(os.path.dirname(__file__)))
    
    # data传参
    PVC_OR_VLAN = obj.dict_data.get("PVC_OR_VLAN")[0]  # ADSL上行只关心PVC值,LAN和EPON上行则关心VLAN值
    Username = obj.dict_data.get("Username")[0]
    Password = obj.dict_data.get("Password")[0]
    X_CT_COM_LanInterface = obj.dict_data.get("X_CT_COM_LanInterface")[0]
    X_CT_COM_ServiceList = obj.dict_data.get("X_CT_COM_ServiceList")[0]
    WANEnable_Switch = obj.dict_data.get("WANEnable_Switch")[0]
    
    # 对X_CT_COM_LanInterface重新解析,兼容LAN1,lan1格式
    ret, X_CT_COM_LanInterface = ParseLANName(X_CT_COM_LanInterface)
    if ret == ERR_FAIL:
        info = u'输入的X_CT_COM_LanInterface参数错误'
        obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + info)
        info = u"工单%s 执行结束" % os.path.basename(os.path.dirname(__file__))
        obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + info)
        return ret

    # X_CT-COM_WANEponLinkConfig节点参数
    if PVC_OR_VLAN == "":
        PVC_OR_VLAN_flag = 0
    else:
        PVC_OR_VLAN_flag = 1
        
    if Username == "":
        Username_flag = 0
    else:
        Username_flag = 1
        
    if Password == "":
        Password_flag = 0
    else:
        Password_flag = 1
     
    if X_CT_COM_LanInterface == "":
        X_CT_COM_LanInterface_flag = 0
    else:
        X_CT_COM_LanInterface_flag = 1
        
    if X_CT_COM_ServiceList == "":
        X_CT_COM_ServiceList_flag = 0
    else:
        X_CT_COM_ServiceList_flag = 1
     
    

    dict_wanlinkconfig = {'Enable':[1, '1'],
                          'Mode':[PVC_OR_VLAN_flag, '2'],
                          'VLANIDMark':[PVC_OR_VLAN_flag, PVC_OR_VLAN]}
    
    # WANPPPConnection节点参数
    # 注意:X_CT-COM_IPMode节点有些V4版本没有做,所以不能使能为1.实际贝曼工单也是没有下发的
    dict_wanpppconnection = {'Enable':[1, '1'],
                             'ConnectionType':[1, 'IP_Routed'], 
                             'Name':[0, 'Null'],
                             'Username':[Username_flag, Username], 
                             'Password':[Password_flag, Password],
                             'X_CT-COM_LanInterface':[X_CT_COM_LanInterface_flag, X_CT_COM_LanInterface], 
                             'X_CT-COM_ServiceList':[X_CT_COM_ServiceList_flag, X_CT_COM_ServiceList],
                             'X_CT-COM_LanInterface-DHCPEnable':[0, 'Null'], 
                             'X_CT-COM_IPMode':[0, 'Null']}
    
    # WANIPConnection节点参数
    dict_wanipconnection = {}
    
    # 开始执行WAN连接开通工单
    ret, ret_data = WANSetUP(obj, sn, WANEnable_Switch, DeviceType,
                       AccessMode, PVC_OR_VLAN, dict_wanlinkconfig,
                       dict_wanpppconnection, dict_wanipconnection,
                       rollbacklist=rollbacklist)
    
    # 将工单脚本执行结果返回到OBJ的结果中
    obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + ret_data)
    
    # 如果执行失败，统一调用回退机制
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
    
    dict_data= {"PVC_OR_VLAN":("61","1"), "Username":("TW61","2"),"Password":("TW61","3"),
                "X_CT_COM_LanInterface":("LAN1","4"),
                "X_CT_COM_ServiceList":("INTERNET","5"),
                "WANEnable_Switch":("1","6")}
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
