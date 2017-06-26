#coding:utf-8

"""
    nwf 2012-10-08  V1.0
                    1 message interface
    nwf 2013-03-07  V1.1
                    1 +worklist
    nwf 2013-05-25  unify

"""


# post key
KEY_MESSAGE     = "KEY_MESSAGE"
KEY_OBJECT      = "KEY_OBJECT"

# added by lana--20121113
KEY_MESSAGE_TYPE    = "KEY_MESSAGE_TYPE"
KEY_SN              = "KEY_SN"
KEY_QUEUE           = "KEY_QUEUE"   # the value of KEY_QUEUE can be INIT, WAIT, [requet1,rquest2...]
KEY_SEQUENCE        = "KEY_SEQUENCE"

#KEY_QUEUE value including following
QUEUE_INIT = "INIT" # agent do not wait pre rpc exec first, return fail 
QUEUE_WAIT = "WAIT" # agent wait pre rpc exec first

#add by wangjun-2013-04-16
KEY_PRIORITY_LEVEL  ="KEY_PRIORITY_LEVEL"#key_priority_level
#KEY_PRIORITY_LEVEL value including following
PRIORITY_HIGH       ="HIGH"
PRIORITY_NORMAL     ="NORMAL"

#add by wangjun-201305-25
KEY_SENDER          = "KEY_SENDER" #key_sender

KEY_SENDER_USER     = "user"
KEY_SENDER_WORKLIST = "worklist"
KEY_SENDER_ACS      = "acs"
KEY_SENDER_AGENT    = "agent" #wangjun add by 20130604


# MESSAGE_TYPE including following defined value

# agent create
MSG_TYPE_QUEUE_CHECK        = "MSG_TYPE_QUEUE_CHECK"
MSG_TYPE_NOTIFICATION       = "MSG_TYPE_NOTIFICATION"

# worklist 
WORK_LIST_TYPE_PHISIC   = "physic"
WORK_LIST_TYPE_LOGIC    = "logic"

WORK_LIST_STATUS_BUILD      = "build"
WORK_LIST_STATUS_BIND       = "bind"
WORK_LIST_STATUS_RESERVE    = "reserve" # bind<reserve<=exec
WORK_LIST_STATUS_RUNNING    = "running" # in exec
WORK_LIST_STATUS_STANDBY    = "standby" # hold in exec queue
WORK_LIST_STATUS_SUCCESS    = "success" # exec's result
WORK_LIST_STATUS_FAIL       = "fail"
WORK_LIST_STATUS_ABNORMAL   = "abnormal"    # eg tr069 reboot
WORK_LIST_STATUS_EXPIRE     = "expire"      # init time > 7 day


MONITOR_INFORM_STATUS_INIT          = "init"
MONITOR_INFORM_STATUS_START_BEGIN   = "start_begin"
MONITOR_INFORM_STATUS_START_SUCCESS = "start_success"
MONITOR_INFORM_STATUS_START_FAIL    = "start_fail"
MONITOR_INFORM_STATUS_STOP_BEGIN    = "stop_begin"
MONITOR_INFORM_STATUS_STOP_SUCCESS  = "stop_success"
MONITOR_INFORM_STATUS_STOP_FAIL     = "stop_fail"

# -----------------------------message -----------------------------------
class MsgUserRpc(object):
    """
    user send cmd
    acs received and return to user cmd
    """
    def __init__(self, sn="", rpc="", args={}, worklist_id=""):
        self.sn = sn
        
        self.rpc_name               = rpc
        self.rpc_args               = args
        self.worklist_id            = worklist_id
        
        self.dict_ret               = {}    
        self.dict_ret["str_result"] = ""
        # dict_ret{"str_result", "dict_data"}
        # dict_data["FaultCode"]=8002  
        # dict_data["FaultString"]="Internel error"  


class MsgUserRpcCheck(object):
    """
    """
    def __init__(self,sn='',event_rqst='',dict_ret={}):
        self.sn                     = sn
        self.event_rqst             = event_rqst
        self.dict_ret               = dict_ret  
        self.dict_ret["str_result"] = ""


#add by wangjun 20130624
class MsgRpcTimeout(object):
    """
    """
    def __init__(self,sn='', user_rpc_obj=None):
        self.sn                     = sn
        self.user_rpc_obj           = user_rpc_obj
        self.dict_ret               = {}    
        self.dict_ret["str_result"] = ""
        

# -----------------------------(query) ---------------------   
class MsgQueryCPEInfo(object):   
    """
    """
    def __init__(self, sn=''):
        self.sn                         = sn
        # cpe basic info 
        self.software_version           = ""                  
        self.hardware_version           = ""                 
        self.connection_request_url     = ""           
        self.cpe2acs_url                = ""
        
        self.cwmp_version               = ""
        self.cpe2acs_loginname          = ""
        self.cpe2acs_loginpassword      = ""
        self.acs2cpe_loginname          = ""
        self.acs2cpe_loginpassword      = ""
        self.soap_inform_timeout        = ""                   
        
        self.auth_type                  = ""
        self.worklist_domain            = ""
        self.worklist_rollback          = False
        self.cpe_operator               = "CT"
        
        self.interface_version          = "v3.0"        
        
        self.soap_inform                = None  # added by lana        
        self.dict_ret                   = {}   
        self.dict_ret["str_result"]     = ""
        

class MsgQueryCPEInterfaceVersion(object):   
    """
    """
    def __init__(self, sn=''):
        self.sn                         = sn
        self.dict_ret                   = {}    
        self.dict_ret["str_result"]     = ""    
        
        
class MsgQueryCPEOnline(object):   
    """
    """
    def __init__(self, sn=''):
        self.sn                     = sn
        self.online_status          = {}        # {sn1:online,sn2:online}
        self.dict_ret               = {}               
        self.dict_ret["str_result"] = ""


class MsgQueryIsHang(object):   
    """
    """
    def __init__(self):
        self.dict_ret               = {}    
        self.dict_ret["str_result"] = ""
        

class MsgQueryVersionIsOk(object):   
    """
    """
    def __init__(self):
        self.version = ""   # 'v.beta131021.svn1719' or "v2.3.0"
        self.dict_ret               = {}    
        self.dict_ret["str_result"] = ""        


class MsgQueryLastSessionSoap(object):   
    """
    """
    def __init__(self, sn):
        self.sn                     = sn
        self.dict_ret               = {}    
        self.dict_ret["str_result"] = ""
        


# ----------------------------- worklist  message ---------------------
class MsgWorklist(object):
    """
    """

    def __init__(self, id_="", 
                      type_="", 
                      sn="", username="", userid="", 
                      operator="", cpe_interface_version="", domain="", 
                      worklist_name="", dict_data={}, 
                      status="", 
                      time_build="", time_bind="", time_reserve="", 
                      time_exec_start="", time_exec_end=""):
        """
        worklist info, 1 line 
        """
        self.id_                = id_       # auto generated, like time tag
        self.worklist_name      = worklist_name        
        self.sn                 = sn   
        self.operator           = operator
        self.cpe_interface_version  = cpe_interface_version
        self.domain             = domain        
        self.type_              = type_     # physic or logic
        self.group              = "USER"    # USER or SYS, default=USER
        self.username           = username
        self.userid             = userid
        self.status             = status  
        self.rollback           = False     # if worklist fail then rollback rpc        
        self.dict_data          = dict_data
        self.time_build         = time_build
        self.time_bind          = time_bind
        self.time_reserve       = time_reserve
        self.time_exec_start    = time_exec_start
        self.time_exec_end      = time_exec_end
        self.desc               = ""        # desc 4 status

        # acs use below variable
        #self.event
        #self.timer
        self.dict_ret               = {}        
        self.dict_ret["str_result"] = ""
        

class MsgWorklistBuild(MsgWorklist):
    """
    build/upload worklist
    """
    def __init__(self, worklist_name="", dict_data={}, group="USER"):
        """
        """
        super(MsgWorklistBuild, self).__init__()
        
        self.worklist_name  = worklist_name # eg PPPoEWANSetUp
        self.dict_data      = dict_data     # worklist datafile parameters                                
                                # "parameter1":(value or value list, appendix)
                                # "parameter2":(value or value list, appendix)                
        self.group = group                                

class MsgWorklistBindPhysical(MsgWorklist):
    """
    """
    def __init__(self, id_, sn=""):
        """
        """
        super(MsgWorklistBindPhysical, self).__init__()
        
        self.id_    = id_
        self.sn     = sn           
        
class MsgWorklistBindLogical(MsgWorklist):
    """
    """
    def __init__(self, id_, username="", userid=""):
        """
        """
        super(MsgWorklistBindLogical, self).__init__()
        
        self.id_        = id_
        self.username   = username
        self.userid     = userid             
        
class MsgWorklistExecute(MsgWorklist):
    """
    user tell agent/acs 
    """
    def __init__(self, id_):
        """        
        """        
        super(MsgWorklistExecute, self).__init__()
        
        self.id_ = id_
        
class MsgWorklistExecStart(MsgWorklist):
    """
    exec start tell acs
    """
    def __init__(self, id_):
        """        
        """        
        super(MsgWorklistExecStart, self).__init__()
        
        self.id_ = id_     

#add by wangjun 20130530
class MsgWorklistExecRsp(MsgWorklist):
    """
    exec response tell agent
    """
    def __init__(self, id_, sn, execute_status, dict_ret):
        """        
        """        
        super(MsgWorklistExecRsp, self).__init__()
        
        self.id_            = id_
        self.sn             = sn
        self.execute_status = execute_status    # EV_WORKLIST_EXECUTE_RSP or fail
        self.dict_ret       = dict_ret          



