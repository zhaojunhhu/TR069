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
import _QoS
reload(_QoS)
from _QoS import QoS

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
    Max = obj.dict_data.get("Max")[0]
    Min = obj.dict_data.get("Min")[0]
    ClassQueue = obj.dict_data.get("ClassQueue")[0]
    DSCPMarkValue = obj.dict_data.get("DSCPMarkValue")[0]
    M802_1_P_Value = obj.dict_data.get("M802_1_P_Value")[0]
    
    # X_CT-COM_UplinkQoS节点参数
    dict_root = {'Mode':[0, 'Null'],
                 'Enable':[1, '1'],
                 'Bandwidth':[0, 'Null'],
                 'Plan':[1, 'priority'],
                 'EnableForceWeight':[0, 'Null'],
                 'EnableDSCPMark':[1, '1'],
                 'Enable802-1_P':[1, '2']}
    
    # X_CT-COM_UplinkQoS.App.{i}.节点下的参数
    dict_app = {'AppName':[0, 'Null'],
                'ClassQueue':[0, 'Null']}
    
    # X_CT-COM_UplinkQoS.Classification.{i}.type.{i}.节点下的参数
    # 注意,使用列表嵌套字典的形式,因为基于业务的QoS保障测试-UDP时需要多个实例
    list_value_type = [{'Type':[1, 'DIP'],
                        'Max':[1, Max],
                        'Min':[1, Min],
                        'ProtocolList':[1, 'TCP,UDP']}]
    
    # X_CT-COM_UplinkQoS.Classification.{i}.节点下的参数
    dict_classification = {'ClassQueue':[1, ClassQueue],
                           'DSCPMarkValue':[1, DSCPMarkValue],
                           '802-1_P_Value':[1, M802_1_P_Value]}
    
    # X_CT-COM_UplinkQoS.PriorityQueue.{i}.节点下的参数
    dict_priorityQueue = {'Enable':[1, '1'],
                          'Priority':[1, '1'],
                          'Weight':[0, 'Null']}
    
    # 开始执行QoS工单
    ret, ret_data = QoS(obj, sn, DeviceType, dict_root, 
                  dict_app, list_value_type, 
                  dict_classification, dict_priorityQueue, 
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
    
    dict_data= {"Min":("222.66.65.57","1"),"Max":("222.66.65.57","2"),
        "DSCPMarkValue":("2","3"),"M802_1_P_Value":("2","4"),
            "ClassQueue":("1","5")}
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