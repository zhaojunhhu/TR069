#coding:utf-8

"""
    nwf 2014-06-30  thread->process  for user write worklist separated
"""

import  threading
import  os
import  sys
from    time            import ctime,sleep
from    shutil          import copy2
from    datetime        import datetime
import  pickle
from    cStringIO       import StringIO
import  imp
from    multiprocessing import Process

# user lib
import  TR069.lib.common.logs.log   as      log  
from    TR069.lib.common.error      import  *
from    TR069.lib.common.event      import  *
from    TR069.lib.common.function   import  print_trace, get_id
from    TR069.lib.common.httpclient import  HttpClient
import  TR069.lib.worklists.worklistcfg      as      worklistcfg

from    TR069.lib.users.user        import UserRpc as User
import  TR069.lib.users.user        as user


class CpeThread(Process):
    """
    do work (user worklist exec)
    """       
    
    def __init__(self, msg, obj):
        """        
        """
        
        Process.__init__(self)
        
        self.msg = msg
        self.obj = obj   # obj = MsgWorklistExecute

        self.exec_script_dir = None  # member(tr069v3\lib\worklist\script\ADSL\script)
        self.exec_script_modulename = None  # member(tr069v3\lib\worklist\script\ADSL\script\WLAN_ADD_script(.py))

        self.log_path = log.get_log_path()
        
        
    def run(self):
        from worklist import Worklist

        ret = None
        msg = self.msg
        obj = self.obj
        msg_rsp = msg + 2  # default

        # start log
        log_dir = self.log_path   
        log.start_only_1file(name=obj.sn, file_name=obj.sn, 
                            directory=log_dir, level="DebugWarn")  
        log.set_file_id(testcase_name="worklist")


        for nwf in [1]:
            try:                
                msg_rsp = self.handle_worklist(msg, obj)
            except Exception,e:  
                print_trace(e)                 

        ret, msg = self.build_worklist_exec_rsp_rqst(obj, msg_rsp)
        ret = self.send_message(msg, worklistcfg.SHORT_CONNECTION_TIMEOUT)        


    def handle_worklist(self, msg, obj):
        """
        obj = MsgWorklistExecute
        """        
        ret = None
        ret_api     = ERR_FAIL
        ret_data    = ""
        ret_obj     = None  # event obj
        ret_out     = ""    # RF ret 
        file_imp    = None
        module_imp  = None

        sn = obj.sn
        desc = "cpe(sn=%s) begin execute worklist(name=%s)" %(
                sn, obj.worklist_name)
        log.app_info(desc)

        for nwf in [1]:
            try:

                # nwf 2014-06-28; DB lost interface_version
                if (not obj.cpe_interface_version):
                    ret_api, ret_data = user.query_cpe_interface_version(sn)
                    if ret_api == ERR_SUCCESS:
                        ret_obj = ret_data
                        ret_out = ret_obj.dict_ret["str_result"]                    
                        obj.cpe_interface_version = ret_out
                    else:
                        desc = "query CPE interface version fail."
                        obj.dict_ret["str_result"] = desc
                        break
                    
                ret = self.check_dir_file(obj)
                if (ret != ERR_SUCCESS):
                    break                                

                # nwf 2014-06-27;  use full path, not sys.path[0] + module name
                name_imp = self.exec_script_modulename
                file_imp, imppath, description = imp.find_module(name_imp, 
                                                                [self.exec_script_dir])
                module_imp =imp.load_module(name_imp, file_imp, imppath, description)                                
                entry = worklistcfg.DOMAIN_SCRIPT_FILE_ENTRY                          
                # entry (eg test_script(obj)
                x = "ret= %s.%s(obj)" %("module_imp", entry) 

                desc = "cpe(sn=%s) execute worklist(name=%s)" %(obj.sn, obj.worklist_name)
                log.app_info(desc)
        
                exec x
                
            except Exception,e:
                print_trace(e)            
                ret = ERR_FAIL
                obj.dict_ret["str_result"] = str(e)                    
                break              
            finally:
                if (file_imp):
                    file_imp.close()


        if (ret == ERR_SUCCESS):        
            msg_rsp = msg + 1  # response        
        else:
            msg_rsp = msg + 2
         
        return msg_rsp
        

    def check_dir_file(self, obj):
        """
        obj(MsgWorklistExecute)  is dir[domain] + file[worklist name] exist?
        """        
        
        ret = ERR_FAIL
        ret_api = None
        script_root_dir = worklistcfg.SCRIPT_ROOT_DIR

        desc = "cpe(sn=%s, cpe device type=%s) begin search worklist(name=%s)" %(
                    obj.sn, obj.domain, obj.worklist_name)
        log.app_info(desc)


        for nwf in [1]: 
            try:
                dir_root = script_root_dir  # tr069v3\lib\worklist\operator
                ret_api = os.path.isdir(dir_root)
                if (ret_api == False):
                    desc = "%s is not dir in worklist server." %(dir_root)
                    obj.dict_ret["str_result"] = desc
                    log.app_err(desc)
                    break

                operator = obj.operator
                # tr069v3\lib\worklist\operator\CT
                dir_operator = os.path.join(dir_root, operator)  
                ret_api = os.path.isdir(dir_operator)
                if (ret_api == False):
                    desc = "%s is not dir in worklist server." %(dir_operator)                    
                    log.app_err(desc)
                    desc = u"cpe operator=%s 不支持(支持的有 CT CU)." %operator
                    obj.dict_ret["str_result"] = desc
                    break


                # V3.0 or V4.0?
                cpe_interface_version = obj.cpe_interface_version
                dir_interface_version = os.path.join(dir_operator, cpe_interface_version)
                ret_api = os.path.isdir(dir_interface_version)
                if (ret_api == False):
                    desc = "%s is not dir in worklist server." %(dir_interface_version)                    
                    log.app_err(desc)
                    desc = u"CPE operator=%s, interface version=%s 不支持." %(
                            operator, cpe_interface_version)
                    obj.dict_ret["str_result"] = desc
                    break 


                # tr069v3\lib\worklist\operator\CT\V3.0\business
                dir_business = os.path.join(dir_interface_version, worklistcfg.BUSINESS_DOMAINS)  
                ret_api = os.path.isdir(dir_business)
                if (ret_api == False):
                    desc = "%s is not dir in worklist server." %(dir_business)
                    obj.dict_ret["str_result"] = desc
                    log.app_err(desc)
                    break                    

                domain = obj.domain
                # tr069v3\lib\worklist\operator\CT\V3.0\business\ADSL
                dir_domain = os.path.join(dir_business, domain)
                ret_api = os.path.isdir(dir_domain)
                if (ret_api == False):
                    desc = "%s is not dir in worklist server." %(dir_domain)                    
                    log.app_err(desc)
                    desc = u"CPE device type=%s 不支持." %domain
                    obj.dict_ret["str_result"] = desc
                    break                                             


                # nwf 2013-07-02; support _COMMON(Auto)
                desc = ""
                
                dir_system = os.path.join(dir_interface_version, worklistcfg.SYSTEM_DOMAINS)
                for dir_domain in [dir_domain, dir_system]:

                    # nwf 2013-04-10 ; support to pyc(publish)
                    worklist_name= obj.worklist_name
                    # tr069v3\lib\worklist\operator\CT\V3.0\business\ADSL
                    exec_script_dir = os.path.join(dir_domain, worklist_name)
                    file1 = os.path.join(exec_script_dir, worklistcfg.SCRIPT_FILE_NAME+".py")
                    ret_api = os.path.isfile(file1)
                    if (ret_api == False):
                        # retry
                        file2 = os.path.join(exec_script_dir, worklistcfg.SCRIPT_FILE_NAME + ".pyc")
                        ret_api = os.path.isfile(file2)
                        if (ret_api == False):                                    
                            desc += "warning:(%s) or (%s) is not file in worklist server.\n" %(file1, file2)                            
                            log.app_err(desc)
                            desc = u"CPE worklist name=%s 不支持." %worklist_name
                            obj.dict_ret["str_result"] = desc
                        else:
                            # success
                            break
                    else:
                        # success
                        break

                if (ret_api == False):
                    break
                    

                # save E:\____python\tr069\TR069_BS2_nwf\TR069\lib\worklists\operator\CT\v3.0\business\ADSL_2LAN\QoS_DSCP
                self.exec_script_dir =exec_script_dir   
                # script.py             
                exec_script_modulename = worklistcfg.SCRIPT_FILE_NAME   # no .py     
                self.exec_script_modulename = exec_script_modulename                                     
                
            except Exception,e:
                print_trace(e)   
                
                obj.dict_ret["str_result"] = str(e)
                break

            desc = "cpe(sn=%s, cpe device type=%s) search worklist(name=%s) success." %(obj.sn, obj.domain, obj.worklist_name)
            log.app_info(desc)                
            ret = ERR_SUCCESS
        
        return ret
        

    def build_worklist_exec_rsp_rqst(self, obj, msg_rsp):
        """
        obj is MsgWorklistExecute
        """
        ret = ERR_FAIL  # default  
        msg = ""

        desc = "cpe(sn=%s), worklist id=%s, message=%s" %(obj.sn, obj.id_, get_event_desc(msg_rsp))
        log.app_info(desc)

        for nwf in [1]:
            try:         

                obj                 = MsgWorklistExecRsp(obj.id_, obj.sn, msg_rsp, obj.dict_ret)
                
                strio               = StringIO()
                pickle.dump(obj, strio)  
                
                dict1                   = {}
                dict1[KEY_MESSAGE]      = EV_WORKLIST_EXECUTE_RSP_RQST
                dict1[KEY_OBJECT]       = strio.getvalue()                
                dict1[KEY_SN]           = obj.sn                
                dict1[KEY_SENDER]       = KEY_SENDER_WORKLIST
                dict1[KEY_MESSAGE_TYPE] = EVENT_WORKLIST_GROUP
                dict1[KEY_QUEUE]        = QUEUE_WAIT
                dict1[KEY_SEQUENCE]     = get_id("Seq")
                
                msg                 = str(dict1)
        
            except Exception,e:
                msg = e
                print_trace(e)
                
                break
            
            ret = ERR_SUCCESS

        return ret, msg


    def send_message(self, msg, timeout):
        """
        """
        url = "http://%s:%s%s" %(worklistcfg.AGENT_HTTP_IP, worklistcfg.AGENT_HTTP_PORT, worklistcfg.WORKLIST2AGENT_PAGE)
        httpclient1 = HttpClient(url, timeout)
        
        ret, str_data = httpclient1.send_message(msg)    

        return ret, str_data  



def test():    
    pass
        
if __name__ == '__main__':
    test()