class MsgWorklistExecFinish(MsgWorklist):
    """
    exec response tell acs
    """
    def __init__(self, id_, event, dict_ret):
        """        
        """        
        super(MsgWorklistExecFinish, self).__init__()
        
        self.id_            = id_
        self.execute_status = event             # EV_WORKLIST_EXECUTE_RSP or fail
        self.dict_ret       = dict_ret          # "str_result"
                             

class MsgWorklistReserve(MsgWorklist):
    """
    reserve one worklist success, then can exec
    """
    def __init__(self, id_):
        """        
        """        
        super(MsgWorklistReserve, self).__init__()
        
        self.id_ = id_   

class MsgWorklistQuery(MsgWorklist):
    """
    query 1 record
    """
    def __init__(self, id_):
        """        
        """        
        super(MsgWorklistQuery, self).__init__()
        
        self.id_ = id_           
        
                
class MsgWorklistDownload(object):
    """   
    """
    def __init__(self):
        """        
        """        
        self.operator   = "CT"      # CT or CU
        self.cpe_interface_versions = []  # v3.0 v4.0, MsgWorklistCpeInterfaceVersion list
        
        self.dict_ret   = {}        

class MsgWorklistCpeInterfaceVersion(object):
    """    
    """
    def __init__(self, cpe_interface_version=""):
        """        
        """
        self.cpe_interface_version = cpe_interface_version # eg v3.0
        self.domains    = []        # MsgWorklistDomain list  


class MsgWorklistDomain(object):
    """    
    """
    def __init__(self, name=""):
        """        
        """
        self.name           = name  # eg EPON
        self.wl_datafiles   = []    # eg PPPoEWANSetUp_script.py + BridgeWANSetUp_script.py

class MsgWorklistFile(object):
    """
    """
    def __init__(self, name=""):
        """        
        """
        self.name       = name  # eg PPPoEWANSetUp
        self.dict_data  = {}    #  parameter format
                        # 'parameter1': (value or value list, appendix)
                        # 'parameter2': (value or value list, appendix)                


# -----------------------------(configure) ---------------------
class MsgConfig(object):
    """
    user gui or RF  configure  
    nwf 2013-05-06, no matter what cpe online
    """
    def __init__(self, sn=""):
        self.sn                     = sn
        self.acs2cpe_loginname      = None  # None is not cfg
        self.acs2cpe_loginpassword  = None      
        self.soap_inform_timeout    = None  #zsj add
        self.cpe2acs_loginname      = None
        self.cpe2acs_loginpassword  = None
        self.auth_type              = None  # auth_type=["digest","basic","False"]
        self.cwmp_version           = None  # auto= inform cwmp version
        self.worklist_domain        = None
        self.worklist_rollback      = None  # (True or False) worklist fail, rpc rollback
        
        self.dict_ret               = {}    # dict_ret{"str_result","dict_data"}
        self.dict_ret["str_result"] = ""
        

class MsgModifyCPEInfo(object):
    """
    modify CPE info
    nwf 2013-05-06, no matter what cpe online
    """
    def __init__(self, sn=""):
        self.sn                     = sn     
        self.dict_modify_items      = {}    # modify items,eg{auth_type:"digest",cwmp_version="cwmp-1-1", worklist_domain="ADSL",}
        self.dict_ret               = {}    # result of modify, dict_ret={str_result:description, dict_data:result of data}
        self.dict_ret["str_result"] = ""        
        

class MsgWaitEventCode(object):
    """
    """
    def __init__(self, sn=""):
        self.id_                        = ""
        self.sn                         = sn  
        self.include_eventcodes         = []
        self.exclude_eventcodes         = []
        self.status                     = ""    # start or stop
        self.time_start                 = None
        self.time_stop                  = None        
        self.dict_ret                   = {} 
        self.dict_ret["str_result"]     = ""
        

class MsgAlarmInform(object):
    """
    alarm  inform
    """
    def __init__(self, sn=""):
        self.eventcode              = ""    # "X CT-COM ALARM"
        self.sn                     = sn     
        self.id_                    = ""
        self.status                 = ""    # start or stop
        self.time_start             = None
        self.time_stop              = None
        self.node_add_object        = None  # tr069 node value (InternetGatewayDevice.DeviceInfo.X_CT-COM_Alarm.AlarmConfig.1)

        self.parameterlist          = ""    # alarm detail(InternetGatewayDevice.WANDevice.1.WANConnectionDevice.4.WANIPConnection.1.Stats.EthernetPacketsReceived)        
        self.limit_min              = "" 
        self.limit_max              = ""        
        self.timelist               = ""
        self.mode                   = ""        
        
        self.parameter_values       = []    # ret value; [(time1, value1), (time2, value2)]           
        self.dict_ret               = {}
        self.dict_ret["str_result"] = ""
        

class MsgMonitorInform(object):
    """
    monitor inform
    """
    def __init__(self, sn=""):
        self.eventcode              = ""    # "X CT-COM MONITOR"
        self.sn                     = sn     
        self.id_                    = ""
        self.status                 = ""    # start or stop
        self.time_start             = None
        self.time_stop              = None
        self.node_add_object        = None  # tr069 node value
        
        self.parameterlist          = ""    # monitor detail
        self.timelist               = ""     
        
        self.parameter_values       = []    # ret value; [(time1, value1), (time2, value2)]             
        self.dict_ret               = {}
        self.dict_ret["str_result"] = ""


class MsgTR069Close(object):
    """
    """
    def __init__(self):
        self.dict_ret               = {}    
        self.dict_ret["str_result"] = ""


class MsgQueryCpeLastFaults(object):
    """
    """
    def __init__(self, sn):
        self.sn                     = sn
        self.dict_ret               = {}    
        self.dict_ret["str_result"] = ""


# -------------------------------------event ----------------------------

EVENT_RPC_GROUP         = 0x1000    #0x xxyy  xx is type;yy is specific 
EVENT_QUERY_GROUP       = 0x1100       
EVENT_WORKLIST_GROUP    = 0x1200    
EVENT_CONFIGURE_GROUP   = 0x1300    # configure cpe info

# -------------------------------------------------------rpc cfg
EV_RPC_GETRPCMETHODS_RQST           = (EVENT_RPC_GROUP + 0)        
EV_RPC_GETRPCMETHODS_RSP            = (EVENT_RPC_GROUP + 1)
EV_RPC_GETRPCMETHODS_FAIL           = (EVENT_RPC_GROUP + 2)

EV_RPC_SETPARAMETERVALUES_RQST      = (EVENT_RPC_GROUP + 3)
EV_RPC_SETPARAMETERVALUES_RSP       = (EVENT_RPC_GROUP + 4)
EV_RPC_SETPARAMETERVALUES_FAIL      = (EVENT_RPC_GROUP + 5)

EV_RPC_GETPARAMETERVALUES_RQST      = (EVENT_RPC_GROUP + 6)
EV_RPC_GETPARAMETERVALUES_RSP       = (EVENT_RPC_GROUP + 7) 
EV_RPC_GETPARAMETERVALUES_FAIL      = (EVENT_RPC_GROUP + 8) 

EV_RPC_GETPARAMETERNAMES_RQST       = (EVENT_RPC_GROUP + 9) 
EV_RPC_GETPARAMETERNAMES_RSP        = (EVENT_RPC_GROUP + 10) 
EV_RPC_GETPARAMETERNAMES_FAIL       = (EVENT_RPC_GROUP + 11) 

EV_RPC_SETPARAMETERATTRIBUTES_RQST  = (EVENT_RPC_GROUP + 12) 
EV_RPC_SETPARAMETERATTRIBUTES_RSP   = (EVENT_RPC_GROUP + 13) 
EV_RPC_SETPARAMETERATTRIBUTES_FAIL  = (EVENT_RPC_GROUP + 14) 

EV_RPC_GETPARAMETERATTRIBUTES_RQST  = (EVENT_RPC_GROUP + 15) 
EV_RPC_GETPARAMETERATTRIBUTES_RSP   = (EVENT_RPC_GROUP + 16) 
EV_RPC_GETPARAMETERATTRIBUTES_FAIL  = (EVENT_RPC_GROUP + 17) 

EV_RPC_ADDOBJECT_RQST               = (EVENT_RPC_GROUP + 18) 
EV_RPC_ADDOBJECT_RSP                = (EVENT_RPC_GROUP + 19) 
EV_RPC_ADDOBJECT_FAIL               = (EVENT_RPC_GROUP + 20) 

EV_RPC_DELETEOBJECT_RQST            = (EVENT_RPC_GROUP + 21) 
EV_RPC_DELETEOBJECT_RSP             = (EVENT_RPC_GROUP + 22) 
EV_RPC_DELETEOBJECT_FAIL            = (EVENT_RPC_GROUP + 23) 

EV_RPC_REBOOT_RQST                  = (EVENT_RPC_GROUP + 24) 
EV_RPC_REBOOT_RSP                   = (EVENT_RPC_GROUP + 25) 
EV_RPC_REBOOT_FAIL                  = (EVENT_RPC_GROUP + 26) 

EV_RPC_DOWNLOAD_RQST                = (EVENT_RPC_GROUP + 27) 
EV_RPC_DOWNLOAD_RSP                 = (EVENT_RPC_GROUP + 28) 
EV_RPC_DOWNLOAD_FAIL                = (EVENT_RPC_GROUP + 29) 

EV_RPC_UPLOAD_RQST                  = (EVENT_RPC_GROUP + 30) 
EV_RPC_UPLOAD_RSP                   = (EVENT_RPC_GROUP + 31) 
EV_RPC_UPLOAD_FAIL                  = (EVENT_RPC_GROUP + 32) 

