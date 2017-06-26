#coding:utf-8

# ***************************************************************************
#
#  nwf      2012-08-13      V1.0
#  nwf      2013-05-24      refactor(unify)
#  nwf      2013-06-20      cpe split to (property + soap + user)
# ***************************************************************************

# sys lib
import  sys
import  os
from    cStringIO                   import  StringIO
from    datetime                    import  datetime, timedelta
from    functools                   import  partial
import  inspect
import  pickle
import  re
import  time
from    threading                   import  Timer
from    twisted.internet            import  reactor, threads
from    twisted.web                 import  http
from    twisted.web.server          import  NOT_DONE_YET
import  urllib
import  urlparse


# user lib
from    TR069.lib.common.error          import  *
from    TR069.lib.common.event          import  *
import  TR069.lib.common.logs.log       as      log 
from    TR069.lib.common.httpclient     import  HttpClient
from    TR069.lib.common.function       import  *
import  TR069.lib.acss.acs.webservercfg         as      webservercfg
from    acsauth                         import  get_url, AUTHENTICTATE_SUCCEED   
from    cpeauth                         import  authenticate_acs_cperequest, ACS_AUTHENTICATE_PASS, ACS_AUTHENTICATE_FAIL    # http auth
import  construct   # SOAP 
import  parse
from    rpcstruct                   import  *    # SOAP
import  verify      # SOAP
from    cpe_db                      import  *

from    cpe_db_index                import  CpeDbIndex
from    cpe_property                import  CpeProperty
from    cpe_soap                    import  CpeSoap
from    cpe_user                    import  CpeUser
from    cpe_user_worklist           import  CpeUserWorklist
from    cpe_operator                import  CpeOperator
from    inform_monitor              import  InformMonitor
from    cpe_thread                  import  AcsCpeThread
import  testlibversion

# ----------------------------------------------------------------------

# status
CPE_ST_INIT                 = 0     # cpe created
CPE_ST_WAIT_POST_NULL       = 1
CPE_ST_WAIT_RPC_RESPONSE    = 2
CPE_ST_READY                = 3     # after send 204

#  timer config
TIMER_WAIT_POST_NULL        = 60    #  seconds
TIMER_WAIT_RPC_RESPONSE     = 60



# soap msg
CWMP_INFORM                 = "Inform"
CWMP_INFORM_RESPONSE        = "InformResponse"
CWMP_POST_NULL              = "PostNull"        #  define
CWMP_NOCONTENT              = "CwmpNoContent"   #  define


# global variable
dict_all_parameters_type    = {}


