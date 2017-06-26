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
import _WAN
reload(_WAN)
from _WAN import WAN

def test_script(obj):
    """
    """
    sn = obj.sn # 取得SN号
    DeviceType = "ADSL"  # 绑定tr069模板类型.只支持ADSL\LAN\EPON三种
    AccessMode = 'PPPoE'    # WAN接入模式,可选PPPoE_Bridge,PPPoE,DHCP,Static
    change_or_enable = 'Change'
    # 初始化日志
    obj.dict_ret.update(str_result=u"开始执行工单:%s........\n" %
                        os.path.basename(os.path.dirname(__file__)))
    
    # data传参
    PVC_OR_VLAN_1 = obj.dict_data.get("PVC_OR_VLAN_1")[0]
    ChangeTo1 = obj.dict_data.get("ChangeTo1")[0]
    PVC_OR_VLAN_2 = obj.dict_data.get("PVC_OR_VLAN_2")[0]
    ChangeTo2 = obj.dict_data.get("ChangeTo2")[0]
    
    PVC_OR_VLAN_3 = obj.dict_data.get("PVC_OR_VLAN_3")[0]
    ChangeTo3 = obj.dict_data.get("ChangeTo3")[0]
    
    # 支持多个传参数
    if PVC_OR_VLAN_1 == "":
        PVC_OR_VLAN1_flag = 0
    else:
        PVC_OR_VLAN1_flag = 1
    if PVC_OR_VLAN_2 == "":
        PVC_OR_VLAN2_flag = 0
    else:
        PVC_OR_VLAN2_flag = 1
    
    if PVC_OR_VLAN_3 == "":
        PVC_OR_VLAN3_flag = 0
    else:
        PVC_OR_VLAN3_flag = 1
        
    
    dict_pvcorvlan = {'PVC_OR_VLAN_1':[PVC_OR_VLAN1_flag, PVC_OR_VLAN_1, ChangeTo1],
                      'PVC_OR_VLAN_2':[PVC_OR_VLAN2_flag, PVC_OR_VLAN_2, ChangeTo2], 
                      'PVC_OR_VLAN_3':[PVC_OR_VLAN3_flag, PVC_OR_VLAN_3, ChangeTo3],
                      'PVC_OR_VLAN_4':[0, 'Null', 'Null'], 
                      'PVC_OR_VLAN_5':[0, 'Null', 'Null'],
                      'PVC_OR_VLAN_6':[0, 'Null', 'Null']}
    
    # 开始执行PVC修改工单
    ret, ret_data = WAN(obj, sn, DeviceType, AccessMode,
                  change_or_enable, dict_pvcorvlan)
    
    # 将工单脚本执行结果返回到OBJ的结果中
    obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + ret_data)
    
    # 因为没有新建实例的可能，所以无需调用回退机制

    
    info = u"工单:%s执行结束\n" % os.path.basename(os.path.dirname(__file__))
    obj.dict_ret.update(str_result=obj.dict_ret["str_result"] + info)    
    return ret


if __name__ == '__main__':
    log_dir = g_prj_dir
    log.start(name="nwf", directory=log_dir, level="DebugWarn")
    log.set_file_id(testcase_name="tr069")    
    
    obj = MsgWorklistExecute(id_="1")
    obj.sn = "201303051512"
    
    dict_data= {"PVC_OR_VLAN_1":("PVC:0/61","1"),"ChangeTo1":("PVC:0/71","2"),
        "PVC_OR_VLAN_2":("PVC:0/62","3"),"ChangeTo2":("PVC:0/72","4")}
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