EV_RPC_FACTORYRESET_RQST            = (EVENT_RPC_GROUP + 33) 
EV_RPC_FACTORYRESET_RSP             = (EVENT_RPC_GROUP + 34) 
EV_RPC_FACTORYRESET_FAIL            = (EVENT_RPC_GROUP + 35) 

EV_RPC_SCHEDULEINFORM_RQST          = (EVENT_RPC_GROUP + 36) 
EV_RPC_SCHEDULEINFORM_RSP           = (EVENT_RPC_GROUP + 37) 
EV_RPC_SCHEDULEINFORM_FAIL          = (EVENT_RPC_GROUP + 38) 

EV_RPC_GETQUEUEDTRANSFERS_RQST      = (EVENT_RPC_GROUP + 39) 
EV_RPC_GETQUEUEDTRANSFERS_RSP       = (EVENT_RPC_GROUP + 40) 
EV_RPC_GETQUEUEDTRANSFERS_FAIL      = (EVENT_RPC_GROUP + 41) 

EV_RPC_SETVOUCHERS_RQST             = (EVENT_RPC_GROUP + 42) 
EV_RPC_SETVOUCHERS_RSP              = (EVENT_RPC_GROUP + 43) 
EV_RPC_SETVOUCHERS_FAIL             = (EVENT_RPC_GROUP + 44) 

EV_RPC_GETOPTIONS_RQST              = (EVENT_RPC_GROUP + 45) 
EV_RPC_GETOPTIONS_RSP               = (EVENT_RPC_GROUP + 46) 
EV_RPC_GETOPTIONS_FAIL              = (EVENT_RPC_GROUP + 47) 

EV_RPC_GETALLQUEUEDTRANSFERS_RQST   = (EVENT_RPC_GROUP + 48) 
EV_RPC_GETALLQUEUEDTRANSFERS_RSP    = (EVENT_RPC_GROUP + 49) 
EV_RPC_GETALLQUEUEDTRANSFERS_FAIL   = (EVENT_RPC_GROUP + 50) 

EV_RPC_SCHEDULEDOWNLOAD_RQST        = (EVENT_RPC_GROUP + 51) 
EV_RPC_SCHEDULEDOWNLOAD_RSP         = (EVENT_RPC_GROUP + 52) 
EV_RPC_SCHEDULEDOWNLOAD_FAIL        = (EVENT_RPC_GROUP + 53) 

EV_RPC_CANCELTRANSFER_RQST          = (EVENT_RPC_GROUP + 54) 
EV_RPC_CANCELTRANSFER_RSP           = (EVENT_RPC_GROUP + 55) 
EV_RPC_CANCELTRANSFER_FAIL          = (EVENT_RPC_GROUP + 56) 

EV_RPC_CHANGEDUSTATE_RQST           = (EVENT_RPC_GROUP + 57) 
EV_RPC_CHANGEDUSTATE_RSP            = (EVENT_RPC_GROUP + 58) 
EV_RPC_CHANGEDUSTATE_FAIL           = (EVENT_RPC_GROUP + 59) 

# get_url
EV_RPC_CONNECTION_REQUEST_RQST      = (EVENT_RPC_GROUP + 60) 
EV_RPC_CONNECTION_REQUEST_RSP       = (EVENT_RPC_GROUP + 61) 
EV_RPC_CONNECTION_REQUEST_FAIL      = (EVENT_RPC_GROUP + 62) 



# nwf 2013-06-03; rpc group acknowledge for rpc rqst
EV_RPC_CHECK_RSP                    = (EVENT_RPC_GROUP + 0xf0)  # success
EV_RPC_CHECK_FAIL                   = (EVENT_RPC_GROUP + 0xf1)  # fail

#add by wangjun 20130624 # rpc timout message
EV_RPC_AGENT_TIMEOUT_POST           = (EVENT_RPC_GROUP + 0xf2) 
EV_RPC_AGENT_TIMEOUT_RSP            = (EVENT_RPC_GROUP + 0xf3)


# ---------------------------------------------- query(acs) ----------------
EV_QUERY_ONLINE_CPE_RQST        = (EVENT_QUERY_GROUP + 0)       
EV_QUERY_ONLINE_CPE_RSP         = (EV_QUERY_ONLINE_CPE_RQST + 1)
EV_QUERY_ONLINE_CPE_FAIL        = (EV_QUERY_ONLINE_CPE_RQST + 2)

EV_QUERY_ALL_ONLINE_CPE_RQST    = (EVENT_QUERY_GROUP + 3)    
EV_QUERY_ALL_ONLINE_CPE_RSP     = (EV_QUERY_ALL_ONLINE_CPE_RQST + 1)     
EV_QUERY_ALL_ONLINE_CPE_FAIL    = (EV_QUERY_ALL_ONLINE_CPE_RQST + 2)    

EV_QUERY_CPE_INFO_RQST          = (EVENT_QUERY_GROUP + 6)        
EV_QUERY_CPE_INFO_RSP           = (EV_QUERY_CPE_INFO_RQST + 1)
EV_QUERY_CPE_INFO_FAIL          = (EV_QUERY_CPE_INFO_RQST + 2)

EV_QUERY_IS_HANG_RQST           = (EVENT_QUERY_GROUP + 9)
EV_QUERY_IS_HANG_RSP            = (EV_QUERY_IS_HANG_RQST + 1)
EV_QUERY_IS_HANG_FAIL           = (EV_QUERY_IS_HANG_RQST + 2)

EV_QUERY_VERSION_IS_OK_RQST     = (EVENT_QUERY_GROUP + 12)
EV_QUERY_VERSION_IS_OK_RSP      = (EV_QUERY_VERSION_IS_OK_RQST + 1)
EV_QUERY_VERSION_IS_OK_FAIL     = (EV_QUERY_VERSION_IS_OK_RQST + 2)

EV_QUERY_CPE_LAST_FAULTS_RQST   = (EVENT_QUERY_GROUP + 15)
EV_QUERY_CPE_LAST_FAULTS_RSP    = (EV_QUERY_CPE_LAST_FAULTS_RQST + 1)
EV_QUERY_CPE_LAST_FAULTS_FAIL   = (EV_QUERY_CPE_LAST_FAULTS_RQST + 2)

EV_QUERY_LAST_SESSION_SOAP_RQST = (EVENT_QUERY_GROUP + 18)
EV_QUERY_LAST_SESSION_SOAP_RSP  = (EV_QUERY_LAST_SESSION_SOAP_RQST + 1)
EV_QUERY_LAST_SESSION_SOAP_FAIL = (EV_QUERY_LAST_SESSION_SOAP_RQST + 2)

EV_QUERY_CPE_INTERFACE_VERSION_RQST = (EVENT_QUERY_GROUP + 21)        
EV_QUERY_CPE_INTERFACE_VERSION_RSP  = (EV_QUERY_CPE_INTERFACE_VERSION_RQST + 1)
EV_QUERY_CPE_INTERFACE_VERSION_FAIL = (EV_QUERY_CPE_INTERFACE_VERSION_RQST + 2)


# --------------------------------------------------worklist------------------
EV_WORKLIST_BUILD_RQST          = (EVENT_WORKLIST_GROUP + 0)    # user build
EV_WORKLIST_BUILD_RSP           = (EV_WORKLIST_BUILD_RQST + 1)
EV_WORKLIST_BUILD_FAIL          = (EV_WORKLIST_BUILD_RQST + 2)

EV_WORKLIST_BIND_PHISIC_RQST    = (EVENT_WORKLIST_GROUP + 3)    # user bind
EV_WORKLIST_BIND_PHISIC_RSP     = (EV_WORKLIST_BIND_PHISIC_RQST + 1)
EV_WORKLIST_BIND_PHISIC_FAIL    = (EV_WORKLIST_BIND_PHISIC_RQST + 2)

EV_WORKLIST_BIND_LOGIC_RQST     = (EVENT_WORKLIST_GROUP + 6)        
EV_WORKLIST_BIND_LOGIC_RSP      = (EV_WORKLIST_BIND_LOGIC_RQST + 1)
EV_WORKLIST_BIND_LOGIC_FAIL     = (EV_WORKLIST_BIND_LOGIC_RQST + 2)

# nwf 2013-05-29; async
EV_WORKLIST_EXECUTE_RQST        = (EVENT_WORKLIST_GROUP + 9)    # user exec
EV_WORKLIST_EXECUTE_RSP         = (EV_WORKLIST_EXECUTE_RQST + 1)
EV_WORKLIST_EXECUTE_FAIL        = (EV_WORKLIST_EXECUTE_RQST + 2)

EV_WORKLIST_RESERVE_RQST        = (EVENT_WORKLIST_GROUP + 12)   # agent reserve
EV_WORKLIST_RESERVE_RSP         = (EV_WORKLIST_RESERVE_RQST + 1)
EV_WORKLIST_RESERVE_FAIL        = (EV_WORKLIST_RESERVE_RQST + 2)

EV_WORKLIST_DOWNLOAD_RQST       = (EVENT_WORKLIST_GROUP + 15)    
EV_WORKLIST_DOWNLOAD_RSP        = (EV_WORKLIST_DOWNLOAD_RQST + 1)
EV_WORKLIST_DOWNLOAD_FAIL       = (EV_WORKLIST_DOWNLOAD_RQST + 2)

#added by wangjun-2013-1-3-14
EV_WORKLIST_EXEC_START_RQST     = (EVENT_WORKLIST_GROUP + 18)           
EV_WORKLIST_EXEC_START_RSP      = (EV_WORKLIST_EXEC_START_RQST + 1)
EV_WORKLIST_EXEC_START_FAIL     = (EV_WORKLIST_EXEC_START_RQST + 2)