class CPE(object):
    """
    server cpe
    """    
    
    m_dict_sn2cpe                   = dict()    # inform & user rpc can create cpe 
    m_dict_sessionno2cpe            = dict()    # {session, sn)  
    m_dict_double_sessionno         = dict()    # (sessionno, True) for connection lost use  
   
    m_last_request                  = None      # 
    
    
    def __init__(self, sn):
        """
        
        """
        self.cpe_id                 = 0
        self.sn                     = sn        #  2013-03-17 update to oui-sn           
        self.status                 = CPE_ST_INIT  


        # property, only 1
        self.cpe_property           = CpeProperty(self)

        # soap
        self.cpe_soap               = CpeSoap(self)               

        # user
        self.cpe_user               = CpeUser(self)     

        # monitor inform
        self.inform_monitor         = InformMonitor(self) 

        # cpe thread
        self.cpe_thread             = AcsCpeThread(self)

        # db index
        self.curr_rpc_name              = ''
        self.cpe_db_index           = CpeDbIndex(self)
    

    # assist --------------------------------------------------------
    
    def get_sn(self):
        return self.sn
    
    def set_cpe_id(self, cpe_id):
        self.cpe_id = cpe_id
        
    def get_cpe_id(self):
        return self.cpe_id
    
    def set_status(self, status):
        old = self.get_status()
        old_desc = self.get_status_desc()
        if (status != old):
            self.status = status        
            log.app_info("cpe(sn=%s), status swtiched(%s->%s)" 
                         %(self.get_sn(), old_desc, self.get_status_desc()))
    def get_status(self):
        return self.status
        
    def get_status_desc(self):
        """
        status(int convert to str)
        """
        status_desc = ""
        
        status = self.get_status()        
        if (status == CPE_ST_INIT):
            status_desc = "CPE_ST_INIT"
        elif (status == CPE_ST_WAIT_POST_NULL):
            status_desc = "CPE_ST_WAIT_POST_NULL"
        elif (status == CPE_ST_WAIT_RPC_RESPONSE):
            status_desc = "CPE_ST_WAIT_RPC_RESPONSE"
        elif (status == CPE_ST_READY):
            status_desc = "CPE_ST_READY"
        else :
            status_desc = ("status(%s) not known"  %status)

        return status_desc 

    @staticmethod
    def update_double_sessionno(sessionno):
        d1 = {sessionno:True}
        CPE.m_dict_double_sessionno.update(d1)
    @staticmethod
    def pop_double_sessionno(sessionno):
        CPE.m_dict_double_sessionno.pop(sessionno)
        
    @staticmethod
    def get_last_request():
        return CPE.m_last_request
    @staticmethod
    def set_last_request(request):
        CPE.m_last_request = request        

                

    # --------------------------------------------------------------------
    # -----------------------soap msg entry  --------------------------
    # --------------------------------------------------------------------
    @staticmethod    
    def dispatch_soap(request):    
        """
        request = twisted.web.server.Request
        """  
        ret = None

        # save
        CPE.set_last_request(request)
        
        ret = CPE.process_head(request)
        if (ret != ERR_SUCCESS):                  
            return ret

        ret = CPE.process_auth(request)
        if (ret != ERR_SUCCESS):                  
            return ret
        
        ret = CPE.process_body(request)
        
        return ret

    # ---------------------------  user msg entry -------------- 
    @staticmethod    
    def dispatch_user(request):    
        """
        request = twisted.web.server.Request user
        """  
        ret         = ERR_FAIL  # default
        ret_api     = None

        # save
        CPE.set_last_request(request)

        for nwf in [1]:

            # dict in?
            try:
                body = request.content.read()
                dict1 = eval(body)
            except Exception,e:
                log.app_err("request content read, isn't a dict(%s)." %(e))
                break

            CpeUser.set_user_dictmsg(request, dict1)            

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
                CPE.process_user_message_seq_exist(request, msg)
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

            # mysql
            #insert_acs_log(get_event_desc(v_msg), body)
            
            # dispatch
            try:
                msg_group = int(v_msg) & 0xFF00
                if (msg_group == EVENT_RPC_GROUP): 
                    if (v_msg == EV_RPC_AGENT_TIMEOUT_POST):
                        ret = CPE.process_agent_timeout_sync(request, v_msg, obj)
                    else:
                        ret = CPE.process_user_rpc_short_connection(request, v_msg, obj)
                elif (msg_group == EVENT_QUERY_GROUP):                
                    ret = CPE.process_query(request, v_msg, obj)
                elif (msg_group == EVENT_CONFIGURE_GROUP):                
                    ret = CPE.process_config(request, v_msg, obj)    
                elif (msg_group == EVENT_WORKLIST_GROUP):
                    ret = CPE.process_worklist4user(request, v_msg, obj)
                else:
                    log.app_err("user message group(=%d) not support." %msg_group)
                    break
            except Exception,e:
                print_trace(e) 
                break
            ret = ERR_SUCCESS  # not use
        
        return NOT_DONE_YET   #  async

        
    @staticmethod    
    def process_head(request):    
        """
        request = twisted.web.server.Request
        """  
        
        ret                 = None    
        ret_api             = None
        cpe                 = None
        cwmp_version        = "cwmp-1-0" # default
        soap_verify         = None
        soap_message        = None
        cwmp_id             = None        
        content_head        = ""
        content_body        = ""
        is_sessionno_exist  = False
        content_head_in    = ""
        

        try:
            # save_in_head
            content_head_in = request.transport.protocol.content_head_in
        except Exception,e:        
            pass
  
        head = request.requestHeaders
        body = request.content.read()
        
        # mysql  
        content_head = str(head)
        content_body = body        
        
        soap_sessionno = request.transport.sessionno
        cpe = CPE.get_cpe_bysessionno(soap_sessionno) 
        if (cpe):
            is_sessionno_exist = True
              
        for nwf in [1]:
            # step1  get soap obj
            if (body == ""):

                soap_message = CWMP_POST_NULL    # body = ""  means post null
                
            else :

                soap_verify = verify.Verify()
                ret_api = soap_verify.check_soap_msg(body)
                if ret_api == verify.VERIFY_ERR_UNSUPPORT_RPC_METHOD:

                    ret = CPE.process_rpc_outoftr069(request, soap_verify)
                    break
                    
                elif (ret_api == verify.VERIFY_FAIL):
                    #  soap fail, echo 400  BAD_REQUEST
                    log.app_err("check_soap_msg fail.")            

                    ret = CPE.process_soap_fail(request)
                    break                    

                # soap ok  
                soap_message = soap_verify.cur_RPC_name   
                               
                try:
                    cwmp_id = soap_verify.soap_header_cwmp_id # update(soap may not include header)
                except Exception,e:
                    pass
            
            # is inform? need create cpe ; otherwise get cpe by sessionno
            if (soap_message == CWMP_INFORM):

                oui = soap_verify.result.DeviceId.OUI
                sn = soap_verify.result.DeviceId.SerialNumber   
                oui_sn = "%s-%s" %(oui, sn)
                
                # nwf 2013-06-27; 2 session 1 cpe?
                ret = CPE.is_2session1cpe(oui_sn, soap_sessionno)
                if (ret):
                    CPE.update_double_sessionno(soap_sessionno)
                    
                    CPE.process_2session1cpe(request, oui_sn)

                    ret = ERR_FAIL
                    break

                cpe = CPE.add(oui_sn, soap_sessionno)
                
                # save              
                cpe.cpe_soap.set_soap_sessionno(soap_sessionno)
                cpe.cpe_soap.set_soap_inform(soap_verify)

                cwmp_version = soap_verify.cur_cwmp_version 
                version_cfg = cpe.cpe_soap.get_cwmpversion()
                if ((version_cfg == "Auto") or (not version_cfg)):
                    # gui config = "Auto" or not cfg
                    cpe.cpe_soap.set_cwmpversion(cwmp_version) # only inform include
                
                root_node = soap_verify.result.ParameterList[0].Name.split('.')[0]
                soft_ver = soap_verify.result.DeviceId.Softwareversion
                hard_ver = soap_verify.result.DeviceId.Hardwareversion
                acs2cpe_url = soap_verify.result.DeviceId.ConnectionRequestURL
                #cpe.cpe_property.set_acs2cpe_url(acs2cpe_url)
                
                dict_col = {}
                dict_data = {}
                if cpe.cpe_property.is_update_acs2cpe_url(acs2cpe_url):
                    dict_col['CONN_RQST_URL'] = acs2cpe_url
                    
                if cpe.cpe_property.is_update_software_version(soft_ver):
                    dict_col['SOFTWARE_VERSION'] = soft_ver
                    
                if cpe.cpe_property.is_update_hardware_version(hard_ver):
                    dict_col['HARDWARE_VERSION'] = hard_ver
                    
                # 动态数根节点
                if cpe.cpe_property.is_update_root_node(root_node):
                    dict_col['ROOT_NODE'] = root_node
                    
                # 最后交互时间
                time_contact = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if cpe.cpe_soap.is_update_contact_time(time_contact):
                    dict_col['TIME_LAST_CONTACT'] = time_contact
                
                if dict_col:
                    # 字典的值不为空时，才更新数据库
                    dict_data['columns'] = dict_col
                    dict_data['condition'] = 'CPE_ID=%s' % cpe.get_cpe_id()
                    operate_db('CPE', 'UPDATE', dict_data)

                # mysql      
                if (not is_sessionno_exist): 
                    event_codes = CPE.get_inform_eventcodes(soap_verify)
                    for code_item in event_codes:
                        if code_item == '6 CONNECTION REQUEST':
                            # insert_rpc = True
                            break
                    else:
                        cpe.curr_rpc_name = 'Inform'
                        db_rpc_id = insert_acs_rpc(oui_sn, 'Inform', '', 0)
                        cpe.cpe_db_index.set_rpc_id(db_rpc_id)
                    str_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    cpe.cpe_soap.time_s2_start = str_time
                    update_acs_rpc_time(cpe, 'TIME_S2_START', str_time)                        
                    # Alter by lizn 2014-03-10               
                
                eventcodes      = CPE.get_inform_eventcodes(soap_verify)  
                inform_soap_id = insert_acs_soap(soap_message, "IN", oui_sn, content_head, content_head_in, content_body, str(eventcodes))                
                cpe.cpe_db_index.set_soap_inform_id(inform_soap_id)

                # nwf 2014-02-25; save to memory
                if (cpe.cpe_user.user_rpc and 
                    (cpe.cpe_user.user_rpc.rpc_name != "connection_request")):
                    cpe.cpe_db_index.set_soap_inform_id_4rpc(inform_soap_id)

            else:      
                if (cpe is None):
                    log.app_err("cpe is none(soap message=%s, sessionno=%s)." 
                                %(soap_message, soap_sessionno))
                    ret = ERR_FAIL
                    break  

                # mysql                
                insert_acs_soap(soap_message, "IN", cpe.get_sn(), content_head, content_head_in, content_body)
                                    
            cpe.cpe_soap.set_soap_msg(soap_message)  # save
            cpe.cpe_soap.set_soap_verify(soap_verify)            
            cpe.cpe_soap.set_cwmpid(cwmp_id)  # save   
            
            cpe.cpe_property.set_cpe_request(request) # save cpe session               
    
            ret = ERR_SUCCESS  # allright is right        
        
        return ret


    @staticmethod 
    def process_auth(request):  
        """
        """
        ret = None
        
        soap_sessionno = request.transport.sessionno
        cpe = CPE.get_cpe_bysessionno(soap_sessionno) 
        sn = cpe.get_sn()
        
        # step2  http auth
        ret = cpe.is_auth(request, sn)
        if (ERR_SUCCESS != ret):
            CPE.request_write(request, "", "auth_fail", sn)   #zsj add

        if (ERR_FAIL == ret):   
            # only auth fail/success is result(auth fatal=need second inform)
            desc = "cpe auth fail"
            cpe.on_tx_user_rpc_fail(desc)
            
        return ret
        
    
    @staticmethod    
    def process_body(request):    
        """
        request = twisted.web.server.Request
        require process_head ok
        """  
        ret = None
        
        soap_sessionno = request.transport.sessionno
        cpe = CPE.get_cpe_bysessionno(soap_sessionno)  
        
        status = cpe.get_status()
        soap_message = cpe.cpe_soap.get_soap_msg()
        
        if (status ==CPE_ST_INIT):
            
            ret = cpe.process_st_init(request, soap_message)            
        elif (status ==CPE_ST_WAIT_POST_NULL):
            
            ret = cpe.process_st_wait_postnull(request, soap_message)            
        elif (status ==CPE_ST_WAIT_RPC_RESPONSE):
            
            ret = cpe.process_st_wait_rpcresponse(request, soap_message)        
        elif (status ==CPE_ST_READY):
            
            ret = cpe.process_st_ready(request, soap_message)        
        else :
            log.app_err("invalid status=%s" %status)
            ret = ERR_FAIL
        
        return ret 
        

    @staticmethod     
    def process_rpc_outoftr069(request, soap_verify):
        """
        """

        # CPE sended RPC is not supported on ACS  ---added by lana
        # When ACS send Fault, the session is over, user will return when time out
        cwmp_version = soap_verify.cur_cwmp_version
        CPE.tx_fault(request, 
                        cwmp_version,
                        ["8000", "Methods not supported"], 
                        soap_verify.soap_header_cwmp_id)
                        
        CPE.on_connection_lost(request.transport)

        return ERR_SUCCESS # skip err


    @staticmethod 
    def process_soap_fail(request):
        """
        cpe's soap msg is wrong, echo back to cpe only, effect nothig
        """
        
        request.setResponseCode(400, "Bad Request")
        CPE.request_write(request, "", "soap_fail")
        
        return ERR_FAIL # exit flow

    
    # ------------------------------------- status machine ---------------------
    def process_st_init(self, request, soap_message):
        """
        only recv inform
        """
        ret = None
        
        if (soap_message == CWMP_INFORM):
            ret = self.on_rx_inform(request, soap_message)   
        else :
            ret = ERR_FAIL
            log.app_err("cpe sn=%s, status=%s, soap message=%s can't processed." 
                    %(self.get_sn(), self.get_status_desc(), soap_message))            
        
        return ret

        
    def process_st_wait_postnull(self, request, soap_message):
        """
        only recv post null or timeout
        """
        ret = None
        
        if (soap_message == CWMP_POST_NULL):
            ret = self.on_rx_post_null(request, soap_message)
        else:
            ret = self.process_acs_rpc(request, soap_message)            
    
        return ret

    
    def process_st_wait_rpcresponse(self, request, soap_message):
        """
        only recv rpc response or timeout
        """
        ret = None
        
        if (soap_message == "Fault"):
            #  prior to fault
            ret = self.on_rx_rpc_fault(request, soap_message)
        elif ((self.cpe_user.get_user_rpc().rpc_name + "response").lower() == soap_message.lower()):
            # is rpc response?
            ret = self.on_rx_rpc_response(request, soap_message) 
        else:
            ret = ERR_FAIL
            log.app_err("cpe sn=%s, status=%s, soap message=%s can't processed." 
                    %(self.get_sn(), self.get_status_desc(), soap_message))            

        return ret

    
    def process_st_ready(self, request, soap_message):
        """
        only recv inform 
        """
        ret = None
        
        if (soap_message == CWMP_INFORM):
            ret = self.on_rx_inform(request, soap_message)           
        else :
            ret = ERR_FAIL
            log.app_err("cpe sn=%s, status=%s, soap message=%s can't processed." 
                    %(self.get_sn(), self.get_status_desc(), soap_message))   
        
        return ret


    @staticmethod    
    def process_agent_timeout_sync(request, msg, obj): 
        """
        should be config msg, not me defined
        
        """
        ret         = ERR_FAIL   
        cpe         = None        
        desc        = ""       
        msg_rsp     = msg +1 # default(no fail)
        
        for nwf in [1]:  
        
            # check args in
            if (not isinstance(obj, MsgRpcTimeout)):
                desc    = "obj is not MsgRpcTimeout."
                log.app_err(desc)

                obj.dict_ret["str_result"] = desc
                
                ret     = ERR_FATAL                
                break 
                
            sn              = obj.sn
            user_rpc_obj    = obj.user_rpc_obj
            user_rpc_name   = user_rpc_obj.rpc_name            

            # sn ?
            cpe = CPE.get_cpe(sn)
            if (cpe is None):
                desc    = "cpe is not on line."
                log.app_err(desc)

                obj.dict_ret["str_result"] = desc
                              
                break             
            
            # match?
            acs_user_rpc    = cpe.cpe_user.get_user_rpc()
            if (not acs_user_rpc):
                desc    = "cpe user rpc is None"
                log.app_err(desc)

                obj.dict_ret["str_result"] = desc
                             
                break                 

            if (acs_user_rpc.rpc_name != user_rpc_name):
                desc    = "acs user rpc name(%s) != user rpc name(%s)" %(acs_user_rpc.rpc_name, user_rpc_name)
                log.app_err(desc)

                obj.dict_ret["str_result"] = desc
                              
                break  
             
            # close cpe session; clear acs user rpc
            cpe.close_session()
            cpe.cpe_user.set_user_rpc(None) 
            cpe.cpe_thread.cancel_thread_userrpc_get_url()
                    
        ret = CPE.on_tx_user_response(request, msg_rsp, obj)
                
        return ret  



    @staticmethod    
    def process_user_rpc_short_connection(request, msg, obj):    
        """
        request = twisted.web.server.Request user 
        msg = eg, EV_RPC_SETPARAMETERVALUES_RQST
        obj = MsgUserRpc
        short connection, ack first, then do rpc, then report to agent
        """  
        ret     = ERR_FAIL   
        cpe     = None        
        desc    = ""
        
        obj_ret = MsgUserRpcCheck()
        obj_ret.event_rqst = msg
        
        for nwf in [1]:  
        
            # check args in
            if (not isinstance(obj, MsgUserRpc)):
                desc    = "obj is not MsgUserRpc"
                log.app_err(desc)

                obj_ret.dict_ret["str_result"] = desc
                
                ret     = ERR_FATAL
                
                break 
        
            sn          = obj.sn
            rpc_name    = obj.rpc_name            
        
            cpe = CPE.get_cpe(sn)
            if (cpe is None):
                cpe = CPE.add(sn, None)
            
            cpe.cpe_user.set_user_request(request)  # save
            cpe.cpe_user.set_user_event(msg)

            # busy?
            obj_old = cpe.cpe_user.get_user_rpc()
            if (obj_old):
                desc = "cpe(sn=%s) rpc(%s) is busy." %(sn, obj_old.rpc_name)
                log.app_err(desc)

                obj_ret.dict_ret["str_result"] = desc

                break

            # args valid?
            cpe.cpe_user.set_next_user_rpc(obj)  # pre
            ret = cpe.check_user_cmd_valid(obj)
            if (ret != ERR_SUCCESS):
                cpe.cpe_user.set_next_user_rpc(None) # restore
                break                

            log.app_info("cpe(sn=%s, user rpc=%s) configure success." %(sn, rpc_name)) 

            # mysql; compatible for lower version
            worklist_id = ""
            if (hasattr(obj, "worklist_id")):      
                id_desc = obj.worklist_id
                #worklist_id = CpeUserWorklist.m_dict_desc_id.get(id_desc, '')
                ret_obj = restore_acs_part_worklist(id_desc)
                if ret_obj:
                    worklist_id = ret_obj.worklist_id
                    log.app_info('[%s]id=%s' % (worklist_id, id_desc))
                
            db_rpc_id = insert_acs_rpc(sn, rpc_name, str(obj.rpc_args), worklist_id)
            cpe.cpe_db_index.set_rpc_id(db_rpc_id)
            
            # clear last fault
            cpe.cpe_soap.set_last_faults(None)
                        
            ret = ERR_SUCCESS

        # ack first            
        CPE.on_tx_user_response_short_connection(request, ret, obj_ret)
        # then rpc
        if (ret == ERR_SUCCESS):            
            CPE.process_user_rpc_async(cpe)
                
        return ret    


    @staticmethod    
    def process_user_rpc_async(cpe):    
        """
        """                                                                          

        # fire
        d=threads.deferToThread(CPE.process_user_rpc_geturl, cpe)
        d.addCallback(CPE.process_user_rpc_callback, cpe)

        cpe.cpe_thread.set_thread_userrpc_get_url(d)    # save
                
        return None        


    @staticmethod    
    def process_user_rpc_geturl(cpe):    
        """
        in thread 
        """    
        ret = ERR_FAIL
        err_message = ""

        try:
            # strategy wait cpe's session lost ;max 20s
            i = 0
            while (1):
            
                # last rpc ok?
                if (cpe.cpe_soap.get_soap_sessionno() is None):

                    # push next rpc
                    cpe.cpe_user.set_user_rpc(cpe.cpe_user.get_next_user_rpc())
                    cpe.cpe_user.set_next_user_rpc(None)
                    
                    break
                else:
                    desc = "cpe(sn=%s) session is active, waiting(%s) seconds" %(cpe.get_sn(), i+1)
                    log.app_info(desc)
                
                # timeout?
                if (i >= webservercfg.WAIT_CPE_SESSION_LOST_TIMEOUT):
                    # acs close cpe session
                    cpe.close_session()
                    time.sleep(1)  
                    continue                

                time.sleep(1)
                i = i + 1                
            
            ret, err_message =cpe.get_url()

        except Exception,e:
            print_trace(e) 
        
        return ret, err_message


    @staticmethod    
    def process_user_rpc_callback(args, cpe):    
        """
        get url 
        """  
        
        ret, err_message = args

        if (ret != ERR_SUCCESS):
            desc = "message:%s" % err_message
            cpe.on_tx_user_rpc_fail(desc)
        else:

            # only get_url?
            user_rpc = cpe.cpe_user.get_user_rpc()
            if (user_rpc and (user_rpc.rpc_name == "connection_request")):

                user_msg_response = int(cpe.cpe_user.get_user_event()) + 1  # success
                cpe.on_tx_user_rpc_response(user_msg_response)
            
            else:
        
                # wait inform
                timer = reactor.callLater(60 ,on_user_timeout_60s, cpe)
                cpe.cpe_user.set_user_timer_60s(timer)       
        
        return None


    def process_acs_rpc(self, request, soap_message):  
        """
        
        """
        ret = None

        if (soap_message == "GetRPCMethods"):
            ret = self.process_getrpcmethods(request, soap_message)
        elif (soap_message == "TransferComplete"):
            ret = self.process_noparameter_rpc(request, soap_message)
        elif (soap_message == "AutonomousTransferComplete"):
            ret = self.process_noparameter_rpc(request, soap_message)
        elif (soap_message == "Kicked"):
            ret = self.process_kicked(request, soap_message)
        elif (soap_message == "RequestDownload"):
            ret = self.process_noparameter_rpc(request, soap_message)
        elif (soap_message == "DUStateChangeComplete"):
            ret = self.process_noparameter_rpc(request, soap_message)
        elif (soap_message == "AutonomousDUStateChangeComplete"):
            ret = self.process_noparameter_rpc(request, soap_message)
        elif soap_message == "Inform":
            ret = self.on_tx_inform_response(request, soap_message)
        else:
            # echo 8000
            ret = self.process_acs_rpc_notsupport(request, soap_message)
        
        return ret


    def process_getrpcmethods(self, request, soap_message):  
        """
        
        """
        ret         = None
        desc        = ""
        ret_api     = None
        sn          = self.get_sn()

        for nwf in [1]:
            try:
                log.app_info("----------(cpe status=%s; soap message=%s)----------" 
                            %(self.get_status_desc(), soap_message))
                
                obj_construct = construct.Construct()
                if self.cpe_soap.get_cwmpversion() == "cwmp-1-0":
                    rpcs = ["GetRPCMethods", 
                            "Inform", "TransferComplete",
                            "Kicked", "RequestDownload"]
                elif self.cpe_soap.get_cwmpversion() == "cwmp-1-1":
                    rpcs = ["GetRPCMethods", 
                            "Inform", "TransferComplete",
                            "AutonomousTransferComplete",
                            "Kicked", "RequestDownload"]
                elif self.cpe_soap.get_cwmpversion() in ["cwmp-1-2", "cwmp-1-3"]:
                    rpcs = ["GetRPCMethods", 
                            "Inform", "TransferComplete",
                            "AutonomousTransferComplete",
                            "Kicked", "RequestDownload",
                            "DUStateChangeComplete",
                            "AutonomousDUStateChangeComplete"]
                else:
                    rpcs = []
                    
                obj_getrpcmethodsresponse = GetRPCMethodsResponse() # rpc args
                obj_getrpcmethodsresponse.MethodList = rpcs

                soap_message_rsp = soap_message + "Response"
                ret_api, desc = obj_construct.create_soap_envelope(soap_message_rsp, 
                                                                    self.cpe_soap.get_cwmpversion(), 
                                                                 obj_getrpcmethodsresponse, 
                                                                    self.cpe_soap.get_cwmpid())
                if (construct.CONSTRUCT_SUC != ret_api):
                    log.app_err(desc)
                    ret = ERR_FAIL
                    break
                
                # add head
                CPE.request_write(request, obj_construct.str_xml, soap_message_rsp, sn)                
                
            except Exception,e:
                log.app_err("%s" %e)
                ret = ERR_FAIL
                break
            ret = ERR_SUCCESS
            
        return ret


    def process_acs_rpc_notsupport(self, request, soap_message):  
        """
        
        """
        ret         = None
        desc        = ""
        ret_api     = None
        sn          = self.get_sn()

        for nwf in [1]:
            try:
                log.app_info("----------(cpe status=%s; soap message=%s not support)----------" 
                            %(self.get_status_desc(), soap_message))


                obj_construct = construct.Construct()            
                obj_fault = Fault()
                obj_fault.faultcode = "Server"
                obj_fault.faultstring = "CWMP fault"
                
                obj_fault.detail = CWMPFaultStruct()                
                obj_fault.detail.FaultCode = 8000
                obj_fault.detail.FaultString = "rpc (%s) not support" %(soap_message)
                
                ret_api, desc = obj_construct.create_soap_envelope("Fault", 
                                                                    self.cpe_soap.get_cwmpversion(), 
                                                                    obj_fault, 
                                                                    self.cpe_soap.get_cwmpid())                
                if (construct.CONSTRUCT_SUC != ret_api):
                    log.app_err(desc)
                    ret = ERR_FAIL
                    break
                
                # add head
                CPE.request_write(request, obj_construct.str_xml, "Fault", sn)                
                
            except Exception,e:
                print_trace(e) 
                ret = ERR_FAIL
                break
                
            ret = ERR_SUCCESS
            
        return ret

    
    def process_kicked(self, request, soap_message):  
        """
        
        """
        ret         = None
        desc        = ""
        ret_api     = None
        sn          = self.get_sn()

        for nwf in [1]:
            try:
                log.app_info("----------(cpe status=%s; soap message=%s)----------" 
                            %(self.get_status_desc(), soap_message))
                
                obj_construct = construct.Construct()            
                obj_kicked = KickedResponse()
                obj_kicked.NextURL = "http://unsupport.now"

                soap_message_rsp = soap_message + "Response"
                ret_api, desc = obj_construct.create_soap_envelope(soap_message_rsp, 
                                                                    self.cpe_soap.get_cwmpversion(), 
                                                                    obj_kicked, 
                                                                    self.cpe_soap.get_cwmpid())
                if (construct.CONSTRUCT_SUC != ret_api):
                    log.app_err(desc)
                    ret = ERR_FAIL
                    break
                
                # add head
                CPE.request_write(request, obj_construct.str_xml, soap_message_rsp, sn)                
                
            except Exception,e:
                log.app_err("%s" %e)
                ret = ERR_FAIL
                break
                
            ret = ERR_SUCCESS
            
        return ret

    
    def process_noparameter_rpc(self, request, soap_message):  
        """
        
        """
        ret         = None
        desc        = ""
        ret_api     = None
        sn          = self.get_sn()

        for i in [1]:
            try:
                log.app_info("----------(cpe status=%s; soap message=%s)----------" 
                            %(self.get_status_desc(), soap_message))
                
                obj_construct = construct.Construct()             

                soap_message_rsp = soap_message + "Response"
                ret_api, desc = obj_construct.create_soap_envelope(soap_message_rsp, 
                                                                    cwmp_version=self.cpe_soap.get_cwmpversion(),  
                                                                    cwmp_id=self.cpe_soap.get_cwmpid())
                if (construct.CONSTRUCT_SUC != ret_api):
                    log.app_err(desc)
                    ret = ERR_FAIL
                    break
                
                # add head
                CPE.request_write(request, obj_construct.str_xml, soap_message_rsp, sn)                
                
            except Exception,e:
                log.app_err("%s" %e)
                ret = ERR_FAIL
                break
            ret = ERR_SUCCESS
            
        return ret    


    @staticmethod    
    def process_query(request, msg, obj):    
        """
        request = user request 
        """  
        ret = None
        cpe = None        


        for nwf in [1]:
            if (msg == EV_QUERY_CPE_INFO_RQST):
                ret,msg_rsp= CPE.on_rx_query_cpe_info(msg, obj)
                
            elif (msg == EV_QUERY_ALL_ONLINE_CPE_RQST or
                  msg == EV_QUERY_ONLINE_CPE_RQST):
                ret, msg_rsp = CPE.on_rx_query_cpe_online(msg, obj)

            elif (msg == EV_QUERY_IS_HANG_RQST):
                ret, msg_rsp = CPE.on_rx_query_is_hang(msg, obj)

            elif (msg == EV_QUERY_VERSION_IS_OK_RQST):
                ret, msg_rsp = CPE.on_rx_query_version_is_ok(msg, obj)

            elif (msg == EV_QUERY_CPE_LAST_FAULTS_RQST):
                ret, msg_rsp = CPE.on_rx_query_cpe_last_faults(msg, obj)

            elif (msg == EV_QUERY_LAST_SESSION_SOAP_RQST):
                ret, msg_rsp = CPE.on_rx_query_last_session_soap(msg, obj)                                

            elif (msg == EV_QUERY_CPE_INTERFACE_VERSION_RQST):
                ret, msg_rsp = CPE.on_rx_query_cpe_interface_version(msg, obj)
                
            else :
                ret = ERR_FAIL

                desc = "msg(%s) is not recognize" %msg
                log.app_err(desc)
                
                break

            if (ret == ERR_FATAL):
                # msg is not recognize
                break
                
            ret = CPE.on_tx_user_response(request, msg_rsp, obj)
        
        return ret


    @staticmethod    
    def process_config(request, msg, obj):    
        """
        request = user request 
        """  
        ret             = None
        cpe             = None     
        obj_database    = obj   # default        
                            
        for nwf in [1]:
            if (msg == EV_CONFIGURE_USER_INFO_RQST):
                ret,msg_rsp= CPE.on_rx_user_config_info(msg, obj)
                
            elif msg == EV_MODIFY_CPE_INFO_RQST:
                ret, msg_rsp = CPE.on_rx_user_modify_info(msg, obj)

            elif (msg == EV_TR069_ACS_EXIT_RQST):                
                ret, msg_rsp = CPE.on_rx_tr069_acs_exit(msg, obj)      
                
            else:

                ret, msg_rsp, obj_database = InformMonitor.process_config(msg, obj)                           

            if (ret == ERR_FATAL):
                # msg is not recognize
                break
                
            ret = CPE.on_tx_user_response(request, msg_rsp, obj_database)
        
        return ret

        
    def process_inform_eventcodes(self, request):    
        """
        """          
        from eventcode import EventCode
        
        ret = ERR_SUCCESS
      
        soap_inform = self.cpe_soap.get_soap_inform()

        # log
        eventcodes = CPE.get_inform_eventcodes(soap_inform)             

        desc = "cpe(sn=%s), eventcodes=%s" %(self.get_sn(), str(eventcodes))
        log.app_info(desc)
        
        obj = EventCode()
        ret = obj.process_inform_events(soap_inform.result.Event, self)   
        
        return ret         
                

    @staticmethod    
    def process_worklist4user(request, msg, obj):    
        """
        request = user request
        build + bind + get + report == query(sync, block, but quickly)
        exec_rqst is async
        """  
        ret = None
        cpe = None       
        msg_rsp = msg +2 # default
        obj_database = obj 

        for nwf in [1]:
        
            ret, msg_rsp, obj_database = CpeUserWorklist.process_worklist4user(msg, obj)                                               
            if (ret == ERR_FATAL):
                desc = "msg(%s) is not recognize" %msg
                log.app_err(desc)
                
                break

            ret = CPE.on_tx_user_response(request, msg_rsp, obj_database)
        
        return ret


    @staticmethod    
    def is_2session1cpe(sn, sessionno):    
        """          
        1 cpe 2 request?
        """  
        ret = False
        cpe = None  
        sessionno_old = None

        for nwf in [1]:
        
            cpe = CPE.get_cpe(sn)
            if (not cpe):
                break

            sessionno_old = cpe.cpe_soap.get_soap_sessionno()
            # new ?
            if (not sessionno_old):
                break
                
            if (sessionno_old != sessionno):
                desc = "cpe(sn=%s) 2 session(%s; %s)." %(sn, sessionno_old, sessionno)
                log.app_err(desc)
            
                ret = True
                break        

        return ret


    @staticmethod    
    def process_2session1cpe(request, sn):    
        """              
        """  
        ret = ERR_FAIL
        cpe = None  

        cpe = CPE.get_cpe(sn)
        cpe.on_rx_2_inform(request, CWMP_INFORM)
        
        return None


    @staticmethod    
    def process_user_message_seq_exist(request, msg):    
        """              
        """  

        CPE.user_request_write(request, msg)
                
        return None 

    
    # -------------------------------------------  
    def on_rx_inform(self, request, soap_message):
        """
        request = http.Request
        """
        ret = None

        soap_inform = self.cpe_soap.get_soap_inform()
        # mysql
        inform_soap_id = self.cpe_db_index.get_soap_inform_id()
        insert_monitor_result(inform_soap_id, soap_inform, self.get_sn())

        # nwf 20130605 ;(inform6 can kill 60s_timer or 180s_timer)
        if (self.is_inform_6()):
            try:
                self.cpe_user.get_user_timer_60s().cancel()
            except Exception,e:
                pass

            try:
                self.cpe_user.get_user_timer_180s().cancel()
            except Exception,e:
                pass       
                
        else:
            # any inform can kill 180s_timer; if second chance fail then tell user
            try:
                self.cpe_user.get_user_timer_180s().cancel()   

                on_user_timeout_180s_cancel_tell_user(self)
            except Exception,e:
                pass                                          
        
        for nwf in [1]:
            try:                
                log.app_info("----------(cpe(sn=%s) status=%s; soap message=%s)----------" 
                            %(self.get_sn(), self.get_status_desc(), soap_message))
                ret = self.on_tx_inform_response(request, soap_message)
                if (ret != ERR_SUCCESS):
                    break

                # inform auth ok?  2012-11-26
                ret = self.is_auth(request, self.get_sn())
                if (ret != ERR_SUCCESS):
                    break                 

                self.process_inform_eventcodes(request)                  
                
                # change state + timer trace
                self.set_status(CPE_ST_WAIT_POST_NULL)
                timer = reactor.callLater(TIMER_WAIT_POST_NULL, 
                                            on_cpe_timeout, self, request, "TIMER_WAIT_POST_NULL")
                self.cpe_property.set_cpe_timer(timer)
                
            except Exception,e:
                print_trace(e) 
                ret = ERR_FAIL
                break   
                
            ret = ERR_SUCCESS
            
        return ret   


    def on_rx_2_inform(self, request, soap_message):
        """
        request = http.Request
        nwf 2013-06-20;  still need time wait rpc response
        """
        ret = None                                 
        
        for nwf in [1]:
            try:                
                log.app_info("----------(cpe(sn=%s) status=%s; soap message=%s)----------" 
                            %(self.get_sn(), self.get_status_desc(), soap_message))

                # nwf 2013-07-01; before 204? or after 204?
                status = self.get_status()
                if ((status == CPE_ST_WAIT_POST_NULL) or 
                    (status == CPE_ST_WAIT_RPC_RESPONSE)):
                    # before 204, tx 500
                    ret = self.on_tx_500_2cpe(request, soap_message)
                    if (ret != ERR_SUCCESS):
                        break
                else:
                    # after 204, close old session
                    self.close_session()
                
            except Exception,e:
                print_trace(e) 
                ret = ERR_FAIL
                break   
            ret = ERR_SUCCESS
            
        return ret   
        

    def on_tx_500_2cpe(self, request, soap_message):
        """
        """
        ret     = None
        desc    = ""
        ret_api = None
        sn      = self.get_sn()

        for nwf in [1]:
            try:
                
                # add head
                CPE.request_write(request, "", "500", sn, http.INTERNAL_SERVER_ERROR)           
                
            except Exception,e:
                print_trace(e) 
                ret = ERR_FAIL
                break
            ret = ERR_SUCCESS
            
        return ret       

        
    def on_tx_inform_response(self, request, soap_message):
        """
        construct inform response 
        """
        ret         = None
        desc        = ""
        ret_api     = None
        sn          = self.get_sn()

        for nwf in [1]:
            try:
                log.app_info("----------(cpe(sn=%s) status=%s; soap message=%s)----------" 
                            %(sn, self.get_status_desc(), soap_message))
                
                obj_construct = construct.Construct()            
                soap_message = soap_message + "Response"
                obj_inform_response = InformResponse()
                
                ret_api, desc = obj_construct.create_soap_envelope(soap_message, 
                                                                    self.cpe_soap.get_cwmpversion(), 
                                                                    obj_inform_response, 
                                                                    self.cpe_soap.get_cwmpid())
                if (construct.CONSTRUCT_SUC != ret_api):
                    log.app_err(desc)
                    ret = ERR_FAIL
                    break
                
                # add head
                CPE.request_write(request, obj_construct.str_xml, soap_message, sn)                
                
            except Exception,e:
                print_trace(e) 
                ret = ERR_FAIL
                break
            ret = ERR_SUCCESS
            
        return ret       

    
    def on_rx_post_null_rpc(self, request):
        """
        request = http.Request
        """
        ret = None
        desc = ""

        for nwf in [1]:
            try:
                ret, desc = self.on_tx_rpc(request)  
                if (ret != ERR_SUCCESS):                   
                    self.on_tx_rpc_fail(desc) # skip err
                    break
                
                # cancel pre status timer + status change
                try:
                    self.cpe_property.get_cpe_timer().cancel()
                except Exception,e:
                    pass
                
                self.set_status(CPE_ST_WAIT_RPC_RESPONSE)
                timer = reactor.callLater(TIMER_WAIT_RPC_RESPONSE, 
                                            on_cpe_timeout, self, request, "TIMER_WAIT_RPC_RESPONSE")        
                self.cpe_property.set_cpe_timer(timer)                
            except Exception,e:
                print_trace(e)   
                ret = ERR_FAIL
                break
            ret = ERR_SUCCESS
            
        return ret

            
    def on_rx_post_null_norpc(self, request):
        """
        request = http.Request
        """
        ret = None
        
        try:
        
            # cancel pre status timer 
            try:
                self.cpe_property.get_cpe_timer().cancel()
            except Exception,e:
                pass
        
            ret = self.on_tx_nocontent(request)  
            
            self.set_status(CPE_ST_READY)
       
        except Exception,e:
            print_trace(e)            
            ret = ERR_FAIL
    
        return ret

    
    def on_rx_post_null(self, request, soap_message):
        """
        request = http.Request
        """
        ret = ERR_SUCCESS
        
        try:
            log.app_info("----------(cpe(sn=%s) status=%s; soap message=%s)----------" 
                        %(self.get_sn(), self.get_status_desc(), soap_message))
            
            if (self.cpe_user.get_user_rpc() is None):
                ret = self.on_rx_post_null_norpc(request)
            else:
                if (self.is_inform_6()):
                    ret = self.on_rx_post_null_rpc(request)
                else:
                    # nwf 2013-05-14; rpc1 get_url success, but next inform is "8" not "6"
                    ret = self.on_rx_post_null_norpc(request)
                
        except Exception,e:
            print_trace(e) 
            ret = ERR_FAIL            
        
        return ret    

        
    # ----------------------------------------------------rpcs    
    def on_tx_rpc(self, request):
        """
        """
        ret         = None
        desc        = ""        
        rpc_args    = None
        ret_api     = None
        sn          = self.get_sn()

        user_rpc = self.cpe_user.get_user_rpc()
        rpc_name = user_rpc.rpc_name

        for nwf in [1]:
            try:
                desc = "cpe(sn=%s), %s" %(sn, rpc_name)
                log.app_info(desc)
                            
                obj_construct = construct.Construct()       
                # 
                ret, rpc_args = self.convert_args(self.cpe_user.get_user_event(), user_rpc.rpc_args)
                
                ret_api, desc = obj_construct.create_soap_envelope(rpc_name, 
                                                                    self.cpe_soap.get_cwmpversion(), 
                                                                    rpc_args, 
                                                                    self.cpe_soap.get_cwmpid())
                if (construct.CONSTRUCT_SUC != ret_api):
                    ret = ERR_FAIL
                    break
                   
                CPE.request_write(request, obj_construct.str_xml, rpc_name, sn) 

                # mysql; 
                update_acs_rpc_tx(sn)  
                
            except Exception,e:
                print_trace(e) 
                ret = ERR_FAIL
                desc = e
                break
            ret = ERR_SUCCESS
            
        return (ret, desc)


    def on_tx_rpc_fail(self, desc):
        """
        tx user rpc fail, tell user exception, switch status to init
        """
        ret = None

        try:
            ret = self.on_tx_user_rpc_fail(desc)

            try:
                self.cpe_property.get_cpe_timer().cancel()
            except Exception,e:
                pass        

            self.set_status(CPE_ST_INIT)
        except Exception,e:
            print_trace(e) 
            ret = ERR_FAIL

        return ret

    
    def on_rx_rpc_response(self, request, soap_message):
        """
        """
        ret = None
        
        try:
            log.app_info("----------(cpe(sn=%s) status=%s; soap message=%s)----------" 
                        %(self.get_sn(), self.get_status_desc(), soap_message))

            try:
                self.cpe_property.get_cpe_timer().cancel()
            except Exception,e:
                pass

            ret = self.on_tx_nocontent(request)
            
            # (+1=response)
            ret = self.on_tx_user_rpc_response(self.cpe_user.get_user_event()+1)       

            self.set_status(CPE_ST_READY)
            self.cpe_user.set_user_event(None)
            
        except Exception,e:
            print_trace(e) 
            ret = ERR_FAIL            
            
        return ret

    
    def on_rx_rpc_fault(self, request, soap_message):
        """
        cpe's rpc response is fault
        """
        ret = None
        
        try:
            log.app_info("----------(cpe(sn=%s) status=%s; soap message=%s)----------" 
                        %(self.get_sn(), self.get_status_desc(), soap_message))

            # save
            soap_verify = self.cpe_soap.get_soap_verify()
            self.cpe_soap.set_last_faults(soap_verify)

            try:
                self.cpe_property.get_cpe_timer().cancel()
            except Exception,e:
                pass

            ret = self.on_tx_nocontent(request)
            
            #  (+2=fail)
            ret = self.on_tx_user_rpc_response(self.cpe_user.get_user_event()+2)
        
            self.set_status(CPE_ST_READY)
            
        except Exception,e:
            print_trace(e) 
            ret = ERR_FAIL            
            
        return ret    
        
            
    def on_tx_nocontent(self, request):
        """
        """
        ret     = None
        sn      = self.get_sn()

        for nwf in [1]:
            try:
                log.app_info("cpe (sn=%s, status=%s)" 
                            %(sn, self.get_status_desc()))
                
                request.setResponseCode(204, "No Content")  
                CPE.request_write(request, "", "204", sn)

                # nwf 2013-06-28
                timer = reactor.callLater(webservercfg.WAIT_CPE_SESSION_LOST_TIMEOUT, 
                            on_cpe_timeout, self, request, "WAIT_CPE_SESSION_LOST_TIMEOUT")        
                self.cpe_property.set_cpe_timer(timer) 

                
            except Exception,e:
                print_trace(e) 
                ret = ERR_FAIL  
                break
            ret = ERR_SUCCESS
       
        return ret     
        

    @staticmethod        
    def on_rx_query_cpe_info(msg, obj):    
        """
        obj = MsgQueryCPEInfo
        """
        ret = ERR_FAIL  # default
        cpe = None        
        msg_rsp = msg + 2 # default
        

        for nwf in [1]:
            # check args
            if (not isinstance(obj, MsgQueryCPEInfo)):
                log.app_err("obj is not MsgQueryCPEInfo")  
                ret = ERR_FATAL
                break

            sn = obj.sn
            cpe = CPE.get_cpe(sn)            
            if (cpe is None):
                cpe = CPE.add(sn, None)
                
                desc = "cpe sn(%s) not online, user create." %(sn)
                log.app_info(desc) 
                
            soap_verify = cpe.cpe_soap.get_soap_inform()
            if (soap_verify):                        
                obj.connection_request_url = soap_verify.result.DeviceId.ConnectionRequestURL
                obj.software_version = soap_verify.result.DeviceId.Softwareversion
                obj.hardware_version = soap_verify.result.DeviceId.Hardwareversion
            else:
                obj.connection_request_url  = ""
                obj.software_version        = ""
                obj.hardware_version        = ""             
            
            obj.cpe2acs_url             = cpe.get_cpe2acs_url()            
            obj.cwmp_version            = cpe.cpe_soap.get_cwmpversion()
            obj.cpe2acs_loginname       = cpe.cpe_property.get_cpe2acs_loginname()
            obj.cpe2acs_loginpassword   = cpe.cpe_property.get_cpe2acs_loginpassword()
            obj.acs2cpe_loginname       = cpe.cpe_property.get_acs2cpe_loginname()
            obj.acs2cpe_loginpassword   = cpe.cpe_property.get_acs2cpe_loginpassword()

            obj.auth_type               = cpe.cpe_property.get_cpe_authtype()
            obj.worklist_domain         = cpe.cpe_property.get_cpe_domain()
            obj.worklist_rollback       = cpe.cpe_property.get_cpe_worklist_rollback()
            obj.cpe_operator            = cpe.cpe_property.get_cpe_operator()
            obj.soap_inform_timeout     = cpe.cpe_soap.get_soap_inform_timeout()

            obj.interface_version       = cpe.cpe_property.get_cpe_interface_version()
            
            # added by lana-20121225
            if hasattr(soap_verify, "result"):
                obj.soap_inform = soap_verify.result
        
            ret = ERR_SUCCESS
            msg_rsp = msg + 1
                       
        return ret,msg_rsp

    
    @staticmethod 
    def on_rx_query_cpe_online(msg, obj):
        """
        obj = MsgQueryCPEOnline
        """
        ret = ERR_FAIL  # default
        cpe = None        
        msg_rsp = msg + 2 # default
        obj.online_status = {}
        
        for i in [1]:
            if (not isinstance(obj, MsgQueryCPEOnline)):
                log.app_err("obj is not MsgQueryCPEOnline")  
                ret = ERR_FATAL
                break
            
            if obj.sn:
                # only query current cpe's online status
                cpe = CPE.get_cpe(obj.sn)            
                if (cpe is None):
                    obj.online_status[obj.sn] = 0
                else:
                    soap_inform = cpe.cpe_soap.get_soap_inform()
                    if soap_inform:
                        key = obj.sn    # 以前已sn做标识，现在已oui_sn做标识 zsj 2013/8/26
                        obj.online_status[key] = 1
                    else:
                        obj.online_status[obj.sn] = 0
            else:
                # query all cpe's online status
                for sn in CPE.m_dict_sn2cpe.keys():
                    cpe = CPE.get_cpe(sn)
                    soap_inform = cpe.cpe_soap.get_soap_inform()
                    if soap_inform:
                        key = sn       # 以前已sn做标识，现在已oui_sn做标识
                        obj.online_status[key] = 1
            
            ret = ERR_SUCCESS
            msg_rsp = msg + 1
                       
        return ret,msg_rsp        
         

    @staticmethod        
    def on_rx_query_is_hang(msg, obj):    
        """
        obj = MsgQueryIsHang
        """
        ret = ERR_FAIL  # default       
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


    @staticmethod        
    def on_rx_query_version_is_ok(msg, obj):    
        """
        """
        ret     = ERR_FAIL  # default
        ret_api = False       
        msg_rsp = msg + 2 # default
        

        for nwf in [1]:

            # check args
            if (not isinstance(obj, MsgQueryVersionIsOk)):
                log.app_err("obj is not MsgQueryVersionIsOk")  
                ret = ERR_FATAL
                break            
            
            version_download = obj.version
            # for test
            if (version_download == ""):
                version_download = "v2.3.0"            
            
            ret_api = is_beta_version(version_download)
            if (ret_api):
            
                # if in list, ok
                version_locals = webservercfg.SUPPORT_CLIENT_VERSIONS_BETA
                if (version_download in version_locals):
                    msg_rsp = msg + 1
                    
                else:
                
                    # download is bigger > local_max
                    local_max = find_beta_ver_name_by_max_svn(version_locals)
                    if (not local_max):
                        break
                        
                    ret_api = beta_server_version_less_than_lib(local_max, version_download)
                    if (ret_api):
                        msg_rsp = msg + 1
            else:
            
                version_locals = webservercfg.SUPPORT_CLIENT_VERSIONS_STABLE
                if (version_download in version_locals):
                    msg_rsp = msg + 1   
                    
                else:

                    local_max = find_stable_ver_name_max(version_locals)
                    if (not local_max):
                        break

                    ret_api = stable_server_version_less_than_lib(local_max, version_download)
                    if (ret_api):
                        msg_rsp = msg + 1                        
      
            ret = ERR_SUCCESS   
            if (msg_rsp == msg + 2):
                desc = "TR069Server support lib versions = %s, client lib version=%s" %(version_locals, version_download)
                obj.dict_ret["str_result"] = desc
                       
        return ret,msg_rsp


    @staticmethod        
    def on_rx_query_cpe_last_faults(msg, obj):    
        """
        """
        ret = ERR_FAIL  # default
        cpe = None        
        msg_rsp = msg + 2 # default        

        for nwf in [1]:
            # check args
            if (not isinstance(obj, MsgQueryCpeLastFaults)):
                log.app_err("obj is not MsgQueryCpeLastFaults")  
                ret = ERR_FATAL
                break            

            cpe = CPE.get_cpe(obj.sn) 
            if (not cpe):  
                obj.dict_ret["str_result"] = "cpe is not online."  
            else:                
                obj.dict_ret["str_result"] = str(cpe.cpe_soap.get_last_faults())
                msg_rsp = msg + 1
        
            ret = ERR_SUCCESS            
                       
        return ret,msg_rsp


    @staticmethod        
    def on_rx_query_last_session_soap(msg, obj):    
        """
        """
        ret         = ERR_FAIL  # default
        ret_api     = False
        cpe         = None        
        msg_rsp     = msg + 2 # default        

        for nwf in [1]:
            # check args
            if (not isinstance(obj, MsgQueryLastSessionSoap)):
                log.app_err("obj is not MsgQueryCpeLastFaults")  
                ret = ERR_FATAL
                break            

            sn = obj.sn
            cpe = CPE.get_cpe(sn) 
            if (not cpe):  
                obj.dict_ret["str_result"] = "cpe(sn=%s) is not online."  %sn
            else:       
            
                ret_api, content = get_last_session_soap(sn)
                if (ret_api):                    
                    obj.dict_ret["str_result"] = content
                    msg_rsp = msg + 1
                else:
                    obj.dict_ret["str_result"] = content
        
            ret = ERR_SUCCESS            
                       
        return ret,msg_rsp


    @staticmethod        
    def on_rx_query_cpe_interface_version(msg, obj):    
        """
        """
        ret         = ERR_FAIL  # default
        ret_api     = False
        cpe         = None        
        msg_rsp     = msg + 2 # default        

        for nwf in [1]:
            # check args
            if (not isinstance(obj, MsgQueryCPEInterfaceVersion)):
                log.app_err("obj is not MsgQueryCPEInterfaceVersion")  
                ret = ERR_FATAL
                break            

            sn = obj.sn
            cpe = CPE.get_cpe(sn) 
            if (not cpe):  
                obj.dict_ret["str_result"] = "cpe(sn=%s) is not online."  %sn
            else:       

                # nwf 20140604; for backward compatibility
                operator = cpe.cpe_property.get_cpe_operator()
                interface_version = cpe.cpe_property.get_cpe_interface_version()
                if (not interface_version):
                    interface_version = CpeOperator.get_operator_interface_version_default(operator)                                        

                obj.dict_ret["str_result"] = interface_version

            msg_rsp = msg + 1
            ret = ERR_SUCCESS            
                       
        return ret,msg_rsp

    
    def on_tx_user_rpc_response(self, user_msg_response):    
        """
        user_msg_response
        """  
        ret = None
                       
        try:
            
            # fill user_rpc msg
            user_rpc = self.cpe_user.get_user_rpc()    
            if (user_rpc.rpc_name == "connection_request"):
                pass
            else:
                soap_verify = self.cpe_soap.get_soap_verify()
                ret, xml_result = self.convert_result(user_msg_response, soap_verify.result, user_rpc)
                user_rpc.dict_ret = xml_result            

            user_request = self.cpe_user.get_user_request()   
            user_request.need_new_http_client = True 
            
            CPE.on_tx_user_response(user_request, user_msg_response, user_rpc)
            self.cpe_user.set_user_rpc(None)            
        except Exception,e:
            print_trace(e) 
            ret = ERR_FAIL
    
        return ret

            
    def on_tx_user_rpc_fail(self, desc):    
        """
        timeout or exception
        """  
        ret = None 
                        
        for nwf in [1]:
            try:
                user_rpc = self.cpe_user.get_user_rpc()
                if(user_rpc is None):
                    # skip
                    break

                log.app_info("-_-\n%s" %desc)

                # fill user_rpc
                user_rpc.dict_ret = {}
                user_rpc.dict_ret["str_result"] = desc  # ref event
                # + fault code
                dict_data = {}
                dict_data["FaultCode"]=8002  # acs's error
                dict_data["FaultString"]= desc        
                user_rpc.dict_ret["dict_data"] = dict_data
                
                user_msg_response = int(self.cpe_user.get_user_event()) + 2  # fail    
                
                user_request = self.cpe_user.get_user_request()  
                user_request.need_new_http_client = True               
                
                CPE.on_tx_user_response(user_request, user_msg_response, user_rpc);                      
                self.cpe_user.set_user_rpc(None)
                
            except Exception,e:
                print_trace(e)     
                ret = ERR_FAIL
                break
            
            ret = ERR_SUCCESS
            
        return ret            


    @staticmethod        
    def on_rx_user_config_info(msg, obj):    
        """
        obj = MsgConfig
        """
        ret = ERR_FAIL  # default
        cpe = None        
        msg_rsp = msg + 2 # default
        
        for nwf in [1]:

            if (not isinstance(obj, MsgConfig)):
                log.app_err("obj is not MsgConfig")  
                ret = ERR_FATAL
                break

            # nwf 2013-05-06 ; no matter what cpe is online 
            sn = obj.sn
            cpe = CPE.get_cpe(sn)            
            if (cpe is None):
                cpe = CPE.add(sn, None)
                
                desc = "cpe sn(%s) not online, user create." %(sn)
                log.app_info(desc)  
                
            # ok config(be careful, None is not need config)
            if (obj.acs2cpe_loginname is not None):
                cpe.cpe_property.set_acs2cpe_loginname(obj.acs2cpe_loginname)
            if (obj.acs2cpe_loginpassword is not None):
                cpe.cpe_property.set_acs2cpe_loginpassword(obj.acs2cpe_loginpassword) 
            if (obj.cpe2acs_loginname is not None):
                cpe.cpe_property.set_cpe2acs_loginname(obj.cpe2acs_loginname)
            if (obj.cpe2acs_loginpassword is not None):
                cpe.cpe_property.set_cpe2acs_loginpassword(obj.cpe2acs_loginpassword)
                
            if (obj.auth_type is not None):
                cpe.cpe_property.set_cpe_authtype(obj.auth_type)
            if (obj.worklist_domain is not None):
                cpe.cpe_property.set_cpe_domain(obj.worklist_domain)
            if (obj.worklist_rollback is not None):
                cpe.cpe_property.set_cpe_worklist_rollback(obj.worklist_rollback)    
            if (obj.cpe_operator is not None):
                cpe.cpe_property.set_cpe_operator(obj.cpe_operator)                 

            if (obj.cwmp_version is not None):
                cpe.cpe_soap.set_cwmpversion(obj.cwmp_version)
            if (obj.soap_inform_timeout is not None):
                cpe.cpe_soap.set_soap_inform_timeout(obj.soap_inform_timeout)            
            
            ret = ERR_SUCCESS
            msg_rsp = msg + 1
                       
        return ret,msg_rsp
    
    
    @staticmethod        
    def on_rx_user_modify_info(msg, obj):    
        """
        obj = MsgModifyCPEInfo
        """
        ret = ERR_FAIL  # default
        cpe = None        
        msg_rsp = msg + 2 # default
        
        #    
        for i in [1]:
            if (not isinstance(obj, MsgModifyCPEInfo)):
                log.app_err("obj is not MsgModifyCPEInfo")  
                ret = ERR_FATAL
                break

            sn = obj.sn
            cpe = CPE.get_cpe(sn)            
            if (cpe is None):
                cpe = CPE.add(sn, None)
                
                desc = "cpe sn(%s) not online, user create." %(sn)
                log.app_info(desc)
                
            dict_col = {}
            dict_data = {}
                
            # modify all itmes in obj.dict_modify_items
            # None is default(not modify, "" or False is valid ); nwf 2013-06-17
            value = obj.dict_modify_items.get("cpe_auth_acs_username")
            if (value is not None):
                #cpe.cpe_property.set_acs2cpe_loginname(value)
                if cpe.cpe_property.is_update_acs2cpe_name(value):
                    dict_col['ACS2CPE_NAME'] = value
                
            value = obj.dict_modify_items.get("cpe_auth_acs_password")
            if (value is not None):
                #cpe.cpe_property.set_acs2cpe_loginpassword(value)
                if cpe.cpe_property.is_update_acs2cpe_password(value):
                    dict_col['ACS2CPE_PASSWORD'] = value

            value = obj.dict_modify_items.get("acs_auth_cpe_username")    
            if (value is not None):
                #cpe.cpe_property.set_cpe2acs_loginname(value)
                if cpe.cpe_property.is_update_cpe2acs_name(value):
                    dict_col['CPE2ACS_NAME'] = value

            value = obj.dict_modify_items.get("acs_auth_cpe_password")
            if (value is not None):
                #cpe.cpe_property.set_cpe2acs_loginpassword(value)
                if cpe.cpe_property.is_update_cpe2acs_password(value):
                    dict_col['CPE2ACS_PASSWORD'] = value

            value = obj.dict_modify_items.get("cpe_authtype")    
            if (value is not None):
                #cpe.cpe_property.set_cpe_authtype(value)
                if cpe.cpe_property.is_update_auth_type(value):
                    dict_col['AUTH_TYPE'] = value

            value = obj.dict_modify_items.get("worklist_domain")    
            if (value is not None):
                #cpe.cpe_property.set_cpe_domain(value)
                if cpe.cpe_property.is_update_domain(value):
                    dict_col['CPE_DEVICE_TYPE'] = value

            value = obj.dict_modify_items.get("worklist_rollback")    
            if (value is not None):
                #cpe.cpe_property.set_cpe_worklist_rollback(value)
                if cpe.cpe_property.is_update_worklist_rollback(value):
                    dict_col['CPE_WORKLIST_ROLLBACK'] = value

            value = obj.dict_modify_items.get("cpe_operator")    
            if (value is not None):
                #cpe.cpe_property.set_cpe_operator(value)
                list1 = CpeOperator.get_operators_name()
                if (value not in list1):
                    desc = "cpe sn(%s) operator=%s not in %s" %(sn, value, list1)
                    log.app_info(desc)
                    desc = u"cpe sn(%s) operator=%s 不在支持的集合中(%s)" %(sn, value, list1)
                    obj.dict_ret["str_result"] = desc                    
                    break
                else:
                    if cpe.cpe_property.is_update_operator(value):
                        dict_col['CPE_OPERATOR'] = value
                # auto interface_version
                interface_version = cpe.cpe_property.get_cpe_interface_version()
                operator = value
                versions = CpeOperator.get_operator_versions(operator)
                is_support = (interface_version in versions)
                if (not is_support):
                    interface_ver = CpeOperator.get_operator_interface_version_default(operator)
                    #cpe.cpe_property.set_cpe_interface_version(value)
                    if cpe.cpe_property.is_update_interface_version(interface_ver):
                        dict_col['INTERFACE_VERSION'] = interface_ver
                    
            value = obj.dict_modify_items.get("interface_version")    
            if (value is not None):                 
                operator = cpe.cpe_property.get_cpe_operator()                
                if (value.upper() == "AUTO"):
                    value = CpeOperator.get_operator_interface_version_default(operator)                    
                    if (not value):
                        desc = u"cpe sn(%s) operator=%s, interface_version=AUTO 配置失败，请先配置operator." %(
                                sn, operator)
                        obj.dict_ret["str_result"] = desc
                        break                     
                else:
                    versions = CpeOperator.get_operator_versions(operator)
                    is_support = (value in versions)
                    if (not is_support):
                        desc = u"cpe sn(%s) operator=%s, interface_version=%s 不在支持的集合中(%s)." %(
                                sn, operator, value, versions)
                        obj.dict_ret["str_result"] = desc
                        break                    
                #cpe.cpe_property.set_cpe_interface_version(value)
                if cpe.cpe_property.is_update_interface_version(value):
                    dict_col['INTERFACE_VERSION'] = value

            value = obj.dict_modify_items.get("cwmp_version")                               
            if (value is not None):
                #cpe.cpe_soap.set_cwmpversion(value)
                if cpe.cpe_soap.is_update_cwmp_version(value):
                    dict_col['CWMP_VERSION'] = value

            value = obj.dict_modify_items.get("soap_inform_timeout")    
            if (value is not None):
                #cpe.cpe_soap.set_soap_inform_timeout(value)
                if cpe.cpe_soap.is_update_inform_timeout(value):
                    dict_col['SOAP_INFORM_TIMEOUT'] = value
                
                
            if dict_col:
                # 字典的值不为空时，才更新数据库
                dict_data['columns'] = dict_col
                dict_data['condition'] = 'CPE_ID=%s' % cpe.get_cpe_id()
                operate_db('CPE', 'UPDATE', dict_data)
            
            ret = ERR_SUCCESS
            msg_rsp = msg + 1
                       
        return ret,msg_rsp


    @staticmethod
    def on_tx_user_response_short_connection(request, msg_permit, obj):    
        """
        request user request
        msg_permit is success?
        obj = MsgUserRpcCheck
        """  
        ret = ERR_SUCCESS  # default
        msg = EV_RPC_CHECK_FAIL

        if (msg_permit == ERR_SUCCESS):
            msg = EV_RPC_CHECK_RSP

        ret = CPE.on_tx_user_response(request, msg, obj)
        
        return ret

  
    @staticmethod
    def on_tx_user_response(request, msg, obj):    
        """
        request =user request; else,  need http client send to agent
        
        """  
        ret             = ERR_SUCCESS  # default
        str_dict_msg    = ""
        seq             = None
        
        ip = request.transport.client[0]
        port = request.transport.client[1]
        
        desc = "message=%s(user ip=%s, port=%s)" %(get_event_desc(msg), ip, port)
        log.app_info(desc)  
        
        # mysql
        if (isinstance(obj, MsgUserRpc)):
            update_acs_rpc_response(request, msg, obj)

        try:
            strio = StringIO()
            #pickle.dump(obj, strio)
            pickle.dump(obj, strio, -1) # changed by lana, fix pickel err: a class defines __slots without defining __getstat__ can not be pickel

            try:
                d1  = CpeUser.get_user_dictmsg(request)
                seq = d1.get(KEY_SEQUENCE)
            except Exception,e:
                print_trace(e) 
                d1  = {}
                
            d1[KEY_MESSAGE]     = msg
            d1[KEY_OBJECT]      = strio.getvalue()
            d1[KEY_SENDER]      = KEY_SENDER_ACS              
                                   
            if (request):

                try:
                    need_new_http_client = request.need_new_http_client
                    d1[KEY_SEQUENCE] = get_id("Seq")
                except Exception,e:
                    need_new_http_client = False

                str_dict_msg        = str(d1) 

                # need http client send to agent
                if (need_new_http_client):   
                
                    CPE.new_http_client_send2agent_async(str_dict_msg)
                else:
                
                    CPE.user_request_write(request, str_dict_msg)  
                    
                    UsersMsgSeq.save_user_rsp_msg(seq, str_dict_msg) 
                    
        except Exception,e:
            print_trace(e) 
            ret = ERR_FAIL
        
        return ret         

      
    @staticmethod 
    def on_rx_tr069_acs_exit(msg, obj):
        """
        """
        
        ret = ERR_SUCCESS  # default       
        msg_rsp = msg + 1  

        # clear
        AcsCpeThread.on_exit_tr069_acs()
        
        reactor.stop()
                       
        return ret,msg_rsp

    
    @staticmethod    
    def on_connection_lost(transport):
        """
        reset cpe's property
        """                
        
        try:

            sessionno = transport.sessionno
            ip = transport.client[0]
            port = transport.client[1]

            cpe = CPE.get_cpe_bysessionno(sessionno)
            # user session  --------------------------------------------------
            if (not cpe):

                if (CPE.m_dict_double_sessionno.get(sessionno, None)):
                    CPE.pop_double_sessionno(sessionno)
                    desc = "warning: cpe(ip=%s, port=%s) double session connection lost(sessionno=%s)" %(ip, port, sessionno)
                else:
                    desc = "user(ip=%s, port=%s) connection lost(sessionno=%s)" %(ip, port, sessionno)

                log.app_info(desc)
                return


            # cpe session --------------------------------------------------
            sn = cpe.get_sn()
            log.app_info("cpe(sn=%s) connection lost(ip=%s, port=%s, sessionno=%s)"  
                            %(sn, ip, port, sessionno))

            # is user rpc?
            if (cpe.is_inform_6()):

                user_rpc = cpe.cpe_user.get_user_rpc()
                if(user_rpc):                    
                    # cpe unsurpport  this rpc, cpe close tcp session
                    desc = "cpe close (acs-cpe) session"
                    cpe.on_tx_user_rpc_fail(desc)

            # clear
            cpe.reset_cpe_session()

            # mysql            
            str_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cpe.cpe_soap.time_s2_finish = str_time
            update_acs_rpc_time(cpe, 'TIME_S2_FINISH', str_time)
            if cpe.curr_rpc_name == 'Inform':
                #update_acs_rpc_tx(cpe.get_sn())
                update_inform_rpc(cpe, str_time)
                cpe.curr_rpc_name = ''
            # Alter by lizn 2014-03-10

        except Exception,e:
            print_trace(e)         


    @staticmethod 
    def init():
        """
        """
                
        restore_acs_from_mysql()  

        update_acs_logic_worklists_status()
                               

    @staticmethod    
    def add(sn, soap_sessionno=None):
        """
        inform come, refresh cpe's property
        sn not exist, create cpe; sn exist, update cpe(sessionno)
        nwf 2013-04-16 update; cpe never delete
        """
        cpe = CPE.get_cpe(sn)
        if (cpe is None):
            cpe = CPE(sn)            
            d1 = {sn: cpe}   

            log.app_info("new cpe add(sn=%s)" %(sn))
            CPE.m_dict_sn2cpe.update(d1)

            # mysql
            cpe_id = insert_acs_cpe(sn)
            cpe.set_cpe_id(cpe_id)      # 保存CPE_ID

            # only once
            # cpe.set_default_username_password()
            cpe.cpe_property.acs2cpe_loginname = webservercfg.ACS2CPE_LOGIN_NAME
            cpe.cpe_property.acs2cpe_loginpassword = webservercfg.ACS2CPE_LOGIN_PASSWORD
            cpe.cpe_property.cpe2acs_loginname = webservercfg.CPE2ACS_LOGIN_NAME
            cpe.cpe_property.cpe2acs_loginpassword = webservercfg.CPE2ACS_LOGIN_PASSWORD
            # Alter by lizn 2014-04-14

        # update cpe property                                    
        cpe.cpe_property.set_onlinetime(datetime.now())  
        cpe.cpe_property.set_cpe_status("online")          
        
        d1 ={soap_sessionno: cpe}
        CPE.m_dict_sessionno2cpe.update(d1)  
        
        return cpe

    
    @staticmethod    
    def delete(sn):
        """
        strategy:timout>=12hour delete cpe obj
        """

        cpe = CPE.get_cpe(sn)
        if (cpe is None):
            log.app_info("cpe (sn=%s) not exist" %sn)
        else:            
            log.app_info("cpe(sn=%s) delete ok." %(sn))
            CPE.m_dict_sn2cpe.pop(sn, None) 

            soap_sessionno = cpe.cpe_soap.get_soap_sessionno()         
            CPE.m_dict_sessionno2cpe.pop(soap_sessionno, None) 


    def close_session(self):
        """
        acs start close cpe session
        """

        try:
            request = self.cpe_property.get_cpe_request()
            if (request):
                request.transport.loseConnection()

                desc = "acs close (acs-cpe) session"
                log.app_err(desc)
        except Exception,e:                
            print_trace(e)         


    def convert_args(self, rpc_event, rpc_args):
        """
        convert user's args to xml's args
        success return (ERR_SUCEESS,xml_args) ,xml_args=result
        fail, return (ERR_FAIL,xml_args), xml_args = err desc
        """
        log.app_info("----Begin convert_args----")
        ret = ERR_SUCCESS
        xml_args = None
        
        try:

            if (rpc_event == EV_RPC_GETRPCMETHODS_RQST):
                xml_args = ""                
                            
            elif (rpc_event == EV_RPC_SETPARAMETERVALUES_RQST):
                tmp_object = SetParameterValues()
                if type(rpc_args) is dict:
                    tmp_list = rpc_args.get('ParameterList', "")
                    tmp_ParameterKey = rpc_args.get('ParameterKey', "")
                    tmp_ParameterList = []
                
                    for dict_x in tmp_list:
                        if type(dict_x) is dict:
                            tmp_Name = dict_x.get('Name', "")
                            tmp_Value = dict_x.get('Value', "")
                            struct_Parameter = ParameterValueStruct()
                            struct_Parameter.Name = tmp_Name
                            struct_Parameter.Value = tmp_Value

                            # nwf 2014-06-06; user can set node type
                            tmp_Type_user = dict_x.get('Type', "")                            
                            tmp_Type_sys = self.get_parameter_type(tmp_Name)

                            if (tmp_Type_user and tmp_Type_sys):
                                # user>system
                                struct_Parameter.Value_type = tmp_Type_user
                                
                                if (tmp_Type_user != tmp_Type_sys):
                                    desc = "Warning:node name=%s, value=%s, value type:user type(%s) != sys type(%s) " %(
                                                        tmp_Name, tmp_Value, 
                                                        tmp_Type_user, tmp_Type_sys)
                                    log.app_info(desc)
                                    
                            if (tmp_Type_user and not tmp_Type_sys):
                                struct_Parameter.Value_type = tmp_Type_user

                            if (not tmp_Type_user and tmp_Type_sys):                            
                                struct_Parameter.Value_type = tmp_Type_sys
                                
                            if (not tmp_Type_user and not tmp_Type_sys):                                       
                                struct_Parameter.Value_type = "string"
                                
                            tmp_ParameterList.append(struct_Parameter)
                        else:
                            log.app_info("SetParameterValues args error!!!")
                        
                    tmp_object.ParameterList = tmp_ParameterList
                    tmp_object.ParameterKey = tmp_ParameterKey
                    xml_args = tmp_object
                else:
                    xml_args = ""
                
            elif (rpc_event == EV_RPC_GETPARAMETERVALUES_RQST):
                tmp_object = GetParameterValues()
                if type(rpc_args) is dict:
                    tmp_ParameterNames = rpc_args.get('ParameterNames', [])
                    if type(tmp_ParameterNames) is not list:
                        if "," in tmp_ParameterNames:
                            tmp_ParameterNames = tmp_ParameterNames.split(",")
                        else:
                            list_tmp = []
                            list_tmp.append(tmp_ParameterNames)
                            tmp_ParameterNames = list_tmp
                    else:   # zsj modified 2013/2/21 rf不填写下下来的是空列表[]，如果是gui则是[""],保持和中兴平台一致
                        if not len(tmp_ParameterNames):
                            tmp_ParameterNames.append("")
                
                    tmp_object.ParameterNames = tmp_ParameterNames
                    xml_args = tmp_object
                else:
                    xml_args = ""
        
                
            elif (rpc_event == EV_RPC_GETPARAMETERNAMES_RQST):
                tmp_object = GetParameterNames()
                if type(rpc_args) is dict:
                    tmp_ParameterPath = rpc_args.get('ParameterPath', "")
                    tmp_NextLevel = rpc_args.get('NextLevel', "")
                  
                    tmp_object.ParameterPath = tmp_ParameterPath
                    tmp_object.NextLevel = tmp_NextLevel
                    xml_args = tmp_object
                else:
                    xml_args = ""
              
            elif (rpc_event == EV_RPC_SETPARAMETERATTRIBUTES_RQST):
                tmp_object = SetParameterAttributes()
                tmp_object.ParameterList = []
                
                if type(rpc_args) is dict:
                    tmp_variable = rpc_args.get('ParameterList', "")
                    
                    for dict_tmp in tmp_variable:
                        if type(dict_tmp) is dict:
                            struct_tmp_variable = SetParameterAttributesStruct()
                            struct_tmp_variable.Name = dict_tmp.get('Name', "")
                            struct_tmp_variable.NotificationChange = dict_tmp.get('NotificationChange', "")
                            struct_tmp_variable.Notification = dict_tmp.get('Notification', "")
                            struct_tmp_variable.AccessListChange = dict_tmp.get('AccessListChange', "")
                            struct_tmp_variable.AccessList = dict_tmp.get('AccessList', "")
                            tmp_object.ParameterList.append(struct_tmp_variable)
                        else:
                            log.app_info("SetParameterAttributes args error!!!")
                    xml_args = tmp_object
                else:
                    xml_args = ""
                
            elif (rpc_event == EV_RPC_GETPARAMETERATTRIBUTES_RQST):
                tmp_object = GetParameterAttributes()
                if type(rpc_args) is dict:
                    # zsj modified 2013/2/21 rf不填写下下来的是空列表[]，如果是gui则是[""],保持和中兴平台一致
                    tmp_ParameterNames = rpc_args.get('ParameterNames', [])
                    if type(tmp_ParameterNames) is not list:
                        if "," in tmp_ParameterNames:
                            tmp_ParameterNames = tmp_ParameterNames.split(",")
                        else:
                            list_tmp = []
                            list_tmp.append(tmp_ParameterNames)
                            tmp_ParameterNames = list_tmp
                    else:
                        if not len(tmp_ParameterNames):
                            tmp_ParameterNames.append("")
                
                    tmp_object.ParameterNames = tmp_ParameterNames
                    xml_args = tmp_object
                else:
                    xml_args = ""
    
                
            elif (rpc_event == EV_RPC_ADDOBJECT_RQST):
                tmp_object = AddObject()
                if type(rpc_args) is dict:
                    tmp_ObjectName = rpc_args.get('ObjectName', "")
                    tmp_ParameterKey = rpc_args.get('ParameterKey', "")
                    
                    tmp_object.ObjectName = tmp_ObjectName
                    tmp_object.ParameterKey = tmp_ParameterKey
                    xml_args = tmp_object
                else:
                    xml_args = ""
                        
                
            elif (rpc_event == EV_RPC_DELETEOBJECT_RQST):
                tmp_object = DeleteObject()
                if type(rpc_args) is dict:
                    tmp_ObjectName = rpc_args.get('ObjectName', "")
                    tmp_ParameterKey = rpc_args.get('ParameterKey', "")
         
                    tmp_object.ObjectName = tmp_ObjectName
                    tmp_object.ParameterKey = tmp_ParameterKey
                    xml_args = tmp_object
                else:
                    xml_args = ""
                
            elif (rpc_event == EV_RPC_REBOOT_RQST):
                tmp_object = Reboot()
                if type(rpc_args) is dict:
                    tmp_object.CommandKey = rpc_args.get('CommandKey', "")
                    xml_args = tmp_object
                else:
                    xml_args = ""
            
            elif (rpc_event == EV_RPC_DOWNLOAD_RQST):
                tmp_object = Download()
                if type(rpc_args) is dict:
                    tmp_object.CommandKey  = rpc_args.get('CommandKey', "")
                    tmp_object.FileType = rpc_args.get('FileType', "")
                    tmp_object.URL = rpc_args.get('URL', "")
                    tmp_object.Username = rpc_args.get('Username', "")
                    tmp_object.Password = rpc_args.get('Password', "")
                    tmp_object.FileSize = rpc_args.get('FileSize', "")
                    tmp_object.TargetFileName = rpc_args.get('TargetFileName', "")
                    tmp_object.DelaySeconds = rpc_args.get('DelaySeconds', "")
                    tmp_object.SuccessURL = rpc_args.get('SuccessURL', "")
                    tmp_object.FailureURL = rpc_args.get('FailureURL', "")
                    
                    xml_args = tmp_object
                else:
                    xml_args = ""
                       
            elif (rpc_event == EV_RPC_UPLOAD_RQST):
                tmp_object = Upload()
                if type(rpc_args) is dict:
                    tmp_object.CommandKey  = rpc_args.get('CommandKey', "")
                    tmp_object.FileType = rpc_args.get('FileType', "")
                    tmp_object.URL = rpc_args.get('URL', "")
                    tmp_object.Username = rpc_args.get('Username', "")
                    tmp_object.Password = rpc_args.get('Password', "")
                    tmp_object.DelaySeconds = rpc_args.get('DelaySeconds', "")
                    
                    xml_args = tmp_object
                else:
                    xml_args = ""
                
               
            elif (rpc_event == EV_RPC_FACTORYRESET_RQST):
                xml_args = ""
                
            elif (rpc_event == EV_RPC_SCHEDULEINFORM_RQST):
                tmp_object = ScheduleInform()
                if type(rpc_args) is dict:
                    tmp_object.CommandKey  = rpc_args.get('CommandKey', "")
                    tmp_object.DelaySeconds = rpc_args.get('DelaySeconds', "")
                    
                    xml_args = tmp_object
                else:
                    xml_args = ""
               
            elif (rpc_event == EV_RPC_GETQUEUEDTRANSFERS_RQST):
                xml_args = ""
                
            elif (rpc_event == EV_RPC_SETVOUCHERS_RQST):
                tmp_object = SetVouchers()
                if type(rpc_args) is dict:
                    tmp_Vouchers = rpc_args.get('VoucherList', "")
                    
                    tmp_object.VoucherList = tmp_Vouchers    # type: base64[]
                    xml_args = tmp_object
                else:
                    xml_args = ""
                
            elif (rpc_event == EV_RPC_GETOPTIONS_RQST):
                tmp_object = GetOptions()
                if type(rpc_args) is dict:
                    tmp_OptionName = rpc_args.get('OptionName', "")
                    
                    tmp_object.OptionName = tmp_OptionName
                    xml_args = tmp_object
                else:
                    xml_args = ""
                
            elif (rpc_event == EV_RPC_GETALLQUEUEDTRANSFERS_RQST):
                xml_args = ""
                
            elif (rpc_event == EV_RPC_SCHEDULEDOWNLOAD_RQST):
                tmp_object = ScheduleDownload()
                if type(rpc_args) is dict:
                    tmp_object.CommandKey  = rpc_args.get('CommandKey', "")
                    tmp_object.FileType = rpc_args.get('FileType', "")
                    tmp_object.URL = rpc_args.get('URL', "")
                    tmp_object.Username = rpc_args.get('Username', "")
                    tmp_object.Password = rpc_args.get('Password', "")
                    tmp_object.FileSize = rpc_args.get('FileSize', "")
                    tmp_object.TargetFileName = rpc_args.get('TargetFileName', "")
                    list_time = rpc_args.get('TimeWindowList', "")
                    tmp_object.TimeWindowList = []
                    for tmp_time in list_time:
                        if type(tmp_time) is dict:
                            tmp_time_object = TimeWindowStruct()
                            tmp_time_object.WindowStart = tmp_time.get('WindowStart', "")
                            tmp_time_object.WindowEnd = tmp_time.get('WindowEnd', "")
                            tmp_time_object.WindowMode = tmp_time.get('WindowMode', "")            
                            tmp_time_object.UserMessage = tmp_time.get('UserMessage', "")  
                            tmp_time_object.MaxRetries = tmp_time.get('MaxRetries', "")
                            
                            tmp_object.TimeWindowList.append(tmp_time_object)
                    
                    xml_args = tmp_object
                else:
                    xml_args = ""
            
            elif (rpc_event == EV_RPC_CANCELTRANSFER_RQST):
                tmp_object = CancelTransfer()
                if type(rpc_args) is dict:
                    tmp_object.CommandKey = rpc_args.get('CommandKey', "")
                    xml_args = tmp_object
                else:
                    xml_args = ""
                
            elif (rpc_event == EV_RPC_CHANGEDUSTATE_RQST):
                tmp_object = ChangeDUState()
                list_tmp_object = []
                if type(rpc_args) is dict:
                    tmp_OpreationsList = rpc_args.get('Operations', "")
                    if tmp_OpreationsList:
                        for dict_tmp in tmp_OpreationsList:
                            if type(dict_tmp) is dict:
                                name = dict_tmp.keys()[0]
                                dict_x = dict_tmp[name]
                                if  name=='InstallOpStruct':
                                    struct_install_object = InstallOpStruct()
                                    struct_install_object.URL = dict_x.get('URL', "")
                                    struct_install_object.UUID = dict_x.get('UUID', "")
                                    struct_install_object.Username = dict_x.get('Username', "")
                                    struct_install_object.Password = dict_x.get('Password', "")
                                    struct_install_object.ExecutionEnvRef = dict_x.get('ExecutionEnvRef',
                                                                                       "")
                                    list_tmp_object.append(struct_install_object)
                                    
                                elif name =='UpdateOpStruct':
                                    struct_update_object = UpdateOpStruct()
                                    struct_update_object.URL = dict_x.get('URL', None)
                                    struct_update_object.UUID = dict_x.get('UUID', None)
                                    struct_update_object.Username = dict_x.get('Username', None)
                                    struct_update_object.Password = dict_x.get('Password', None)
                                    struct_update_object.Version = dict_x.get('Version', None)
                                    
                                    list_tmp_object.append(struct_update_object)
                
                                elif name =='UninstallOpStruct':
                                    struct_uninstall_object = UninstallOpStruct()
                                    struct_uninstall_object.UUID = dict_x.get('UUID', None)
                                    struct_uninstall_object.Version = dict_x.get('Version', None)
                                    struct_uninstall_object.ExecutionEnvRef = dict_x.get('ExecutionEnvRef',
                                                                                       None)
                                    list_tmp_object.append(struct_uninstall_object)
                                    
                        tmp_object.Operations = list_tmp_object
                    tmp_CommandKey = rpc_args.get('CommandKey', "")
                    tmp_object.CommandKey = tmp_CommandKey
                    
                    xml_args = tmp_object
                else:
                    xml_args = ""
                    
            elif (rpc_event == EV_RPC_CONNECTION_REQUEST_RQST):
                xml_args = ""
                
            else:
                xml_args = "RPC_Event can't find!!!"
                log.app_info(xml_args)
                
                ret = ERR_FAIL
            if ret == ERR_FAIL:
                log.app_info("---Convert_args Error---")
            else:
                log.app_info("-----Convert_args Succeed----")
        except Exception,e:
            xml_args = "---Convert_args Error---\n%s"%e
            log.app_info(xml_args)
            ret = ERR_FAIL
            
        return ret, xml_args


    def convert_result(self, rpc_event, result, rpc_object):
        """
        convert cpe's methods to user's display
        """
        log.app_info("----Begin convert_result----")
        str_tmp = ""
        ret = ERR_SUCCESS
        dict_data = {}
        dict_ret= {}
        try:
            # result is Verify's property
            if (rpc_event == EV_RPC_GETRPCMETHODS_RSP):
                if result:
                    str_tmp = "\n*****%s Succeed!******\n-----The Result:\n"%rpc_object.rpc_name
                    for x in result.MethodList:
                        str_tmp =str_tmp + "%s\n" % x
                    dict_data["MethodsList"] = result.MethodList
                else:
                    str_tmp = "Decode response result faile!"
                    ret = ERR_FAIL
                
            elif (rpc_event == EV_RPC_SETPARAMETERVALUES_RSP):
                if result:
                    str_tmp = "\n*****%s Succeed!******\n-----The Result:\n"%rpc_object.rpc_name
                    str_tmp += "\nStatus = %s \n" % result.Status
                    dict_data["Status"] = result.Status
                else:
                    str_tmp = "Decode response result faile!"
                    ret = ERR_FAIL
                
            elif (rpc_event == EV_RPC_GETPARAMETERVALUES_RSP):
                if result:
                    list_tmp = []
                    str_tmp = "\n*****%s Succeed!******\n-----The Result:\n"%rpc_object.rpc_name
                    for x in result.ParameterList:
                        dict_tmp = {}
                        str_tmp += "Name = %s; Value = %s; Value_Type = %s\n" % (x.Name,
                                                                                 x.Value,
                                                                                 x.Value_type)
                        dict_tmp["Name"] = x.Name
                        dict_tmp["Value"] = x.Value
                        dict_tmp["Value_type"] = x.Value_type
                        list_tmp.append(dict_tmp)
                    dict_data["ParameterList"] = list_tmp
                else:
                    str_tmp = "Decode response result faile!"
                    ret = ERR_FAIL
                
            elif (rpc_event == EV_RPC_GETPARAMETERNAMES_RSP):
                if result:
                    list_tmp = []
                    str_tmp = "\n*****%s Succeed!******\n-----The Result:\n"%(rpc_object.rpc_name)
                    for x in result.ParameterList:
                        dict_tmp = {}
                        str_tmp += "Name = %s; Writable = %s\n" % (x.Name,
                                                                   x.Writable)
                        dict_tmp["Name"] = x.Name
                        dict_tmp["Writable"] = x.Writable
                        list_tmp.append(dict_tmp)
                    dict_data["ParameterList"] = list_tmp
                else:
                    str_tmp = "Decode response result faile!"
                    ret = ERR_FAIL
              
            elif (rpc_event == EV_RPC_SETPARAMETERATTRIBUTES_RSP):
                str_tmp = "\n*****%s Succeed!******\n" % rpc_object.rpc_name
                
            elif (rpc_event == EV_RPC_GETPARAMETERATTRIBUTES_RSP):
                if result:
                    list_tmp = []
                    str_tmp = "\n*****%s Succeed!******\n-----The Result:\n"%rpc_object.rpc_name
                    for x in result.ParameterList:
                        dict_tmp = {}
                        str_tmp += "Name = %s; Notification = %s; AccessList = %s\n" % (x.Name,
                                                                                        x.Notification,
                                                                                        x.AccessList)
                        dict_tmp["Name"] = x.Name
                        dict_tmp["Notification"] = x.Notification
                        dict_tmp["AccessList"] = x.AccessList
                        list_tmp.append(dict_tmp)
                    dict_data["ParameterList"] = list_tmp
                else:
                    str_tmp = "Decode response result faile!"
                    ret = ERR_FAIL
                
            elif (rpc_event == EV_RPC_ADDOBJECT_RSP):
                if result:
                    str_tmp = "\n*****%s Succeed!******\n-----The Result:\n" % rpc_object.rpc_name
                    str_tmp += "NewObject:%s%s\n" % (rpc_object.rpc_args["ObjectName"], result.InstanceNumber)
                    str_tmp += "Status = %s\n" % result.Status
                    
                    dict_data["Status"] = result.Status
                    dict_data["InstanceNumber"] = result.InstanceNumber
                else:
                    str_tmp = "Decode response result faile!"
                    ret = ERR_FAIL
                
            elif (rpc_event == EV_RPC_DELETEOBJECT_RSP):
                if result:
                    str_tmp = "\n*****%s Succeed!******\n-----The Result:\n" % rpc_object.rpc_name
                    str_tmp += "DeleteObject:%s\n" % rpc_object.rpc_args["ObjectName"]
                    str_tmp += "Status = %s\n" % result.Status
                    
                    dict_data["Status"] = result.Status
                else:
                    str_tmp = "Decode response result faile!"
                    ret = ERR_FAIL
                
            elif (rpc_event == EV_RPC_REBOOT_RSP):
                str_tmp = "\n*****Reboot Succeed!!!*****\n"
            
            elif (rpc_event == EV_RPC_DOWNLOAD_RSP):
                if result:
                    str_tmp = "\n*****%s Succeed!******\n-----The Result:\n"%rpc_object.rpc_name
                    str_tmp +=  "Status = %s\n StartTmie = %s\n CompleteTime =%s\n" % (result.Status,
                                                                                       result.StartTime,
                                                                                       result.CompleteTime)
                    dict_data["Status"] = result.Status
                    dict_data["StartTime"] = result.StartTime
                    dict_data["CompleteTime"] = result.CompleteTime
                else:
                    str_tmp = "Decode response result faile!"
                    ret = ERR_FAIL
                
            elif (rpc_event == EV_RPC_UPLOAD_RSP):
                if result:
                    str_tmp = "\n*****%s Succeed!******\n-----The Result:\n"%rpc_object.rpc_name
                    str_tmp +=  "Status = %s\n StartTmie = %s\n CompleteTime =%s\n" % (result.Status,
                                                                                       result.StartTime,
                                                                                       result.CompleteTime)
                    dict_data["Status"] = result.Status
                    dict_data["StartTime"] = result.StartTime
                    dict_data["CompleteTime"] = result.CompleteTime
                else:
                    str_tmp = "Decode response result faile!"
                    ret = ERR_FAIL
               
            elif (rpc_event == EV_RPC_FACTORYRESET_RSP):
                str_tmp = "\n*****FactoryReset Succeed!!!*****\n"
                
            elif (rpc_event == EV_RPC_SCHEDULEINFORM_RSP):
                str_tmp = "\n*****ScheduleInform Succeed!!!*****\n"
               
            elif (rpc_event == EV_RPC_GETQUEUEDTRANSFERS_RSP):
                if result:
                    list_tmp = []
                    str_tmp = "\n*****%s Succeed!******\n-----The Result:\n"%rpc_object.rpc_name
                    for x in result.TransferList:
                        dict_tmp = {}
                        str_tmp += "CommandKey = %s; State = %s\n" % (x.CommandKey,
                                                                      x.State)
                        dict_tmp["CommandKey"] = x.CommandKey
                        dict_tmp["State"] = x.State
                        list_tmp.append(dict_tmp)         
                    dict_data["TransferList"] = list_tmp
                else:
                    str_tmp = "Decode response result faile!"
                    ret = ERR_FAIL
                
            elif (rpc_event == EV_RPC_SETVOUCHERS_RSP):
                str_tmp = "\n*****SetVouchers Succeed!!!*****\n"
                
            elif (rpc_event == EV_RPC_GETOPTIONS_RSP):
                if result:
                    list_tmp = []
                    str_tmp = ret = "\n*****%s Succeed!******\n-----The Result:\n"%rpc_object.rpc_name
                    for x in result.OptionList:
                        dict_tmp = {}
                        str_tmp += "OptionName = %s; VoucherSN = %s; State = %s; \n\
                                 Mode = %s; StartDate = %s; ExpirationDate = %s; \
                                 IsTransferable = %s\n" % (x.OptionName, x.VoucherSN,
                                                           x.State, x.Mode, x.StartDate,
                                                           x.ExpirationDate, x.IsTransferable)
                        dict_tmp["OptionName"] = x.OptionName
                        dict_tmp["VoucherSN"] = x.VoucherSN
                        dict_tmp["State"] = x.State
                        dict_tmp["Mode"] = x.Mode
                        dict_tmp["StartDate"] = x.StartDate
                        dict_tmp["ExpirationDate"] = x.ExpirationDate
                        dict_tmp["IsTransferable"] = x.IsTransferable
                        list_tmp.append(dict_tmp)
                    dict_data["OptionList"] = list_tmp                    
                else:
                    str_tmp = "Decode response result faile!"
                    ret = ERR_FAIL
                
            elif (rpc_event == EV_RPC_GETALLQUEUEDTRANSFERS_RSP):
                if result:
                    list_tmp = []
                    str_tmp = ret = "\n*****%s Succeed!******\n-----The Result:\n"%rpc_object.rpc_name
                    for x in result.TransferList:
                        dict_tmp = {}
                        str_tmp += "CommandKey = %s; State = %s; IsDownload = %s; \
                                 FileType = %s; FileSize = %s; TargetFileName = %s\n" \
                                 % (x.CommandKey, x.State, x.IsDownload, x.FileType,
                                    x.FileSize, x.TargetFileName)
                        dict_tmp["CommandKey"] = x.CommandKey
                        dict_tmp["State"] = x.State
                        dict_tmp["IsDownload"] = x.IsDownload
                        dict_tmp["FileType"] = x.FileType
                        dict_tmp["FileSize"] = x.FileSize
                        dict_tmp["TargetFileName"] = x.TargetFileName
                        list_tmp.append(dict_tmp)
                    dict_data["TransferList"] = list_tmp
                else:
                    str_tmp = "Decode response result faile!"
                    ret = ERR_FAIL
                
            elif (rpc_event == EV_RPC_SCHEDULEDOWNLOAD_RSP):
                str_tmp = "\n*****ScheduleDownload Succeed!!!*****\n"
            
            elif (rpc_event == EV_RPC_CANCELTRANSFER_RSP):
                str_tmp = "\n*****CanelTransfer Succeed!!!*****\n"
                
            elif (rpc_event == EV_RPC_CHANGEDUSTATE_RSP):
                str_tmp = "\n*****ChangeDUState Succeed!!!*****\n"
                
            elif (int(rpc_event) & 0xFF00 == EVENT_RPC_GROUP):
                
                str_tmp = "\n******%s RPC method fail!!!******\n" % rpc_object.rpc_name
                try:
                    # TODO: result.detail maybe a list
                    # TODO: result.faultcode and result.faultstring maybe need parse too.
                    if result.detail:
                        list_tmp = []
                        
                        # parse FaultCode and FaultString in detail everytime, added by lana-20130810
                        str_tmp += "FaultCode:%s\nFaultString:%s\n" % (result.detail.FaultCode,
                                                                       result.detail.FaultString)
                        dict_data["FaultCode"] = result.detail.FaultCode
                        dict_data["FaultString"] = result.detail.FaultString
                        
                        if result.detail.SetParameterValuesFaultList:
                            for x in result.detail.SetParameterValuesFaultList:
                                dict_tmp = {}
                                str_tmp += "FaultCode:%s\nParameterName:%s\nFaultString:%s\n" \
                                       % (x.FaultCode, x.ParameterName, x.FaultString)
                                dict_tmp["FaultCode"] = x.FaultCode
                                dict_tmp["ParameterName"] = x.ParameterName
                                dict_tmp["FaultString"] = x.FaultString
                                list_tmp.append(dict_tmp)
                            dict_data["SetParameterValuesFaultList"] = list_tmp
                            
                    else:
                        str_tmp += "Fault Responsen Nothing Error Message!!!"
                except Exception, e:
                        str_tmp += "Responsen Nothing Error Message!!!message:%s" % e
            else:
                ret = ERR_FAIL
                str_tmp += "Event can't find!!!"
                log.app_info(str_tmp)
                
        except Exception, e:
            ret = ERR_FAIL
            str_tmp += "%s convert result error\n error message:%s" % (rpc_object.rpc_name, e)
            log.app_info(str_tmp)
            
        dict_ret["str_result"] = str_tmp
        dict_ret["dict_data"] = dict_data
        if ret == ERR_FAIL:
            log.app_info("---Convert_result Error---")
        else:
            log.app_info("-----Convert_result Succeed----")
   
        return ret, dict_ret


    def check_user_cmd_valid(self, user_rpc):
        """    
        """
        ret = None
        ret_ex = None
        
        try:     
            ret, ret_ex = self.convert_args(self.cpe_user.get_user_event(), user_rpc.rpc_args)
        except Exception,e:
            ret =ERR_FAIL
            print_trace(e) 
            
        return ret


    def get_parameter_type(self, str_name):
        """
        Get the parameters type,Return the Parameters's type.
        """
        global dict_all_parameters_type
        tmp_name = re.sub('\.\d+\.', '.{i}.', str_name)
        n = dict_all_parameters_type
        tmp_type = dict_all_parameters_type.get(tmp_name, None)
    
        return tmp_type   
        

    @staticmethod
    def get_cpe(sn):
        return CPE.m_dict_sn2cpe.get(sn)


    @staticmethod
    def get_cpe_bysessionno(soap_sessionno):
        return CPE.m_dict_sessionno2cpe.get(soap_sessionno)  

    
    def get_url(self):
        """
        """
        ret = ERR_FAIL
        ret_api = None
        sn = None
        
        sn = self.get_sn()
        
        username = self.cpe_property.get_acs2cpe_loginname()
        password = self.cpe_property.get_acs2cpe_loginpassword()

        # step1 use real username&password; try some times to get cpe url(cpe may busy)
        for loop in [1,2]:

            log.app_info("cpe(sn=%s), acs attempt current ACS2CPE_LOGIN_NAME(%s) and ACS2CPE_LOGIN_PASSWORD(%s)" % (sn, username, password))        

            ret_api, err_message = get_url(sn, self.cpe_property.get_acs2cpe_url(), username, password)    
            if (ret_api == AUTHENTICTATE_SUCCEED):

                ret = ERR_SUCCESS
                break      

        if (ret != ERR_SUCCESS):

            # nwf 2013-07-26; cfg is the same as current
            is_same = (username == webservercfg.ACS2CPE_LOGIN_NAME)  and (password == webservercfg.ACS2CPE_LOGIN_PASSWORD)                            
            if (not is_same):
            
                # step2 use default username&password;
                username = webservercfg.ACS2CPE_LOGIN_NAME
                password = webservercfg.ACS2CPE_LOGIN_PASSWORD     

                
                for loop in [1,2]:

                    # gcw 2013-05-02; cpe may reboot and recovery password
                    log.app_info("cpe(sn=%s), attempt default ACS2CPE_LOGIN_NAME(%s) and ACS2CPE_LOGIN_PASSWORD(%s)" % (sn, username, password))
                
                    ret_api, err_message = get_url(sn, self.cpe_property.get_acs2cpe_url(), username, password)    
                    if (ret_api == AUTHENTICTATE_SUCCEED):

                        ret = ERR_SUCCESS
                        # switch to default
                        self.set_default_username_password()
                        
                        break   
                             
        return ret, err_message


    def get_cpe2acs_url(self):
        """
        eg http://172.125.105.26:18015/ACS-server/ACS
        """
        ip =webservercfg.HTTP_IP
        port = webservercfg.HTTP_PORT
        cpe2acs_page = webservercfg.CPE2ACS_PAGE
        
        ret = "http://%s:%s%s" %(ip, port, cpe2acs_page)
        
        return ret   


    @staticmethod 
    def get_inform_eventcodes(soap_inform):
        eventcodes = []
        
        events = soap_inform.result.Event
        for event in events:
            eventcodes.append(event.EventCode)        

        return eventcodes
        

    def is_auth(self, request, sn):
        """
        sn = '021018000074'
        ERR_SUCCESS  auth ok
        ERR_FAIL    auth fail
        ERR_FATAL   auth fail(has no auth info)
        """
        ret = None
        ret_api = None        
        dict_data = {}

        dict_data["auth_type"] = self.cpe_property.get_cpe_authtype()
        username = self.cpe_property.get_cpe2acs_loginname()
        password = self.cpe_property.get_cpe2acs_loginpassword()  
                 
        if (self.cpe_property.get_cpe_isauth() == False):                 
            # step1 use real username&password;
            dict_data["username"] = username
            dict_data["password"] = password

            # step2 use default username&password;
            username = webservercfg.CPE2ACS_LOGIN_NAME
            password = webservercfg.CPE2ACS_LOGIN_PASSWORD
            dict_data2 = {}
            dict_data2["username"] = username
            dict_data2["password"] = password 
            dict_data2["is_default"] = False
            
            ret_api = authenticate_acs_cperequest(request, sn, dict_data, dict_data2)   
            if (ret_api == ACS_AUTHENTICATE_PASS):
                ret = ERR_SUCCESS
                self.cpe_property.set_cpe_isauth(True)
            elif (ret_api == ACS_AUTHENTICATE_FAIL):
                ret = ERR_FAIL
            else:
                # cpe first send soap [head has no auth info(3-state)]
                ret = ERR_FATAL      
                
            if (dict_data2["is_default"]):
                self.set_default_username_password()                  
                    
        else:
            ret = ERR_SUCCESS                
            
        return ret     


    def is_inform_6(self):
        """
        inform = 6 CONNECTION REQUEST
        user rpc need  send to cpe?
        """
        ret = False
        
        soap_inform = self.cpe_soap.get_soap_inform()
        if (not soap_inform):
            return ret
        
        events = soap_inform.result.Event
        for event in  events:
            if (event.EventCode == "6 CONNECTION REQUEST"):
                ret = True
                break
                
        return ret


    @staticmethod 
    def is_inform_x(soap_inform, eventcode):
        """
        """
        
        ret = False
        if (not soap_inform):
            return ret
        
        events = soap_inform.result.Event
        for event in  events:
            if (event.EventCode == eventcode):
                ret = True
                break
                
        return ret        
    

    @staticmethod 
    def new_http_client_send2agent_async(msg):
        """
        """

        d=threads.deferToThread(CPE.new_http_client_send2agent, msg)
        
        return None 


    @staticmethod 
    def new_http_client_send2agent(msg, timeout=webservercfg.SHORT_CONNECTION_TIMEOUT):
        """
        in thread
        """
        ret         = ERR_FAIL
        err_message = ""    

        for nwf in [1]:

            try:                                            
                url = "http://%s:%s%s" %(webservercfg.AGENT_HTTP_IP, webservercfg.AGENT_HTTP_PORT, webservercfg.ACS2AGENT_PAGE)
                httpclient1 = HttpClient(url, timeout)             

                ret, err_message = httpclient1.send_message(msg)  
                if (ret != ERR_SUCCESS): 

                    desc = "----retry----:%s" %err_message
                    log.app_err(desc)
                    
                    # retry 
                    ret, err_message = httpclient1.send_message(msg)               
                    if (ret != ERR_SUCCESS):
                        log.app_err(err_message)
                        
            except Exception, e:
                print_trace(e)                                                

        return ret        


    @staticmethod    
    def request_write(request, body, mysql_message, sn="", response_code=None):
        """
        auto add header:
        """
        
        request.setHeader("Content-Type", "text/xml; charset=utf-8")      
        request.setHeader("Server", testlibversion.VERSION)
        request.setHeader("SOAPAction", "")
  
        request.setHeader("Content-Length", len(body))
                
        format1="%a, %d %b %Y %H:%M:%S GMT"
        time1=datetime.utcnow().strftime(format1)
        request.setHeader("Date", time1)
        request.setHeader("Content-Length", len(body))

        # nwf 2013-06-20;
        if (response_code):
            request.setResponseCode(response_code)
            
        request.write(body)        
        request.finish()   

        # mysql
        content_head = str(request.responseHeaders)
        content_body = body
        
        content_head2 = ""
        try:
            # save_out_head
            content_head2 = request.content_head_out
        except Exception,e:        
            pass
        
        soap_id = insert_acs_soap(mysql_message, "OUT", sn, content_head, content_head2, content_body)
        if (mysql_message == "204"):
            cpe = CPE.get_cpe(sn)
            cpe.cpe_db_index.set_soap_204_id(soap_id)
            

    @staticmethod    
    def user_request_write(request, msg):
        """
        """
        request.write(msg)
        request.finish()
        request.transport.loseConnection()  # local need(remote don't)        
            

    def reset_cpe_session(self):
        """
        reset cpe's property
        """        
        self.cpe_soap.set_soap_msg(None)
        self.cpe_soap.set_soap_sessionno(None) 
        
        # steady status:ready or init
        if (self.get_status() != CPE_ST_READY):
            self.set_status(CPE_ST_INIT)        

        try:
            self.cpe_property.get_cpe_timer().cancel()
        except Exception,e: 
            pass
        self.cpe_property.set_cpe_timer(None)                
        self.cpe_property.set_cpe_isauth(False)
        self.cpe_property.set_cpe_request(None)


    def set_default_username_password(self):
        """
        read cfg
        """
        dict_col = {}
        dict_data = {}
        
        value = webservercfg.ACS2CPE_LOGIN_NAME
        if self.cpe_property.is_update_acs2cpe_name(value):
            dict_col['ACS2CPE_NAME'] = value
            
        value = webservercfg.ACS2CPE_LOGIN_PASSWORD
        if self.cpe_property.is_update_acs2cpe_password(value):
            dict_col['ACS2CPE_PASSWORD'] = value
        
        value = webservercfg.CPE2ACS_LOGIN_NAME
        if self.cpe_property.is_update_cpe2acs_name(value):
            dict_col['CPE2ACS_NAME'] = value
        
        value  = webservercfg.CPE2ACS_LOGIN_PASSWORD
        if self.cpe_property.is_update_cpe2acs_password(value):
            dict_col['CPE2ACS_PASSWORD'] = value
            
        if dict_col:
            # 字典的值不为空时，才更新数据库
            dict_data['columns'] = dict_col
            dict_data['condition'] = 'CPE_ID=%s' % self.get_cpe_id()
            operate_db('CPE', 'UPDATE', dict_data)
        
        """
        self.cpe_property.set_acs2cpe_loginname(webservercfg.ACS2CPE_LOGIN_NAME)
        self.cpe_property.set_acs2cpe_loginpassword(webservercfg.ACS2CPE_LOGIN_PASSWORD)
        self.cpe_property.set_cpe2acs_loginname(webservercfg.CPE2ACS_LOGIN_NAME)
        self.cpe_property.set_cpe2acs_loginpassword(webservercfg.CPE2ACS_LOGIN_PASSWORD)
        """


    @staticmethod 
    def tx_fault(request, version, args, cwmp_id):
        """
        create Fault message and send to CPE
        """
        ret = ERR_FAIL
        ret_api = None

        for nwf in [1]:
            try:                
                obj_construct = construct.Construct()            
                soap_message = "Fault"
                obj_fault = Fault()
                obj_fault.faultcode = "Server"
                obj_fault.faultstring = "CWMP fault"
                
                obj_fault.detail = CWMPFaultStruct()
                
                obj_fault.detail.FaultCode = args[0]
                obj_fault.detail.FaultString = args[1]
                
                ret_api, desc = obj_construct.create_soap_envelope(soap_message, 
                                                                    version, 
                                                                    obj_fault, 
                                                                    cwmp_id)
                if (construct.CONSTRUCT_SUC != ret_api):
                    break
                
                CPE.request_write(request, obj_construct.str_xml, "Fault") 
                
            except Exception,e:
                print_trace(e) 
                break
            ret = ERR_SUCCESS
            
        return ret
                           
        
