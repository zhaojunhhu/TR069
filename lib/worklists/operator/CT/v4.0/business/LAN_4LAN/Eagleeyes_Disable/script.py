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
import _Eagleeyes
reload(_Eagleeyes)
from _Eagleeyes import Eagleeyes

def test_script(obj):
    """
    """
    sn = obj.sn # 取得SN号
    DeviceType = "LAN"  # 绑定tr069模板类型.只支持ADSL\LAN\EPON三种
    AccessMode = 'PPPoE'    # WAN接入模式,可选PPPoE_Bridge,PPPoE,DHCP,Static
    PortMappingEnabled = 'Disable'    # 是执行全球眼开通还是取消工单.Enable开通,Disable取消
    rollbacklist = []  # 存储工单失败时需回退删除的实例.目前缺省是不开启回退
    # 初始化日志
    obj.dict_ret.update(str_result=u"开始执行工单:%s........\n" %
                        os.path.basename(os.path.dirname(__file__)))
    
    # data传参
    ExternalPort = obj.dict_data.get("ExternalPort")[0]
    InternalPort = obj.dict_data.get("InternalPort")[0]
    PortMappingProtocol = obj.dict_data.get("PortMappingProtocol")[0]
    InternalClient = obj.dict_data.get("InternalClient")[0]
    
    # PortMapping节点下的参数字典
    dict_PortMapping = {'PortMappingLeaseDuration':[1, '0'],
                        'ExternalPort':[1, ExternalPort],
                        'InternalPort':[1, InternalPort],
                        'PortMappingProtocol':[1, PortMappingProtocol],
                        'InternalClient':[1, InternalClient],
                        'PortMappingEnabled':[1, '1']}
    
    # 执行全球眼工单
    ret, ret_data = Eagleeyes(obj, sn, DeviceType, AccessMode,
                        PortMappingEnabled, dict_PortMapping,
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
    obj.sn = "2013012901"
    
    dict_data= {"ExternalPort":("8006","1"),"InternalPort":("80","2"),
        "PortMappingProtocol":("TCP","3"),"InternalClient":("192.168.1.100","4")}
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