EV_WORKLIST_EXEC_FINISH_RQST    = (EVENT_WORKLIST_GROUP + 21)           
EV_WORKLIST_EXEC_FINISH_RSP     = (EV_WORKLIST_EXEC_FINISH_RQST + 1)
EV_WORKLIST_EXEC_FINISH_FAIL    = (EV_WORKLIST_EXEC_FINISH_RQST + 2)

EV_WORKLIST_QUERY_RQST          = (EVENT_WORKLIST_GROUP + 24)           
EV_WORKLIST_QUERY_RSP           = (EV_WORKLIST_QUERY_RQST + 1)
EV_WORKLIST_QUERY_FAIL          = (EV_WORKLIST_QUERY_RQST + 2)

# nwf 2013-05-29; async
EV_WORKLIST_EXECUTE_RSP_RQST    = (EVENT_WORKLIST_GROUP + 27)           
EV_WORKLIST_EXECUTE_RSP_RSP     = (EV_WORKLIST_EXECUTE_RSP_RQST + 1)
EV_WORKLIST_EXECUTE_RSP_FAIL    = (EV_WORKLIST_EXECUTE_RSP_RQST + 2)


# --------------------------------------------------configure------------------
EV_CONFIGURE_USER_INFO_RQST     = (EVENT_CONFIGURE_GROUP + 0)   # user gui configure 
EV_CONFIGURE_USER_INFO_RSP      = (EV_CONFIGURE_USER_INFO_RQST + 1)
EV_CONFIGURE_USER_INFO_FAIL     = (EV_CONFIGURE_USER_INFO_RQST + 2)

EV_MODIFY_CPE_INFO_RQST         = (EVENT_CONFIGURE_GROUP + 3)   # modify cpe info by cmd. added by lana-20121220    
EV_MODIFY_CPE_INFO_RSP          = (EV_MODIFY_CPE_INFO_RQST + 1)
EV_MODIFY_CPE_INFO_FAIL         = (EV_MODIFY_CPE_INFO_RQST + 2)

# monitor or alarm inform
EV_INIT_ALARM_RQST              = (EVENT_CONFIGURE_GROUP + 12)  
EV_INIT_ALARM_RSP               = (EV_INIT_ALARM_RQST + 1)
EV_INIT_ALARM_FAIL              = (EV_INIT_ALARM_RQST + 2)

EV_START_ALARM_RQST             = (EVENT_CONFIGURE_GROUP + 15)  
EV_START_ALARM_RSP              = (EV_START_ALARM_RQST + 1)
EV_START_ALARM_FAIL             = (EV_START_ALARM_RQST + 2)

EV_STOP_ALARM_RQST              = (EVENT_CONFIGURE_GROUP + 18)  
EV_STOP_ALARM_RSP               = (EV_STOP_ALARM_RQST + 1)
EV_STOP_ALARM_FAIL              = (EV_STOP_ALARM_RQST + 2)

EV_GET_ALARM_PARAMETER_RQST     = (EVENT_CONFIGURE_GROUP + 21)  
EV_GET_ALARM_PARAMETER_RSP      = (EV_GET_ALARM_PARAMETER_RQST + 1)
EV_GET_ALARM_PARAMETER_FAIL     = (EV_GET_ALARM_PARAMETER_RQST + 2)

EV_INIT_MONITOR_RQST            = (EVENT_CONFIGURE_GROUP + 24)  
EV_INIT_MONITOR_RSP             = (EV_INIT_MONITOR_RQST + 1)
EV_INIT_MONITOR_FAIL            = (EV_INIT_MONITOR_RQST + 2)

EV_START_MONITOR_RQST           = (EVENT_CONFIGURE_GROUP + 27)  
EV_START_MONITOR_RSP            = (EV_START_MONITOR_RQST + 1)
EV_START_MONITOR_FAIL           = (EV_START_MONITOR_RQST + 2)

EV_STOP_MONITOR_RQST            = (EVENT_CONFIGURE_GROUP + 30)  
EV_STOP_MONITOR_RSP             = (EV_STOP_MONITOR_RQST + 1)
EV_STOP_MONITOR_FAIL            = (EV_STOP_MONITOR_RQST + 2)

EV_GET_MONITOR_PARAMETER_RQST   = (EVENT_CONFIGURE_GROUP + 33)  
EV_GET_MONITOR_PARAMETER_RSP    = (EV_GET_MONITOR_PARAMETER_RQST + 1)
EV_GET_MONITOR_PARAMETER_FAIL   = (EV_GET_MONITOR_PARAMETER_RQST + 2)

EV_QUERY_ALARM_RQST             = (EVENT_CONFIGURE_GROUP + 36)  
EV_QUERY_ALARM_RSP              = (EV_QUERY_ALARM_RQST + 1)
EV_QUERY_ALARM_FAIL             = (EV_QUERY_ALARM_RQST + 2)

EV_QUERY_MONITOR_RQST           = (EVENT_CONFIGURE_GROUP + 39)  
EV_QUERY_MONITOR_RSP            = (EV_QUERY_MONITOR_RQST + 1)
EV_QUERY_MONITOR_FAIL           = (EV_QUERY_MONITOR_RQST + 2)

# wait inform
EV_WAIT_EVENTCODE_INIT_RQST     = (EVENT_CONFIGURE_GROUP + 42)  
EV_WAIT_EVENTCODE_INIT_RSP      = (EV_WAIT_EVENTCODE_INIT_RQST + 1)
EV_WAIT_EVENTCODE_INIT_FAIL     = (EV_WAIT_EVENTCODE_INIT_RQST + 2)

EV_WAIT_EVENTCODE_START_RQST    = (EVENT_CONFIGURE_GROUP + 45)  
EV_WAIT_EVENTCODE_START_RSP     = (EV_WAIT_EVENTCODE_START_RQST + 1)
EV_WAIT_EVENTCODE_START_FAIL    = (EV_WAIT_EVENTCODE_START_RQST + 2)

EV_WAIT_EVENTCODE_STOP_RQST     = (EVENT_CONFIGURE_GROUP + 48)  
EV_WAIT_EVENTCODE_STOP_RSP      = (EV_WAIT_EVENTCODE_STOP_RQST + 1)
EV_WAIT_EVENTCODE_STOP_FAIL     = (EV_WAIT_EVENTCODE_STOP_RQST + 2)

EV_WAIT_EVENTCODE_QUERY_RQST    = (EVENT_CONFIGURE_GROUP + 51)  
EV_WAIT_EVENTCODE_QUERY_RSP     = (EV_WAIT_EVENTCODE_QUERY_RQST + 1)
EV_WAIT_EVENTCODE_QUERY_FAIL    = (EV_WAIT_EVENTCODE_QUERY_RQST + 2)


EV_TR069_ACS_EXIT_RQST          = (EVENT_CONFIGURE_GROUP + 54)  
EV_TR069_ACS_EXIT_RSP           = (EV_TR069_ACS_EXIT_RQST + 1)
EV_TR069_ACS_EXIT_FAIL          = (EV_TR069_ACS_EXIT_RQST + 2)



# ==============================number ----string ==========================
_dict_event = {}
_dict_event[EV_RPC_GETRPCMETHODS_RQST]          = "EV_RPC_GETRPCMETHODS_RQST"
_dict_event[EV_RPC_GETRPCMETHODS_RSP]           = "EV_RPC_GETRPCMETHODS_RSP"
_dict_event[EV_RPC_GETRPCMETHODS_FAIL]          = "EV_RPC_GETRPCMETHODS_FAIL"

_dict_event[EV_RPC_SETPARAMETERVALUES_RQST]     = "EV_RPC_SETPARAMETERVALUES_RQST"
_dict_event[EV_RPC_SETPARAMETERVALUES_RSP]      = "EV_RPC_SETPARAMETERVALUES_RSP"
_dict_event[EV_RPC_SETPARAMETERVALUES_FAIL]     = "EV_RPC_SETPARAMETERVALUES_FAIL"

_dict_event[EV_RPC_GETPARAMETERVALUES_RQST]     = "EV_RPC_GETPARAMETERVALUES_RQST"
_dict_event[EV_RPC_GETPARAMETERVALUES_RSP]      = "EV_RPC_GETPARAMETERVALUES_RSP"
_dict_event[EV_RPC_GETPARAMETERVALUES_FAIL]     = "EV_RPC_GETPARAMETERVALUES_FAIL"

_dict_event[EV_RPC_GETPARAMETERNAMES_RQST]      = "EV_RPC_GETPARAMETERNAMES_RQST"
_dict_event[EV_RPC_GETPARAMETERNAMES_RSP]       = "EV_RPC_GETPARAMETERNAMES_RSP"
_dict_event[EV_RPC_GETPARAMETERNAMES_FAIL]      = "EV_RPC_GETPARAMETERNAMES_FAIL"

_dict_event[EV_RPC_SETPARAMETERATTRIBUTES_RQST] = "EV_RPC_SETPARAMETERATTRIBUTES_RQST"
_dict_event[EV_RPC_SETPARAMETERATTRIBUTES_RSP]  = "EV_RPC_SETPARAMETERATTRIBUTES_RSP"
_dict_event[EV_RPC_SETPARAMETERATTRIBUTES_FAIL] = "EV_RPC_SETPARAMETERATTRIBUTES_FAIL"

_dict_event[EV_RPC_GETPARAMETERATTRIBUTES_RQST] = "EV_RPC_GETPARAMETERATTRIBUTES_RQST"
_dict_event[EV_RPC_GETPARAMETERATTRIBUTES_RSP]  = "EV_RPC_GETPARAMETERATTRIBUTES_RSP"
_dict_event[EV_RPC_GETPARAMETERATTRIBUTES_FAIL] = "EV_RPC_GETPARAMETERATTRIBUTES_FAIL"