# --------------------------------------------------- 
def on_cpe_timeout(cpe, request, timer_name):
    """
    """
    ret = None

    for nwf in [1]:
    
        user_rpc = cpe.cpe_user.get_user_rpc()        
        desc =  ("cpe sn=%s, status=%s, rpc=%s, timer_name=%s" 
                %(cpe.get_sn(), cpe.get_status_desc(), user_rpc and user_rpc.rpc_name, timer_name))
        log.app_info(desc)
        
        cpe.close_session()    
            
        cpe.set_status(CPE_ST_INIT)

        # nwf 2014-02-19; acs close cpe session, should not send user fail
        if ("WAIT_CPE_SESSION_LOST_TIMEOUT" == timer_name):
            break
        
        # user rpc fail
        desc = "timeout; " + desc
        ret = cpe.on_tx_user_rpc_fail(desc)
    
    return ret 


def on_user_timeout_60s(cpe):
    """
    user wait cpe's inform, but timeout
    timeout=60s, only inform6 can cancel timer
    """
    ret = None

    user_rpc = cpe.cpe_user.get_user_rpc() 
    desc =  ("cpe sn=%s, status=%s, rpc=%s, user wait cpe's inform timeout(step1=60s)." 
            %(cpe.get_sn(), cpe.get_status_desc(), user_rpc and user_rpc.rpc_name))
    log.app_info(desc)

    # timeout 180s, another chance
    timer = reactor.callLater(cpe.cpe_soap.get_soap_inform_timeout(), on_user_timeout_180s, cpe)
    cpe.cpe_user.set_user_timer_180s(timer)        
        
    return ret 


def on_user_timeout_180s(cpe):
    """
    user wait cpe's inform, but timeout
    timeout=180s, any inform can cancel timer
    """
    ret = None

    user_rpc = cpe.cpe_user.get_user_rpc() 
    desc =  ("cpe sn=%s, status=%s, rpc=%s, user wait cpe's inform timeout(step2=%ss)." %
            (cpe.get_sn(), cpe.get_status_desc(), user_rpc and user_rpc.rpc_name, cpe.cpe_soap.get_soap_inform_timeout()))
    log.app_info(desc)

    ret = cpe.on_tx_user_rpc_fail(desc)
        
    return ret     


def on_user_timeout_180s_cancel_tell_user(cpe):
    """
    """
    desc = "wait inform 60s fail, wait inform 180s fail too."
    ret = cpe.on_tx_user_rpc_fail(desc)     
               
            

if __name__ == '__main__':
    pass
 
