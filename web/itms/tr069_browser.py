#coding:utf-8

# sys
import  os
import  sys
import threading

# entry
g_prj_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, g_prj_dir)   # E:\____python\django\TR069_BS\itms

# user
import  TR069.lib.users.user        as user
import  TR069.lib.users.usercmd     as usercmd
from    TR069.lib.common.event      import *
from    TR069.lib.common.error      import *
from    TR069.lib.common.function   import *
from django_log                 import ProcessOutLog as log



# model
from    models                      import CPE


class TR069_Browser(object):
    
    def __init__(self):
        """
        """
        # 去除以前的log加载模块！ 2014-5-29
        pass
        """
        if (0):
            g_prj_dir = os.path.dirname(__file__)
            sys.path.insert(0, g_prj_dir)        
            log_dir = os.path.join(g_prj_dir, "TR069_log")
            log.start(name="TR069", directory=log_dir, level="DebugWarn")
            log.set_file_id(testcase_name="TR069")
        """
    def update_1_sn(self, sn, dict_item):
        """
        函数功能：更新CPE的参数信息
        参数：
            sn:           CPE的sn号
            dict_item:    待更新的字段信息
        返回值：
            ret_data:     更新字段已写入数据库，此处可忽略
        """
        
        ret         = None
        ret_data    = None
        ret_obj     = None
        
        ret,ret_data = user.update_cpe_info(sn, dict_item)
        if (ret == ERR_SUCCESS):
            ret_obj = ret_data  

        return ret_data
    
    def run_rpc(self, sn, rpc_name, dict_args, for_dyntree=True):
        """
        函数功能：执行rpc方法
        参数：
            sn：          cpe sn号；
            rpc_name：    rpc方法的名字；
            dict_args：   rpc方法参数
            for_dyntree:  看rpc请求是来自动态树还是静态rpc方法
        返回值：
            list_data  [rpc_exec_result, rpc_exec_code, rpc_exec_data]
        """
        if for_dyntree:
            rpc_exec_result = u"success"
        else:
            rpc_exec_result = u"执行成功"
            
        rpc_exec_code       = ""
        rpc_exec_data       = ""
        
        obj_usercmd = usercmd.Usercmd()
        obj_usercmd.set_request_source_form_bs()
        ret, dict_ret = obj_usercmd.process_rpc(sn,
                                                rpc_name,
                                                dict_args
                                                )
        #raise Exception("ret:%s,dict-ret：%s" % (ret, dict_ret))
        if ret == ERR_FAIL:
            
            if not for_dyntree:
                rpc_exec_result = u"执行失败"
            else:
                rpc_exec_result     = "fail"                
            
            if isinstance(dict_ret, dict):
                if "dict_data" in dict_ret:
                    dict_data = dict_ret.get("dict_data", {})
                    rpc_exec_code   = dict_data.get("FaultCode", "")
                
                    if "FaultString" in dict_data:
                        rpc_exec_data = dict_data.get("FaultString", "")
                    else:
                        rpc_exec_data = dict_ret.get("str_result")
            else:
                rpc_exec_data = dict_ret
        elif for_dyntree:
            rpc_exec_data = dict_ret.get("dict_data")
        else:
            rpc_exec_data   = dict_ret.get("str_result")
            
            if "\n" in rpc_exec_data:
                rpc_exec_data = rpc_exec_data.replace("\n", "<br/>")
        
        return [rpc_exec_result, rpc_exec_code, rpc_exec_data]
    
    def init_worklist(self, dict_args):
        """
        函数功能：新增工单接口函数，包括逻辑工单和物理工单
        参数：
            dict_args：工单参数，逻辑工单含有用户名和密码
        返回值：
            ret：      str型标识执行成功与否
            ret_data： str型为执行失败的信息
        """
        ret      = "success"
        ret_data = ""
        
        obj_worklist = user.UserWorklist()
        
        ret_tmp, ret_data_tmp  = obj_worklist.worklistprocess_build(**dict_args)         
        if ret_tmp == ERR_SUCCESS:
            ret_data = ret_data_tmp.id_
        else:
            ret = "fail"
            ret_data = ret_data_tmp.dict_ret["str_result"]
        
        return ret, ret_data
    
    def bind_physic_worklist(self, dict_data):
        """
        函数功能：绑定物理工单接口
        参数：
            dict_args：包含了工单id以及绑定的sn号
        返回值：
            ret：      str型标识执行成功与否
            ret_data： str型为执行失败的信息
        """
        ret      = "success"
        ret_data = ""
        
        obj_worklist = user.UserWorklist()

        ret_tmp, ret_data_tmp = obj_worklist.worklistprocess_bind_physical(**dict_data)           
        if ret_tmp != ERR_SUCCESS:
            ret = "fail"
            ret_data = u"绑定工单失败，结果如下:%s" % ret_data_tmp
        
        return ret, ret_data
    
    def exec_physic_worklist(self, dict_data):
        """
        函数功能：物理工单执行接口（此处和rf区别为这里用多线程处理，不阻塞）
        参数：
            dict_args：包含了工单id
        返回值：
            thread_obj：多进程对象
        """
        obj_worklist = user.UserWorklist()
        
        thread_obj = threading.Thread(target=obj_worklist.worklistprocess_execute, kwargs=dict_data)

        return thread_obj
        

# global
g_TR069_browser = TR069_Browser()

def test():
    
    sn = "00904C-2013012901"
    
    obj1 = g_TR069_browser
    ret = obj1.query_1_sn(sn)
    print ret
    
    SNs = obj1.query_all_sn()
    print SNs    
    

if __name__ == '__main__':
    
    test()