_dict_event[EV_RPC_ADDOBJECT_RQST]              = "EV_RPC_ADDOBJECT_RQST"
_dict_event[EV_RPC_ADDOBJECT_RSP]               = "EV_RPC_ADDOBJECT_RSP"
_dict_event[EV_RPC_ADDOBJECT_FAIL]              = "EV_RPC_ADDOBJECT_FAIL"

_dict_event[EV_RPC_DELETEOBJECT_RQST]           = "EV_RPC_DELETEOBJECT_RQST"
_dict_event[EV_RPC_DELETEOBJECT_RSP]            = "EV_RPC_DELETEOBJECT_RSP"
_dict_event[EV_RPC_DELETEOBJECT_FAIL]           = "EV_RPC_DELETEOBJECT_FAIL"

_dict_event[EV_RPC_REBOOT_RQST]                 = "EV_RPC_REBOOT_RQST"
_dict_event[EV_RPC_REBOOT_RSP]                  = "EV_RPC_REBOOT_RSP"
_dict_event[EV_RPC_REBOOT_FAIL]                 = "EV_RPC_REBOOT_FAIL"

_dict_event[EV_RPC_DOWNLOAD_RQST]               = "EV_RPC_DOWNLOAD_RQST"
_dict_event[EV_RPC_DOWNLOAD_RSP]                = "EV_RPC_DOWNLOAD_RSP"
_dict_event[EV_RPC_DOWNLOAD_FAIL]               = "EV_RPC_DOWNLOAD_FAIL"

_dict_event[EV_RPC_UPLOAD_RQST]                 = "EV_RPC_UPLOAD_RQST"
_dict_event[EV_RPC_UPLOAD_RSP]                  = "EV_RPC_UPLOAD_RSP"
_dict_event[EV_RPC_UPLOAD_FAIL]                 = "EV_RPC_UPLOAD_FAIL"

_dict_event[EV_RPC_FACTORYRESET_RQST]           = "EV_RPC_FACTORYRESET_RQST"
_dict_event[EV_RPC_FACTORYRESET_RSP]            = "EV_RPC_FACTORYRESET_RSP"
_dict_event[EV_RPC_FACTORYRESET_FAIL]           = "EV_RPC_FACTORYRESET_FAIL"

_dict_event[EV_RPC_SCHEDULEINFORM_RQST]         = "EV_RPC_SCHEDULEINFORM_RQST"
_dict_event[EV_RPC_SCHEDULEINFORM_RSP]          = "EV_RPC_SCHEDULEINFORM_RSP"
_dict_event[EV_RPC_SCHEDULEINFORM_FAIL]         = "EV_RPC_SCHEDULEINFORM_FAIL"

_dict_event[EV_RPC_GETQUEUEDTRANSFERS_RQST]     = "EV_RPC_GETQUEUEDTRANSFERS_RQST"
_dict_event[EV_RPC_GETQUEUEDTRANSFERS_RSP]      = "EV_RPC_GETQUEUEDTRANSFERS_RSP"
_dict_event[EV_RPC_GETQUEUEDTRANSFERS_FAIL]     = "EV_RPC_GETQUEUEDTRANSFERS_FAIL"

_dict_event[EV_RPC_SETVOUCHERS_RQST]            = "EV_RPC_SETVOUCHERS_RQST"
_dict_event[EV_RPC_SETVOUCHERS_RSP]             = "EV_RPC_SETVOUCHERS_RSP"
_dict_event[EV_RPC_SETVOUCHERS_FAIL]            = "EV_RPC_SETVOUCHERS_FAIL"

_dict_event[EV_RPC_GETOPTIONS_RQST]             = "EV_RPC_GETOPTIONS_RQST"
_dict_event[EV_RPC_GETOPTIONS_RSP]              = "EV_RPC_GETOPTIONS_RSP"
_dict_event[EV_RPC_GETOPTIONS_FAIL]             = "EV_RPC_GETOPTIONS_FAIL"

_dict_event[EV_RPC_GETALLQUEUEDTRANSFERS_RQST]  = "EV_RPC_GETALLQUEUEDTRANSFERS_RQST"
_dict_event[EV_RPC_GETALLQUEUEDTRANSFERS_RSP]   = "EV_RPC_GETALLQUEUEDTRANSFERS_RSP"
_dict_event[EV_RPC_GETALLQUEUEDTRANSFERS_FAIL]  = "EV_RPC_GETALLQUEUEDTRANSFERS_FAIL"

_dict_event[EV_RPC_SCHEDULEDOWNLOAD_RQST]       = "EV_RPC_SCHEDULEDOWNLOAD_RQST"
_dict_event[EV_RPC_SCHEDULEDOWNLOAD_RSP]        = "EV_RPC_SCHEDULEDOWNLOAD_RSP"
_dict_event[EV_RPC_SCHEDULEDOWNLOAD_FAIL]       = "EV_RPC_SCHEDULEDOWNLOAD_FAIL"

_dict_event[EV_RPC_CANCELTRANSFER_RQST]         = "EV_RPC_CANCELTRANSFER_RQST"
_dict_event[EV_RPC_CANCELTRANSFER_RSP]          = "EV_RPC_CANCELTRANSFER_RSP"
_dict_event[EV_RPC_CANCELTRANSFER_FAIL]         = "EV_RPC_CANCELTRANSFER_FAIL"

_dict_event[EV_RPC_CHANGEDUSTATE_RQST]          = "EV_RPC_CHANGEDUSTATE_RQST"
_dict_event[EV_RPC_CHANGEDUSTATE_RSP]           = "EV_RPC_CHANGEDUSTATE_RSP"
_dict_event[EV_RPC_CHANGEDUSTATE_FAIL]          = "EV_RPC_CHANGEDUSTATE_FAIL"


_dict_event[EV_RPC_CONNECTION_REQUEST_RQST]     = "EV_RPC_CONNECTION_REQUEST_RQST"
_dict_event[EV_RPC_CONNECTION_REQUEST_RSP]      = "EV_RPC_CONNECTION_REQUEST_RSP"
_dict_event[EV_RPC_CONNECTION_REQUEST_FAIL]     = "EV_RPC_CONNECTION_REQUEST_FAIL"


_dict_event[EV_RPC_CHECK_RSP]                   = "EV_RPC_CHECK_RSP"
_dict_event[EV_RPC_CHECK_FAIL]                  = "EV_RPC_CHECK_FAIL"

#add by wangjun 20130624
_dict_event[EV_RPC_AGENT_TIMEOUT_POST]          = "EV_RPC_AGENT_TIMEOUT_POST"
_dict_event[EV_RPC_AGENT_TIMEOUT_RSP]           = "EV_RPC_AGENT_TIMEOUT_RSP"

# ------------------------------------query  -----------------------------
_dict_event[EV_QUERY_CPE_INFO_RQST]             = "EV_QUERY_CPE_INFO_RQST"  
_dict_event[EV_QUERY_CPE_INFO_RSP]              = "EV_QUERY_CPE_INFO_RSP"
_dict_event[EV_QUERY_CPE_INFO_FAIL]             = "EV_QUERY_CPE_INFO_FAIL"

_dict_event[EV_QUERY_ONLINE_CPE_RQST]           = "EV_QUERY_ONLINE_CPE_RQST"   
_dict_event[EV_QUERY_ONLINE_CPE_RSP]            = "EV_QUERY_ONLINE_CPE_RSP"
_dict_event[EV_QUERY_ONLINE_CPE_FAIL]           = "EV_QUERY_ONLINE_CPE_FAIL"

_dict_event[EV_QUERY_ALL_ONLINE_CPE_RQST]       = "EV_QUERY_ALL_ONLINE_CPE_RQST"   
_dict_event[EV_QUERY_ALL_ONLINE_CPE_RSP]        = "EV_QUERY_ALL_ONLINE_CPE_RSP"
_dict_event[EV_QUERY_ALL_ONLINE_CPE_FAIL]       = "EV_QUERY_ALL_ONLINE_CPE_FAIL"

_dict_event[EV_QUERY_IS_HANG_RQST]              = "EV_QUERY_IS_HANG_RQST"   
_dict_event[EV_QUERY_IS_HANG_RSP]               = "EV_QUERY_IS_HANG_RSP"
_dict_event[EV_QUERY_IS_HANG_FAIL]              = "EV_QUERY_IS_HANG_FAIL"

_dict_event[EV_QUERY_VERSION_IS_OK_RQST]        = "EV_QUERY_VERSION_IS_OK_RQST"   
_dict_event[EV_QUERY_VERSION_IS_OK_RSP]         = "EV_QUERY_VERSION_IS_OK_RSP"
_dict_event[EV_QUERY_VERSION_IS_OK_FAIL]        = "EV_QUERY_VERSION_IS_OK_FAIL"

_dict_event[EV_QUERY_CPE_LAST_FAULTS_RQST]      = "EV_QUERY_CPE_LAST_FAULTS_RQST"   
_dict_event[EV_QUERY_CPE_LAST_FAULTS_RSP]       = "EV_QUERY_CPE_LAST_FAULTS_RSP"
_dict_event[EV_QUERY_CPE_LAST_FAULTS_FAIL]      = "EV_QUERY_CPE_LAST_FAULTS_FAIL"

_dict_event[EV_QUERY_LAST_SESSION_SOAP_RQST]    = "EV_QUERY_LAST_SESSION_SOAP_RQST"   
_dict_event[EV_QUERY_LAST_SESSION_SOAP_RSP]     = "EV_QUERY_LAST_SESSION_SOAP_RSP"
_dict_event[EV_QUERY_LAST_SESSION_SOAP_FAIL]    = "EV_QUERY_LAST_SESSION_SOAP_FAIL"

