#coding:utf-8

# -----------------------------rpc --------------------------
import os
from TR069.lib.common.error import *
from TR069.lib.users.user import UserRpc as User
from time import sleep
import TR069.lib.common.logs.log as log 
from _Common import *
import  TR069.lib.worklists.worklistcfg as worklistcfg 

def QoS(obj, sn, DeviceType, dict_root, 
        dict_app, list_value_type, 
        dict_classification, dict_priorityQueue,
        change_account=1,
        rollbacklist=[]):
    """
    """
    ret_res = ERR_FAIL # 返回成功或失败
    ret_data_scr = "" # 返回结果日志
    
    #QoS的根节点
    QoS_ROOT_PATH = "InternetGatewayDevice.X_CT-COM_UplinkQoS."
    for nwf in [1]:
        try:
            u1=User(sn, ip=worklistcfg.AGENT_HTTP_IP, port=worklistcfg.AGENT_HTTP_PORT, page=worklistcfg.WORKLIST2AGENT_PAGE, sender=KEY_SENDER_WORKLIST, worklist_id=obj.id_)
            reboot_Yes = 0
            
            #第一步：启用QoS和设置调度策略、DSCP及其他标志
            info = u"开始启用QoS和设置调度策略、DSCP及其它标志\n"
            log.app_info (info)
            ret_data_scr += info
            para_list1 = []
            for i in dict_root:
                if dict_root[i][0] == 1:
                    tmp_path = QoS_ROOT_PATH + i
                    para_list1.append(dict(Name=tmp_path, Value=dict_root[i][1]))

            if para_list1 == []:
                info = u"参数为空,请检查"
                log.app_info (info)
                ret_data_scr += info
                return ret_res, ret_data_scr

            #sleep(3)  # must be ;otherwise exception
            ret_root, ret_data_root = u1.set_parameter_values(ParameterList=para_list1)
            if (ret_root == ERR_SUCCESS):
                info = u"启用QoS和设置调度策略、DSCP及其它标志成功\n"
                log.app_info (info)
                ret_data_scr += info
                rebootFlag = int(ret_data_root["Status"])
                if (rebootFlag == 1):
                    reboot_Yes = 1
            else:
                #对于失败的情况，直接返回错误
                info = u"启用QoS和设置调度策略、DSCP及其它标志失败，错误原因：%s\n" % ret_data_root
                log.app_err (info)
                ret_data_scr += info
                return ret_res, ret_data_scr
            
            #第二步：增加队列实例
            #针对基于业务的QoS保障测试-UDP工单,需要多个TYPE实例
            tmp_Classification_path = []  # GCW 20130418 增加一步新建Classification实例的动作
            list_path3 = [] # Classification.{i}.type.路径下需下发的参数列表
            # 取队列号
            class_num = dict_classification['ClassQueue'][1]
            for i in xrange(len(list_value_type)):
                # GCW 20130418比贝曼增加一步，新增加以下实例
                # InternetGatewayDevice.X_CT-COM_UplinkQoS.Classification.
                info = u"开始调用AddObject新建Classification实例\n"
                log.app_info (info)
                ret_data_scr += info
                Classification_path = "InternetGatewayDevice.X_CT-COM_UplinkQoS.Classification."
                #sleep(3)  # must be ;otherwise exception
                ret_add, ret_data_add = u1.add_object(
                                    ObjectName=Classification_path)
    
                if (ret_add == ERR_SUCCESS):
                    instanceNum1 = ret_data_add["InstanceNumber"]
                    info = u"新建Classification实例成功,返回实例号：%s\n" % instanceNum1
                    log.app_info (info)
                    ret_data_scr += info
                    tmp_Classification_path.append(Classification_path + instanceNum1 + ".")
                    # GCW 20130327 增加回退机制
                    rollbacklist.append(Classification_path + instanceNum1 + ".")
                    rebootFlag = int(ret_data_add["Status"])
                    if (rebootFlag == 1):
                        reboot_Yes = 1
                else:
                    #对于失败的情况，返回失败
                    info = u"新建Classification实例失败，退出执行，错误原因：%s\n" % ret_data_add
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                
                
                info = u"开始调用AddObject新建type实例\n"
                log.app_info (info)
                ret_data_scr += info
                type_path = Classification_path + instanceNum1 +".type." 
                #sleep(3)  # must be ;otherwise exception
                ret_add, ret_data_add = u1.add_object(
                                    ObjectName=type_path)
    
                if (ret_add == ERR_SUCCESS):
                    instanceNum1 = ret_data_add["InstanceNumber"]
                    info = u"新建type实例成功,返回实例号：%s\n" % instanceNum1
                    log.app_info (info)
                    ret_data_scr += info
                    # GCW 20130327 增加回退机制
                    # GCW 20130419 由于增加了步骤新建Classification实例，所以回滚直接删除Classification实例
                    # rollbacklist.append(type_path + instanceNum1 + ".")
                    rebootFlag = int(ret_data_add["Status"])
                    if (rebootFlag == 1):
                        reboot_Yes = 1
                else:
                    #对于失败的情况，返回失败
                    info = u"新建type实例失败，退出执行，错误原因：%s\n" % ret_data_add
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                list_path3.append(type_path + instanceNum1 + ".")
            
            
            #第三步：对队列各个参数进行配置
            #注意,电信规范上没有分开写,即可以解读为是在一个RPC中下发后面第三四五步的所有参数,
            #而且对A上行,还有要求VLAN,但贝曼工单抓包看这两点均没有.目前按贝曼实现,待完善!

            for i in xrange(len(list_path3)):
                info = u"开始调用SetParameterValues,对队列各个参数进行配置\n"
                log.app_info (info)
                ret_data_scr += info
                para_list3 = []
                dict_type = list_value_type[i]
                for j in dict_type:
                    if dict_type[j][0] == 1:
                        tmp_path = list_path3[i] + j
                        para_list3.append(dict(Name=tmp_path, Value=dict_type[j][1]))
                if para_list3 == []:
                    info = u"参数为空,请检查\n"
                    log.app_info (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                
                #sleep(3)  # must be ;otherwise exception
                ret_type, ret_data_type = u1.set_parameter_values(ParameterList=para_list3)
    
                if (ret_type == ERR_SUCCESS):
                    info = u"对队列各个参数进行配置成功\n"
                    log.app_info (info)
                    ret_data_scr += info
                    rebootFlag = int(ret_data_type["Status"])
                    if (rebootFlag == 1):
                        reboot_Yes = 1
                else:
                    #对于失败的情况，返回失败
                    info = u"对队列各个参数进行配置失败，错误原因：%s\n" % ret_data_type
                    log.app_err (info)
                    ret_data_scr += info
                    return ret_res, ret_data_scr
                
            #可以有个开关控制是否将以下参数与上面的参数一起下发。电信规范上是一起
            #第四步：对流分类进行配置
            # GCW 20130418增加了对Classification的设置.            
            info = u"开始调用SetParameterValues,对Classification参数进行配置\n"
            log.app_info (info)
            ret_data_scr += info
            #path4 = QoS_ROOT_PATH + "Classification." + class_num + "."

            para_list4 = []
            for i in xrange(len(tmp_Classification_path)):
                for j in dict_classification:
                    if dict_classification[j][0] == 1:
                        tmp_path = tmp_Classification_path[i] + j
                        para_list4.append(dict(Name=tmp_path, Value=dict_classification[j][1]))
            if para_list4 == []:
                info = u"参数为空,请检查\n"
                log.app_info (info)
                ret_data_scr += info
                return ret_res, ret_data_scr
            
            #sleep(3)  # must be ;otherwise exception
            ret_class, ret_data_class = u1.set_parameter_values(ParameterList=para_list4)
            if (ret_class == ERR_SUCCESS):
                info = u"对Classification进行配置成功\n"
                log.app_info (info)
                ret_data_scr += info
                rebootFlag = int(ret_data_class["Status"])
                if (rebootFlag == 1):
                    reboot_Yes = 1
            else:
                #对于失败的情况，返回失败
                info = u"对Classification进行配置失败，错误原因：%s\n" % ret_data_class
                log.app_err (info)
                ret_data_scr += info
                return ret_res, ret_data_scr
            
            #第五步：对优先级队列进行配置
            info = u"开始调用SetParameterValues,对优先级队列进行配置\n"
            log.app_info (info)
            ret_data_scr += info
            path5 = QoS_ROOT_PATH + "PriorityQueue." + class_num + "."
            para_list5 = []
            for i in dict_priorityQueue:
                if dict_priorityQueue[i][0] == 1:
                    tmp_path = path5 + i
                    para_list5.append(dict(Name=tmp_path, Value=dict_priorityQueue[i][1]))
            if para_list5 == []:
                return ret_res, ret_data_scr
            
            #sleep(3)  # must be ;otherwise exception
            ret_prio, ret_data_prio = u1.set_parameter_values(ParameterList=para_list5)

            if (ret_prio == ERR_SUCCESS):
                info = u"对优先级队列进行配置成功\n"
                log.app_info (info)
                ret_data_scr += info
                rebootFlag = int(ret_data_prio["Status"])
                if (rebootFlag == 1):
                    reboot_Yes = 1
            else:
                #对于失败的情况，返回失败
                info = u"对优先级队列进行配置失败,错误原因：%s\n" % ret_data_prio
                log.app_err (info)
                ret_data_scr += info
                return ret_res, ret_data_scr
            
            # 如果需要重启,则下发Reboot方法,目前采用静等待130S
            if (reboot_Yes == 1):

                #sleep(130)
                ret, ret_data = reboot_wait_next_inform(u1)
                if (ret != ERR_SUCCESS):
                    ret_data_scr += ret_data
                    break
                
            # 第五步：调用修改电信维护密码,目前密码固定为nE7jA%5m
            ret, ret_data = ChangeAccount_CT(obj, sn, change_account)
            if ret == ERR_FAIL:
                ret_data_scr += ret_data
                return ret, ret_data_scr
            else:
                ret_data_scr += ret_data
                
            ret_res = ERR_SUCCESS
        except Exception, e:
            log.app_err (str(e))
            ret_data_scr += str(e)+'\n'
            return ret_res, ret_data_scr
    
    return ret_res, ret_data_scr        

if __name__ == '__main__':
    pass
    test_script(sn="20130121009")