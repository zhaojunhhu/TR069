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
import _WLANEnable
reload(_WLANEnable)
from _WLANEnable import WLANEnable

def test_script(obj):
    """
    """
    sn = obj.sn # 取得SN号
    DeviceType = "GPON"  # 绑定tr069模板类型.只支持ADSL\LAN\GPON三种
    AccessMode = 'PPPoE'    # WAN接入模式,可选PPPoE_Bridge,PPPoE,DHCP,Static
    change_or_enable = 'Enable'
    # 初始化日志
    obj.dict_ret.update(str_result=u"开始执行工单:%s........\n" %
                        os.path.basename(os.path.dirname(__file__)))
    
    # data传参
    SSIDNum1 = obj.dict_data.get("SSIDNum1")[0]
    Enable1  = obj.dict_data.get("Enable1")[0]
    
    SSIDNum2 = obj.dict_data.get("SSIDNum2")[0]
    Enable2  = obj.dict_data.get("Enable2")[0]
    
    SSIDNum3 = obj.dict_data.get("SSIDNum3")[0]
    Enable3  = obj.dict_data.get("Enable3")[0]
    
    SSIDNum4 = obj.dict_data.get("SSIDNum4")[0]
    Enable4  = obj.dict_data.get("Enable4")[0]
    
    
    # 支持多个传参数
    if SSIDNum1 == "":
        SSIDNum1_flag = 0
        node_SSIDNum1 = "null"
    else:
        SSIDNum1_flag = 1
        node_SSIDNum1 = SSIDNum1 + ".Enable"
    
    if SSIDNum2 == "":
        SSIDNum2_flag = 0
        node_SSIDNum2 = "null"
    else:
        SSIDNum2_flag = 1
        node_SSIDNum2 = SSIDNum2 + ".Enable"
    
    if SSIDNum3 == "":
        SSIDNum3_flag = 0
        node_SSIDNum3 = "null"
    else:
        SSIDNum3_flag = 1
        node_SSIDNum3 = SSIDNum3 + ".Enable"
        
    if SSIDNum4 == "":
        SSIDNum4_flag = 0
        node_SSIDNum4 = "null"
    else:
        SSIDNum4_flag = 1
        node_SSIDNum4 = SSIDNum4 + ".Enable"
        
    dict_ssid =  {'SSID1':[SSIDNum1_flag, node_SSIDNum1, Enable1],
                    'SSID2':[SSIDNum2_flag, node_SSIDNum2, Enable2], 
                    'SSID3':[SSIDNum3_flag, node_SSIDNum3, Enable3],
                    'SSID4':[SSIDNum4_flag, node_SSIDNum4, Enable4]}

    
    # 开始执行PVC开启关闭工单
    ret, ret_data = WLANEnable(obj, sn, dict_ssid)
    
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
    obj.sn = "2013012901"
    
    dict_data= {"PVC_OR_VLAN_1":("61","1"),"Enable1":("0","2"),
        "PVC_OR_VLAN_2":("62","3"),"Enable2":("1","4")}
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