_dict_event[EV_QUERY_CPE_INTERFACE_VERSION_RQST]    = "EV_QUERY_CPE_INTERFACE_VERSION_RQST"   
_dict_event[EV_QUERY_CPE_INTERFACE_VERSION_RSP]     = "EV_QUERY_CPE_INTERFACE_VERSION_RSP"
_dict_event[EV_QUERY_CPE_INTERFACE_VERSION_FAIL]    = "EV_QUERY_CPE_INTERFACE_VERSION_FAIL"


# ------------------------------------worklist-----------------------------
_dict_event[EV_WORKLIST_BUILD_RQST]         = "EV_WORKLIST_BUILD_RQST"   
_dict_event[EV_WORKLIST_BUILD_RSP]          = "EV_WORKLIST_BUILD_RSP"
_dict_event[EV_WORKLIST_BUILD_FAIL]         = "EV_WORKLIST_BUILD_FAIL"

_dict_event[EV_WORKLIST_BIND_PHISIC_RQST]   = "EV_WORKLIST_BIND_PHISIC_RQST"   
_dict_event[EV_WORKLIST_BIND_PHISIC_RSP]    = "EV_WORKLIST_BIND_PHISIC_RSP"
_dict_event[EV_WORKLIST_BIND_PHISIC_FAIL]   = "EV_WORKLIST_BIND_PHISIC_FAIL"

_dict_event[EV_WORKLIST_BIND_LOGIC_RQST]    = "EV_WORKLIST_BIND_LOGIC_RQST"   
_dict_event[EV_WORKLIST_BIND_LOGIC_RSP]     = "EV_WORKLIST_BIND_LOGIC_RSP"
_dict_event[EV_WORKLIST_BIND_LOGIC_FAIL]    = "EV_WORKLIST_BIND_LOGIC_FAIL"

_dict_event[EV_WORKLIST_EXECUTE_RQST]       = "EV_WORKLIST_EXECUTE_RQST"
_dict_event[EV_WORKLIST_EXECUTE_RSP]        = "EV_WORKLIST_EXECUTE_RSP"
_dict_event[EV_WORKLIST_EXECUTE_FAIL]       = "EV_WORKLIST_EXECUTE_FAIL"

_dict_event[EV_WORKLIST_RESERVE_RQST]       = "EV_WORKLIST_RESERVE_RQST"
_dict_event[EV_WORKLIST_RESERVE_RSP]        = "EV_WORKLIST_RESERVE_RSP"
_dict_event[EV_WORKLIST_RESERVE_FAIL]       = "EV_WORKLIST_RESERVE_FAIL"

_dict_event[EV_WORKLIST_DOWNLOAD_RQST]      = "EV_WORKLIST_DOWNLOAD_RQST"
_dict_event[EV_WORKLIST_DOWNLOAD_RSP]       = "EV_WORKLIST_DOWNLOAD_RSP"
_dict_event[EV_WORKLIST_DOWNLOAD_FAIL]      = "EV_WORKLIST_DOWNLOAD_FAIL"

#added by wangjun-2013-3-13
_dict_event[EV_WORKLIST_EXEC_START_RQST]    = "EV_WORKLIST_EXEC_START_RQST"
_dict_event[EV_WORKLIST_EXEC_START_RSP]     = "EV_WORKLIST_EXEC_START_RSP"
_dict_event[EV_WORKLIST_EXEC_START_FAIL]    = "EV_WORKLIST_EXEC_START_FAIL"

_dict_event[EV_WORKLIST_EXEC_FINISH_RQST]   = "EV_WORKLIST_EXEC_FINISH_RQST"
_dict_event[EV_WORKLIST_EXEC_FINISH_RSP]    = "EV_WORKLIST_EXEC_FINISH_RSP"
_dict_event[EV_WORKLIST_EXEC_FINISH_FAIL]   = "EV_WORKLIST_EXEC_FINISH_FAIL"

_dict_event[EV_WORKLIST_QUERY_RQST]         = "EV_WORKLIST_QUERY_RQST"
_dict_event[EV_WORKLIST_QUERY_RSP]          = "EV_WORKLIST_QUERY_RSP"
_dict_event[EV_WORKLIST_QUERY_FAIL]         = "EV_WORKLIST_QUERY_FAIL"

_dict_event[EV_WORKLIST_EXECUTE_RSP_RQST]   = "EV_WORKLIST_EXECUTE_RSP_RQST"
_dict_event[EV_WORKLIST_EXECUTE_RSP_RSP]    = "EV_WORKLIST_EXECUTE_RSP_RSP"
_dict_event[EV_WORKLIST_EXECUTE_RSP_FAIL]   = "EV_WORKLIST_EXECUTE_RSP_FAIL"


# ------------------------------------configure-----------------------------
_dict_event[EV_CONFIGURE_USER_INFO_RQST]    = "EV_CONFIGURE_USER_INFO_RQST"
_dict_event[EV_CONFIGURE_USER_INFO_RSP]     = "EV_CONFIGURE_USER_INFO_RSP"


_dict_event[EV_MODIFY_CPE_INFO_RQST]        = "EV_MODIFY_CPE_INFO_RQST"
_dict_event[EV_MODIFY_CPE_INFO_RSP]         = "EV_MODIFY_CPE_INFO_RSP"
_dict_event[EV_MODIFY_CPE_INFO_FAIL]        = "EV_MODIFY_CPE_INFO_FAIL"

# wati eventcode
_dict_event[EV_WAIT_EVENTCODE_INIT_RQST]    = "EV_WAIT_EVENTCODE_INIT_RQST"
_dict_event[EV_WAIT_EVENTCODE_INIT_RSP]     = "EV_WAIT_EVENTCODE_INIT_RSP"
_dict_event[EV_WAIT_EVENTCODE_INIT_FAIL]    = "EV_WAIT_EVENTCODE_INIT_FAIL"
                 
_dict_event[EV_WAIT_EVENTCODE_START_RQST]   = "EV_WAIT_EVENTCODE_START_RQST"
_dict_event[EV_WAIT_EVENTCODE_START_RSP]    = "EV_WAIT_EVENTCODE_START_RSP"
_dict_event[EV_WAIT_EVENTCODE_START_FAIL]   = "EV_WAIT_EVENTCODE_START_FAIL"

_dict_event[EV_WAIT_EVENTCODE_STOP_RQST]    = "EV_WAIT_EVENTCODE_STOP_RQST"
_dict_event[EV_WAIT_EVENTCODE_STOP_RSP]     = "EV_WAIT_EVENTCODE_STOP_RSP"
_dict_event[EV_WAIT_EVENTCODE_STOP_FAIL]    = "EV_WAIT_EVENTCODE_STOP_FAIL"
                 
_dict_event[EV_WAIT_EVENTCODE_QUERY_RQST]   = "EV_WAIT_EVENTCODE_QUERY_RQST"
_dict_event[EV_WAIT_EVENTCODE_QUERY_RSP]    = "EV_WAIT_EVENTCODE_QUERY_RSP"
_dict_event[EV_WAIT_EVENTCODE_QUERY_FAIL]   = "EV_WAIT_EVENTCODE_QUERY_FAIL"

# alarm & monitor
_dict_event[EV_INIT_ALARM_RQST]             = "EV_INIT_ALARM_RQST"
_dict_event[EV_INIT_ALARM_RSP]              = "EV_INIT_ALARM_RSP"
_dict_event[EV_INIT_ALARM_FAIL]             = "EV_INIT_ALARM_FAIL"

_dict_event[EV_START_ALARM_RQST]            = "EV_START_ALARM_RQST"
_dict_event[EV_START_ALARM_RSP]             = "EV_START_ALARM_RSP"
_dict_event[EV_START_ALARM_FAIL]            = "EV_START_ALARM_FAIL"

_dict_event[EV_STOP_ALARM_RQST]             = "EV_STOP_ALARM_RQST"
_dict_event[EV_STOP_ALARM_RSP]              = "EV_STOP_ALARM_RSP"
_dict_event[EV_STOP_ALARM_FAIL]             = "EV_STOP_ALARM_FAIL"

_dict_event[EV_GET_ALARM_PARAMETER_RQST]    = "EV_GET_ALARM_PARAMETER_RQST"
_dict_event[EV_GET_ALARM_PARAMETER_RSP]     = "EV_GET_ALARM_PARAMETER_RSP"
_dict_event[EV_GET_ALARM_PARAMETER_FAIL]    = "EV_GET_ALARM_PARAMETER_FAIL"

_dict_event[EV_INIT_MONITOR_RQST]           = "EV_INIT_MONITOR_RQST"
_dict_event[EV_INIT_MONITOR_RSP]            = "EV_INIT_MONITOR_RSP"
_dict_event[EV_INIT_MONITOR_FAIL]           = "EV_INIT_MONITOR_FAIL"

_dict_event[EV_START_MONITOR_RQST]          = "EV_START_MONITOR_RQST"
_dict_event[EV_START_MONITOR_RSP]           = "EV_START_MONITOR_RSP"
_dict_event[EV_START_MONITOR_FAIL]          = "EV_START_MONITOR_FAIL"

_dict_event[EV_STOP_MONITOR_RQST]           = "EV_STOP_MONITOR_RQST"
_dict_event[EV_STOP_MONITOR_RSP]            = "EV_STOP_MONITOR_RSP"
_dict_event[EV_STOP_MONITOR_FAIL]           = "EV_STOP_MONITOR_FAIL"

