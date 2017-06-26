#coding:utf-8

# ***************************************************************************
#
#  nwf      2013-05-24      refactor(unify)
# ***************************************************************************


# sys lib
import  sys
import  os
import  copy 
from    cStringIO           import  StringIO
from    datetime            import  datetime
from    functools           import  partial
import  inspect
import  pickle
import  random
import  re
import  time
from    threading           import  Timer
from    twisted.internet    import  reactor, threads
from    twisted.web.server  import  NOT_DONE_YET
import  urllib
import  urlparse
from    socket              import *


# user lib
from    TR069.lib.common.error          import  *
from    TR069.lib.common.event          import  *
from    TR069.lib.common.function       import  print_trace, get_id, UsersMsgSeq
import  TR069.lib.common.logs.log       as      log 
import  TR069.lib.worklists.worklistcfg          as      worklistcfg
from    cpethread                       import  CpeThread

# ----------------------------------------------------------------------
class Worklist(object):
    """
    """    
    
    def __init__(self):
        """        
        """
        pass
   
   
    @staticmethod
    def set_user_dictmsg(request, user_dictmsg):
        # nwf 2013-03-13 cpe's property upgrade to request's
        request.user_dictmsg = user_dictmsg
    @staticmethod
    def get_user_dictmsg(request):
        return request.user_dictmsg     
   
   
    # ---------------------------  user msg entry -------------- 
    @staticmethod    
    def dispatch_agent(request):    
        """
        request = twisted.web.server.Request user
        """  
        ret         = ERR_FAIL  # default
        ret_api     = None


        for nwf in [1]:

            # dict in?
            try:
                body = request.content.read()
                dict1 = eval(body)
            except Exception,e:
                log.app_err("request content read, isn't a dict(%s)." %(e))
                break

            # save
            Worklist.set_user_dictmsg(request, dict1)            

            # have message ?
            v_msg = dict1.get(KEY_MESSAGE)
            if (not v_msg):
                log.app_err("dict KEY_MESSAGE missing(%s)." %(KEY_MESSAGE))
                break    
                
            ip = request.transport.client[0]
            port = request.transport.client[1]
            log.app_info("receive user(ip=%s, port=%s) message=%s" %(ip, port, get_event_desc(v_msg))) 

            # have message sequence ?
            v_seq = dict1.get(KEY_SEQUENCE)
            if (not v_seq):
                log.app_err("dict KEY_SEQUENCE missing(%s)." %(KEY_SEQUENCE))
                break  

            sender = dict1.get(KEY_SENDER, "")
            log.app_info("receive user(ip=%s, port=%s) sender=%s, sequence=%s" %(ip, port, sender, v_seq))
            ret_api,msg = UsersMsgSeq.is_user_message_seq_exist(v_seq)
            if (ret_api):   
                log.app_err("receive user(ip=%s, port=%s) sequence=%s is exist." %(ip, port, v_seq))                
                Worklist.process_user_message_seq_exist(request, msg)
                break  

            # have obj?   
            v_obj = dict1.get(KEY_OBJECT)
            if (not v_obj):
                log.app_err("dict KEY_OBJECT missing(%s)." %(KEY_OBJECT))
                break
            try:
                strio = StringIO(v_obj)  
                obj = pickle.load(strio)
            except Exception,e:
                log.app_err("dict KEY_OBJECT pick load fail.")
                break                
            
            # dispatch
            try:
                msg_group = int(v_msg) & 0xFF00
                if (msg_group == EVENT_WORKLIST_GROUP):                
                    ret = Worklist.handle_msg(request, v_msg, obj)

                elif (msg_group == EVENT_QUERY_GROUP):                
                    ret = Worklist.process_query(request, v_msg, obj)
                    
                else:
                    desc = "user message group(=%d) not support." %msg_group
                    log.app_err(desc)
                    break
            except Exception,e:
                print_trace(e)
                break
            ret = ERR_SUCCESS  # not use
        
        return NOT_DONE_YET   #  async   
   

    @staticmethod        
    def handle_msg(request, msg, obj):
        """
        obj = MsgWorklistExecute
        """
        ret = None
        msg_rsp = msg + 2   # default =fail
        
        for nwf in [1]:
            
            if (msg == EV_WORKLIST_EXECUTE_RQST):
                
                ret, msg_rsp = Worklist.do_worklist_execute(msg, obj)
                if (ret == ERR_FATAL):
                    # fatal 
                    break             
                
            elif (msg == EV_WORKLIST_DOWNLOAD_RQST):
                ret, msg_rsp = Worklist.do_worklist_download(msg, obj)
                if (ret == ERR_FATAL):
                    # fatal
                    break
                
            else:                
                log.app_err("unknow worklist message(%s)" %msg)
                # sender timeout
                ret = ERR_FAIL
                break
        
            # handle msg ok, echo sender
            ret = Worklist.send_msg(request, msg_rsp, obj)    
    
        return ret
    
    
    @staticmethod        
    def do_worklist_execute(msg, obj):
        """
        obj = MsgWorklist
        only dispatch msg, no work
        """
        ret = None
        
        # check
        if (not isinstance(obj, MsgWorklist)):
            log.app_err("obj is not MsgWorklist")
            msg_rsp = msg + 2  # fail
            return (ERR_FATAL, msg_rsp)            

        try:
            # base on sn(thread)
            desc = "CPE(SN=%s) start process to execute worklist(%s)." %(
                    obj.sn, obj.worklist_name)
            log.app_info(desc) 
            
            thread1 = CpeThread(msg, obj)
            thread1.start()
            
            ret = ERR_SUCCESS 
            msg_rsp = msg + 1  # response(async)
        except Exception,e:
            # sn is busy
            ret = ERR_FAIL
            msg_rsp = msg + 2  # fail
            
            obj.dict_ret["str_result"] = str(e)
            log.app_info(e)               
    
        return (ret, msg_rsp)       


    @staticmethod        
    def do_worklist_download(msg, obj):
        """
        obj = MsgWorklistDownload
        """
        ret = None
        
        # check
        if (not isinstance(obj, MsgWorklistDownload)):
            log.app_err("obj is not MsgWorklistDownload")
            msg_rsp = msg + 2  # fail
            return (ERR_FATAL, msg_rsp)    
        
        msg_rsp = msg + 2 # default, fail                 
        for nwf in [1]:        
            try:            
                ret = Worklist.build_download_msg(obj)
                if (ret != ERR_SUCCESS):
                    break
                    
            except Exception,e:
                print_trace(e)
                
                obj.dict_ret["str_result"] = str(e)                
                ret = ERR_FAIL
                break         

            ret = ERR_SUCCESS
            msg_rsp = msg + 1

        return (ret, msg_rsp)


    @staticmethod    
    def request_write(request, body):
        """
        auto add header:
        """
        
        request.setHeader("Content-Type", "text/xml; charset=utf-8")      
        request.setHeader("Server", "tr069-worklist")
        request.setHeader("SOAPAction", "")
  
        request.setHeader("Content-Length", len(body))
        
        import datetime
        format1="%a, %d %b %Y %H:%M:%S GMT"
        time1=datetime.datetime.utcnow().strftime(format1)
        request.setHeader("Date", time1)
        request.setHeader("Content-Length", len(body))

        request.write(body)
        request.finish()  


    @staticmethod 
    def send_msg(request, msg_rsp, obj):
        """
        echo sender
        """
        ret             = ERR_FAIL  
        str_dict_msg    = ""
        

        ip = request.transport.client[0]
        port = request.transport.client[1]

        desc = "send %s(ip=%s, port=%s)" %(get_event_desc(msg_rsp), ip, port)
        log.app_info(desc)
        try:
            strio = StringIO()
            pickle.dump(obj, strio)  

            try:
                dict1  = Worklist.get_user_dictmsg(request)
                seq = dict1.get(KEY_SEQUENCE)
            except Exception,e:
                print_trace(e) 
                dict1  = {}

            dict1[KEY_MESSAGE]      = msg_rsp
            dict1[KEY_OBJECT]       = strio.getvalue()                  
            dict1[KEY_SENDER]       = KEY_SENDER_WORKLIST  

            str_dict_msg = str(dict1)
            
            Worklist.request_write(request, str_dict_msg)
            UsersMsgSeq.save_user_rsp_msg(seq, str_dict_msg) 
            
            ret = ERR_SUCCESS           
            
        except Exception,e:
            print_trace(e)                
        
        return ret 


    @staticmethod    
    def process_user_message_seq_exist(request, msg):
        """              
        """  

        Worklist.request_write(request, msg)
                
        return None 


    @staticmethod        
    def build_download_msg(obj):
        """
        obj = MsgWorklistDownload
        """
        
        ret         = ERR_SUCCESS  # default
        ret_api     = None
        obj.cpe_interface_versions = []  # clear


        for nwf in [1]:
        
            try:
                root_dir = worklistcfg.SCRIPT_ROOT_DIR  # tr069v3\lib\worklist\operator

                operator = obj.operator
                # tr069v3\lib\worklist\operator\CT
                dir_operator = os.path.join(root_dir, operator)  
                ret_api = os.path.isdir(dir_operator)
                if (ret_api == False):
                    desc = "%s is not dir in worklist server." %(dir_operator)
                    obj.dict_ret["str_result"] = desc
                    log.app_err(desc)
                    break               

                # v3.0 + v4.0                                        
                for root_operator,cpe_interface_versions,files_operator in os.walk(dir_operator):

                    # travel interface_versions
                    for cpe_interface_version in cpe_interface_versions:                     

                        # tr069v3\lib\worklist\operator\CT\v3.0
                        dir_interface_version = os.path.join(dir_operator, cpe_interface_version)                

                        # save --------
                        cls_cpe_interface_version = MsgWorklistCpeInterfaceVersion(cpe_interface_version)
                        obj.cpe_interface_versions.append(cls_cpe_interface_version)
                            
                        # tr069v3\lib\worklist\operator\CT\v3.0\business
                        dir_business = os.path.join(dir_interface_version, worklistcfg.BUSINESS_DOMAINS)  
                        ret_api = os.path.isdir(dir_business)
                        if (ret_api == False):
                            desc = "%s is not dir in worklist server." %(dir_business)
                            obj.dict_ret["str_result"] = desc
                            log.app_err(desc)
                            break 
                            
                        # travel domain
                        for root_domain,dirs_domain,files_domain in os.walk(dir_business):
                        
                            for dir_domain in dirs_domain: 

                                if (dir_domain in ["ADSL"]):
                                    # "ADSL is debug dir"
                                    continue

                                # save --------
                                cls_domain = MsgWorklistDomain(name=dir_domain)
                                cls_cpe_interface_version.domains.append(cls_domain)


                                # travel cpe device type
                                path_domain = os.path.join(root_domain, dir_domain)
                                for root_worklist,dirs_worklist,files_worklist in os.walk(path_domain):

                                    for dir_worklist in dirs_worklist:
                                    
                                        # E:\____python\tr069\TR069_BS2_nwf\TR069\lib\worklists\operator\CT\v3.0\business\ADSL_2LAN\INTERNET_PPPoE_Disable
                                        worklist_name= dir_worklist
                                        dir_worklist = os.path.join(root_domain, dir_domain, worklist_name)     

                                        # E:\____python\tr069\TR069_BS2_nwf\TR069\lib\worklists\operator\CT\v3.0\business\ADSL_2LAN\INTERNET_PPPoE_Disable\data.py                         
                                        file_data = os.path.join(dir_worklist, 
                                                                worklistcfg.SCRIPT_DATA_FILE_NAME+".py")  
                                        ret_api = os.path.isfile(file_data)
                                        if (ret_api == False):
                                            desc = "%s is not file in worklist server." %(file_data)
                                            obj.dict_ret["str_result"] = desc
                                            log.app_err(desc)
                                            break                                        
               
                                        # save --------
                                        cls_datafile = MsgWorklistFile(worklist_name)
                                        cls_domain.wl_datafiles.append(cls_datafile)

                                        path1 = os.path.join(root_worklist, worklist_name)
                                        sys.path.insert(0, path1)
                                        import data
                                        dict_data = str(data.WORKLIST_ARGS)
                                        sys.path.pop(0)                                
                                        cls_datafile.dict_data = dict_data

                                    # 1 level device
                                    break
                                    
                            #only 1 level(domain)
                            break
                        
                    # only 1 level(operator)
                    break
                    
            except Exception,e:
                print_trace(e)
                ret = ERR_FAIL

        return ret


    @staticmethod        
    def process_query(request, msg, obj):
        """
        obj = MsgQueryIsHang
        """
        ret = None
        msg_rsp = msg + 2   # default =fail
        
        for nwf in [1]:
            
            if (msg == EV_QUERY_IS_HANG_RQST):
                
                ret, msg_rsp = Worklist.on_rx_query_is_hang(msg, obj)
                if (ret == ERR_FATAL):
                    # fatal 
                    break                            
                
            else:                
                log.app_err("unknow worklist message(%s)" %msg)
                # sender timeout
                ret = ERR_FAIL
                break
        
            # handle msg ok, echo sender
            ret = Worklist.send_msg(request, msg_rsp, obj)    
    
        return ret  


    @staticmethod        
    def on_rx_query_is_hang(msg, obj):    
        """
        obj = MsgQueryIsHang
        """
        ret = ERR_FAIL  # default
        cpe = None        
        msg_rsp = msg + 2 # default
        

        for nwf in [1]:
            # check args
            if (not isinstance(obj, MsgQueryIsHang)):
                log.app_err("obj is not MsgQueryIsHang")  
                ret = ERR_FATAL
                break            
        
            ret = ERR_SUCCESS
            msg_rsp = msg + 1
                       
        return ret,msg_rsp

    

if __name__ == '__main__':
    pass
 
