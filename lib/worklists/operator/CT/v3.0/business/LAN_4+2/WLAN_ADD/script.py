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
import _WLAN
reload(_WLAN)
from _WLAN import WLAN


def test_script(obj):
    """
    """
    sn = obj.sn # 取得SN号
    DeviceType = "LAN"  # 绑定tr069模板类型.只支持ADSL\LAN\EPON三种
    rollbacklist = []  # 存储工单失败时需回退删除的实例.目前缺省是不开启回退
    # 初始化日志
    obj.dict_ret.update(str_result=u"开始执行工单:%s........\n" %
                        os.path.basename(os.path.dirname(__file__)))
    
    # data传参
    Num = obj.dict_data.get("Num")[0]

    
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
                 'BeaconType':[1, 'None'], 
                 'Standard':[0, 'Null'],
                 'WEPKeyIndex':[0, 'Null'],
                 'KeyPassphrase':[0, 'Null'], 
                 'WEPEncryptionLevel':[0, 'Null'],
                 'BasicAuthenticationMode':[0, 'Null'], 
                 'WPAEncryptionModes':[0, 'Null'],
                 'WPAAuthenticationMode':[0, 'Null'], 
                 'IEEE11iEncryptionModes':[0, 'Null'],
                 'IEEE11iAuthenticationMode':[0, 'Null'], 
                 'BasicDataTransmitRates':[0, 'Null'],
                 'OperationalDataTransmitRates':[0, 'Null']}
    
    # WLANConfiguration.{i}.WEPKey.{i}.节点参数(WEP关心)
    dict_WEPKey = {}
    
    # WLANConfiguration.{i}.PreSharedKey.{i}.节点参数(WPA关心)
    dict_PreSharedKey = {}
    
    # 开始执行WLAN工单
    ret, ret_data = WLAN(obj, sn, Num, dict_root,
                   dict_WEPKey={}, dict_PreSharedKey={},
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
    obj.sn = "021018010268"
    
    dict_data= {"Num":("4","1")}
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