_dict_event[EV_GET_MONITOR_PARAMETER_RQST]  = "EV_GET_MONITOR_PARAMETER_RQST"
_dict_event[EV_GET_MONITOR_PARAMETER_RSP]   = "EV_GET_MONITOR_PARAMETER_RSP"
_dict_event[EV_GET_MONITOR_PARAMETER_FAIL]  = "EV_GET_MONITOR_PARAMETER_FAIL"

_dict_event[EV_QUERY_ALARM_RQST]            = "EV_QUERY_ALARM_RQST"
_dict_event[EV_QUERY_ALARM_RSP]             = "EV_QUERY_ALARM_RSP"
_dict_event[EV_QUERY_ALARM_FAIL]            = "EV_QUERY_ALARM_FAIL"

_dict_event[EV_QUERY_MONITOR_RQST]          = "EV_QUERY_MONITOR_RQST"
_dict_event[EV_QUERY_MONITOR_RSP]           = "EV_QUERY_MONITOR_RSP"
_dict_event[EV_QUERY_MONITOR_FAIL]          = "EV_QUERY_MONITOR_FAIL"

# acs exit
_dict_event[EV_TR069_ACS_EXIT_RQST]          = "EV_TR069_ACS_EXIT_RQST"
_dict_event[EV_TR069_ACS_EXIT_RSP]           = "EV_TR069_ACS_EXIT_RSP"
_dict_event[EV_TR069_ACS_EXIT_FAIL]          = "EV_TR069_ACS_EXIT_FAIL"



# -----------------------------------------------global -----------------
# for database select rpc
g_support_rpc_names = [ "AddObject",
                        "CancelTransfer",
                        "ChangeDUState",
                        "DeleteObject",
                        "Download",
                        "FactoryReset",
                        "GetAllQueuedTransfers",
                        "GetOptions",
                        "GetParameterAttributes",
                        "GetRPCMethods", 
                        
                        "GetParameterValues", 
                        "GetParameterNames",
                        "GetQueuedTransfers", 
                        "Reboot",
                        "ScheduleDownload",
                        "ScheduleInform", 
                        "SetParameterAttributes",
                        "SetParameterValues", 
                        "SetVouchers",
                        "Upload"
                        
                        ]

# import rpc
# nwf 2013-10-28; connection_request, behave like rpc
dict_rpc_event = {"GetRPCMethods":          EV_RPC_GETRPCMETHODS_RQST,
                  "SetParameterValues":     EV_RPC_SETPARAMETERVALUES_RQST,
                  "GetParameterValues":     EV_RPC_GETPARAMETERVALUES_RQST,
                  "GetParameterNames":      EV_RPC_GETPARAMETERNAMES_RQST,
                  "SetParameterAttributes": EV_RPC_SETPARAMETERATTRIBUTES_RQST,
                  "GetParameterAttributes": EV_RPC_GETPARAMETERATTRIBUTES_RQST,
                  "AddObject":              EV_RPC_ADDOBJECT_RQST,
                  "DeleteObject":           EV_RPC_DELETEOBJECT_RQST,
                  "Reboot":                 EV_RPC_REBOOT_RQST,
                  "Download":               EV_RPC_DOWNLOAD_RQST,
                  "Upload":                 EV_RPC_UPLOAD_RQST,
                  "FactoryReset":           EV_RPC_FACTORYRESET_RQST,
                  "ScheduleInform":         EV_RPC_SCHEDULEINFORM_RQST,
                  "GetQueuedTransfers":     EV_RPC_GETQUEUEDTRANSFERS_RQST,
                  "SetVouchers":            EV_RPC_SETVOUCHERS_RQST,
                  "GetOptions":             EV_RPC_GETOPTIONS_RQST,
                  "GetAllQueuedTransfers":  EV_RPC_GETALLQUEUEDTRANSFERS_RQST,
                  "ScheduleDownload":       EV_RPC_SCHEDULEDOWNLOAD_RQST,
                  "CancelTransfer":         EV_RPC_CANCELTRANSFER_RQST,
                  "ChangeDUState":          EV_RPC_CHANGEDUSTATE_RQST,
                  "connection_request":     EV_RPC_CONNECTION_REQUEST_RQST,                  
              }              

#add by wangjun-2013-3-15
dict_workprocess_event = {"MsgWorklistBuild":           EV_WORKLIST_BUILD_RQST,
                          "MsgWorklistBindPhysical":    EV_WORKLIST_BIND_PHISIC_RQST,
                          "MsgWorklistBindLogical":     EV_WORKLIST_BIND_LOGIC_RQST,
                          "MsgWorklistExecute":         EV_WORKLIST_EXECUTE_RQST,
                          "MsgWorklistQuery":           EV_WORKLIST_QUERY_RQST,
                          "MsgWorklistDownload":        EV_WORKLIST_DOWNLOAD_RQST
                         }

dict_workprocess_obj = {"MsgWorklistBuild":             MsgWorklistBuild,
                          "MsgWorklistBindPhysical":    MsgWorklistBindPhysical,
                          "MsgWorklistBindLogical":     MsgWorklistBindLogical,
                          "MsgWorklistExecute":         MsgWorklistExecute,
                          "MsgWorklistQuery":           MsgWorklistQuery,
                          "MsgWorklistDownload":        MsgWorklistDownload
                         }
                         

def get_event_desc(event):
    ret = ""
    
    if (event is None):
        ret = ""
    else:
        ret = _dict_event.get(int(event))
        if (ret is None):
            ret = "unknown event(%s)" %(event)
    return ret

# global 
__all__ = [ "KEY_MESSAGE",
            "KEY_OBJECT",
            "KEY_SN", 
            "KEY_MESSAGE_TYPE", 
            "KEY_SEQUENCE",
            
            "KEY_SENDER", 
            "KEY_SENDER_USER", 
            "KEY_SENDER_WORKLIST", 
            "KEY_SENDER_ACS",    

            "KEY_QUEUE", 
            "QUEUE_INIT", 
            "QUEUE_WAIT",              
            
            "MsgUserRpc",
            "MsgUserRpcCheck", 
            "MsgRpcTimeout", 
            
            "MsgQueryCPEOnline",            
            "MsgQueryCPEInfo", 
            "MsgQueryCPEInterfaceVersion", 
            "MsgQueryIsHang",
            "MsgQueryVersionIsOk",
            "MsgQueryLastSessionSoap",

            "MsgWorklistBuild", 
            "MsgWorklistBindPhysical", 
            "MsgWorklistBindLogical", 
            "MsgWorklist", 
            "MsgWorklistExecute", 
            "MsgWorklistExecStart",
            "MsgWorklistExecFinish", 
            "MsgWorklistExecRsp", 
            "MsgWorklistReserve",
            "MsgWorklistDownload",
            "MsgWorklistCpeInterfaceVersion", 
            "MsgWorklistQuery", 
            "MsgWorklistDomain",            
            "MsgWorklistFile", 
            
            "MsgConfig",
            "MsgModifyCPEInfo",
            "MsgWaitEventCode", 
            "MsgAlarmInform",
            "MsgMonitorInform",

            "MsgTR069Close",         
            "MsgQueryCpeLastFaults",
            
            "get_event_desc", 
            "dict_rpc_event", 
            "dict_workprocess_obj", 
            "dict_workprocess_event", 
            "g_support_rpc_names",

            "EVENT_RPC_GROUP",
            "EVENT_QUERY_GROUP",
            "EVENT_WORKLIST_GROUP",
            "EVENT_CONFIGURE_GROUP", 
            
           
            "EV_RPC_GETRPCMETHODS_RQST",
            "EV_RPC_GETRPCMETHODS_RSP",
            "EV_RPC_GETRPCMETHODS_FAIL",
           
            "EV_RPC_SETPARAMETERVALUES_RQST",
            "EV_RPC_SETPARAMETERVALUES_RSP",
            "EV_RPC_SETPARAMETERVALUES_FAIL",
           
            "EV_RPC_GETPARAMETERVALUES_RQST",
            "EV_RPC_GETPARAMETERVALUES_RSP",
            "EV_RPC_GETPARAMETERVALUES_FAIL",
           
            "EV_RPC_GETPARAMETERNAMES_RQST",
            "EV_RPC_GETPARAMETERNAMES_RSP", 
            "EV_RPC_GETPARAMETERNAMES_FAIL",
           
            "EV_RPC_SETPARAMETERATTRIBUTES_RQST",
            "EV_RPC_SETPARAMETERATTRIBUTES_RSP",
            "EV_RPC_SETPARAMETERATTRIBUTES_FAIL",
           
            "EV_RPC_GETPARAMETERATTRIBUTES_RQST",
            "EV_RPC_GETPARAMETERATTRIBUTES_RSP",
            "EV_RPC_GETPARAMETERATTRIBUTES_FAIL",
           
            "EV_RPC_ADDOBJECT_RQST",
            "EV_RPC_ADDOBJECT_RSP",
            "EV_RPC_ADDOBJECT_FAIL",
           
            "EV_RPC_DELETEOBJECT_RQST",
            "EV_RPC_DELETEOBJECT_RSP",
            "EV_RPC_DELETEOBJECT_FAIL",
           
            "EV_RPC_REBOOT_RQST",
            "EV_RPC_REBOOT_RSP",
            "EV_RPC_REBOOT_FAIL",
           
            "EV_RPC_DOWNLOAD_RQST",
            "EV_RPC_DOWNLOAD_RSP",
            "EV_RPC_DOWNLOAD_FAIL",
           
            "EV_RPC_UPLOAD_RQST",
            "EV_RPC_UPLOAD_RSP",
            "EV_RPC_UPLOAD_FAIL",
           
            "EV_RPC_FACTORYRESET_RQST",
            "EV_RPC_FACTORYRESET_RSP",
            "EV_RPC_FACTORYRESET_FAIL",
           
            "EV_RPC_SCHEDULEINFORM_RQST",
            "EV_RPC_SCHEDULEINFORM_RSP",
            "EV_RPC_SCHEDULEINFORM_FAIL",
           
            "EV_RPC_GETQUEUEDTRANSFERS_RQST",
            "EV_RPC_GETQUEUEDTRANSFERS_RSP",
            "EV_RPC_GETQUEUEDTRANSFERS_FAIL",
           
            "EV_RPC_SETVOUCHERS_RQST",
            "EV_RPC_SETVOUCHERS_RSP",
            "EV_RPC_SETVOUCHERS_FAIL",
           
            "EV_RPC_GETOPTIONS_RQST",
            "EV_RPC_GETOPTIONS_RSP",
            "EV_RPC_GETOPTIONS_FAIL",
           
            "EV_RPC_GETALLQUEUEDTRANSFERS_RQST",
            "EV_RPC_GETALLQUEUEDTRANSFERS_RSP",
            "EV_RPC_GETALLQUEUEDTRANSFERS_FAIL",
           
            "EV_RPC_SCHEDULEDOWNLOAD_RQST",
            "EV_RPC_SCHEDULEDOWNLOAD_RSP",
            "EV_RPC_SCHEDULEDOWNLOAD_FAIL",

            "EV_RPC_CANCELTRANSFER_RQST",
            "EV_RPC_CANCELTRANSFER_RSP",
            "EV_RPC_CANCELTRANSFER_FAIL",

            "EV_RPC_CHANGEDUSTATE_RQST",
            "EV_RPC_CHANGEDUSTATE_RSP",
            "EV_RPC_CHANGEDUSTATE_FAIL", 

            "EV_RPC_CONNECTION_REQUEST_RQST",
            "EV_RPC_CONNECTION_REQUEST_RSP",
            "EV_RPC_CONNECTION_REQUEST_FAIL",            

            "EV_RPC_CHECK_RSP", 
            "EV_RPC_CHECK_FAIL",                       

            "EV_RPC_AGENT_TIMEOUT_POST", 
            "EV_RPC_AGENT_TIMEOUT_RSP", 


            "EV_QUERY_ONLINE_CPE_RQST",
            "EV_QUERY_ONLINE_CPE_RSP",
            "EV_QUERY_ONLINE_CPE_FAIL",

            "EV_QUERY_ALL_ONLINE_CPE_RQST", 
            "EV_QUERY_ALL_ONLINE_CPE_RSP", 
            "EV_QUERY_ALL_ONLINE_CPE_FAIL",            

            "EV_QUERY_CPE_INFO_RQST",
            "EV_QUERY_CPE_INFO_RSP",
            "EV_QUERY_CPE_INFO_FAIL", 

            "EV_QUERY_CPE_INTERFACE_VERSION_RQST", 
            "EV_QUERY_CPE_INTERFACE_VERSION_RSP", 
            "EV_QUERY_CPE_INTERFACE_VERSION_FAIL", 
            
            "EV_QUERY_IS_HANG_RQST",  
            "EV_QUERY_IS_HANG_RSP", 
            "EV_QUERY_IS_HANG_FAIL",  

            "EV_QUERY_VERSION_IS_OK_RQST",
            "EV_QUERY_VERSION_IS_OK_RSP",
            "EV_QUERY_VERSION_IS_OK_FAIL",
            
            "EV_QUERY_CPE_LAST_FAULTS_RQST",
            "EV_QUERY_CPE_LAST_FAULTS_RSP",
            "EV_QUERY_CPE_LAST_FAULTS_FAIL",

            "EV_QUERY_LAST_SESSION_SOAP_RQST",
            "EV_QUERY_LAST_SESSION_SOAP_RSP",
            "EV_QUERY_LAST_SESSION_SOAP_FAIL",

            "WORK_LIST_TYPE_PHISIC",
            "WORK_LIST_TYPE_LOGIC",
            
            "WORK_LIST_STATUS_BUILD",
            "WORK_LIST_STATUS_BIND", 
            "WORK_LIST_STATUS_RESERVE",
            "WORK_LIST_STATUS_RUNNING",
            "WORK_LIST_STATUS_SUCCESS",
            "WORK_LIST_STATUS_FAIL",
            "WORK_LIST_STATUS_ABNORMAL",
            "WORK_LIST_STATUS_EXPIRE",
            
            "EV_WORKLIST_BUILD_RQST",
            "EV_WORKLIST_BUILD_RSP",
            "EV_WORKLIST_BUILD_FAIL",
            
            "EV_WORKLIST_BIND_PHISIC_RQST",
            "EV_WORKLIST_BIND_PHISIC_RSP",
            "EV_WORKLIST_BIND_PHISIC_FAIL",
            
            "EV_WORKLIST_BIND_LOGIC_RQST",
            "EV_WORKLIST_BIND_LOGIC_RSP",
            "EV_WORKLIST_BIND_LOGIC_FAIL",    

            "EV_WORKLIST_EXECUTE_RQST",
            "EV_WORKLIST_EXECUTE_RSP",
            "EV_WORKLIST_EXECUTE_FAIL",
            
            "EV_WORKLIST_RESERVE_RQST",
            "EV_WORKLIST_RESERVE_RSP",
            "EV_WORKLIST_RESERVE_FAIL",              
            
            "EV_WORKLIST_DOWNLOAD_RQST",
            "EV_WORKLIST_DOWNLOAD_RSP",
            "EV_WORKLIST_DOWNLOAD_FAIL",
            
            "EV_WORKLIST_EXEC_START_RQST",
            "EV_WORKLIST_EXEC_START_RSP",
            "EV_WORKLIST_EXEC_START_FAIL",

            "EV_WORKLIST_EXEC_FINISH_RQST",
            "EV_WORKLIST_EXEC_FINISH_RSP",
            "EV_WORKLIST_EXEC_FINISH_FAIL",  

            "EV_WORKLIST_QUERY_RQST",
            "EV_WORKLIST_QUERY_RSP",
            "EV_WORKLIST_QUERY_FAIL",
            
            "EV_WORKLIST_EXECUTE_RSP_RQST",
            "EV_WORKLIST_EXECUTE_RSP_RSP",
            

            "EV_CONFIGURE_USER_INFO_RQST", 
            "EV_CONFIGURE_USER_INFO_RSP", 
            "EV_CONFIGURE_USER_INFO_FAIL",
            
            "EV_MODIFY_CPE_INFO_RQST",
            "EV_MODIFY_CPE_INFO_RSP",
            "EV_MODIFY_CPE_INFO_FAIL",

            "EV_WAIT_EVENTCODE_INIT_RQST",  
            "EV_WAIT_EVENTCODE_INIT_RSP", 
            "EV_WAIT_EVENTCODE_INIT_FAIL", 

            "EV_WAIT_EVENTCODE_START_RQST", 
            "EV_WAIT_EVENTCODE_START_RSP",
            "EV_WAIT_EVENTCODE_START_FAIL",

            "EV_WAIT_EVENTCODE_STOP_RQST", 
            "EV_WAIT_EVENTCODE_STOP_RSP", 
            "EV_WAIT_EVENTCODE_STOP_FAIL",           

            "EV_WAIT_EVENTCODE_QUERY_RQST", 
            "EV_WAIT_EVENTCODE_QUERY_RSP",
            "EV_WAIT_EVENTCODE_QUERY_FAIL",   


            "EV_INIT_ALARM_RQST", 
            "EV_INIT_ALARM_RSP", 
            "EV_INIT_ALARM_FAIL", 
            
            "EV_START_ALARM_RQST", 
            "EV_START_ALARM_RSP", 
            "EV_START_ALARM_FAIL", 

            "EV_STOP_ALARM_RQST", 
            "EV_STOP_ALARM_RSP", 
            "EV_STOP_ALARM_FAIL", 

            "EV_GET_ALARM_PARAMETER_RQST", 
            "EV_GET_ALARM_PARAMETER_RSP", 
            "EV_GET_ALARM_PARAMETER_FAIL", 

            "EV_INIT_MONITOR_RQST", 
            "EV_INIT_MONITOR_RSP", 
            "EV_INIT_MONITOR_FAIL", 
            
            "EV_START_MONITOR_RQST", 
            "EV_START_MONITOR_RSP", 
            "EV_START_MONITOR_FAIL", 

            "EV_STOP_MONITOR_RQST", 
            "EV_STOP_MONITOR_RSP", 
            "EV_STOP_MONITOR_FAIL", 

            "EV_GET_MONITOR_PARAMETER_RQST", 
            "EV_GET_MONITOR_PARAMETER_RSP", 
            "EV_GET_MONITOR_PARAMETER_FAIL",

            "EV_QUERY_ALARM_RQST",
            "EV_QUERY_ALARM_RSP",
            "EV_QUERY_ALARM_FAIL",

            "EV_QUERY_MONITOR_RQST",
            "EV_QUERY_MONITOR_RSP",
            "EV_QUERY_MONITOR_FAIL",

            "EV_TR069_ACS_EXIT_RQST", 
            "EV_TR069_ACS_EXIT_RSP",
            "EV_TR069_ACS_EXIT_FAIL",
            

            "MONITOR_INFORM_STATUS_INIT",
            "MONITOR_INFORM_STATUS_START_BEGIN",
            "MONITOR_INFORM_STATUS_START_SUCCESS",
            "MONITOR_INFORM_STATUS_START_FAIL",
            "MONITOR_INFORM_STATUS_STOP_BEGIN",  
            "MONITOR_INFORM_STATUS_STOP_SUCCESS", 
            "MONITOR_INFORM_STATUS_STOP_FAIL", 


           ]
