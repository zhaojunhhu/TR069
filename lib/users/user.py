# coding:utf-8

# ***************************************************************************
#
#  nwf      2013-05-25      refactor(unify)
# ***************************************************************************


import  time
import  os
import  sys
from    os.path     import dirname


import  usercmd
from    TR069.lib.common.function   import print_trace
from    TR069.lib.common.error      import *
from    TR069.lib.common.event      import *
import  TR069.lib.common.config     as config
import  TR069.lib.users.usercfg          as usercfg 
from    TR069.lib.common.releasecfg       import *   # for tr069 self or RF?
     

# --------------------------------------------------------------
class UserRpc():
    """
    
    """
    
    def __init__(self, sn, rpc_name="", dict_args={}, ip="", port="", page="", sender="", worklist_id=""):
        self.sn             = sn
        
        self.rpc_name       = rpc_name
        self.dict_args      = dict_args
        
        # nwf 2013-06-03
        self.ip             = ip 
        self.port           = port
        self.page           = page
        
        self.sender         = sender
        self.worklist_id    = worklist_id   # nwf 2013-09-16


    def add_object(self, **args):
        """
        This method MAY be used by the ACS to create a new instance of a multi instance 
        object a collection of Parameters and/or other objects for which multiple instances are 
        defined
        """
        self.rpc_name = "AddObject"
        self.dict_args = args
        
        return self.process_rpc()
               
        
    def cancel_transfer(self, **args):
        """
        This method MAY be used by the ACS to cause the CPE to cancel a file transfer initiated 
        by an earlier Download, ScheduleDownload or Upload method call. The TransferComplete method is
        not called for a file transfer that has successfully been canceled.
        This method have one argument,the type is string.

        """
        self.rpc_name = "CancelTransfer"
        self.dict_args = args        
        
        return self.process_rpc()


    def change_du_state(self, **args):
        """
        This method MAY be used by an ACS to trigger the explicit state transitions of
        Install, Update, and Uninstall for a Deployment Unit (DU), i.e. installing a new DU,
        updating an existing DU, or uninstalling an existing DU.
        This method have two argument,first type is OperationStruct[], second is string.
        """
        self.rpc_name = "ChangeDUState"
        self.dict_args = args        
        
        return self.process_rpc()
        

    def delete_object(self, **args):
        """
        This method is used to remove a particular instance of an object.  This method call takes 
        as an argument the path name of the object instance including the instance number.
        This method have two arguments, they type are string.
        """
        self.rpc_name = "DeleteObject"
        self.dict_args = args        
        
        return self.process_rpc()
        

    def download(self, **args):
        """
        This method MAY be used by the ACS to cause the CPE to download a specified file 
        from the designated location.
        This method have one arguments ,the type is dict.
        """
        self.rpc_name = "Download"
        self.dict_args = args        
        
        return self.process_rpc()
        

    def factory_reset(self):
        """
        This method resets the CPE to its factory default state, and calls for use
        with extreme caution. The CPE MUST initiate the factory reset procedure only after
        successful completion of the session.
        This method have no parameter.
        """
        self.rpc_name = "FactoryReset"
        self.dict_args = {}        
        
        return self.process_rpc()

        
    def get_all_queued_transfers(self, **args):
        """
        This method MAY be used by an ACS to determine the status of all queued
        downloads and uploads, including any that were not specifically requested by the
        ACS, i.e. autonomous transfers.
        This method have no parameter.
        """
        self.rpc_name = "GetAllQueuedTransfers"
        self.dict_args = args        
        
        return self.process_rpc()
        

    def get_options(self, **args):
        """
        This method MAY be used by an ACS to obtain a list of the options currently
        set in a CPE, and their associated state information.
        This method have one argument,the type is string.
        """
        self.rpc_name = "GetOptions"
        self.dict_args = args        
        
        return self.process_rpc()
        

    def get_queued_transfers(self, **args):
        """
        This method MAY be used by an ACS to determine the status of previously requested 
        downloads or uploads.
        This method have no parameter.
        """
        self.rpc_name = "GetQueuedTransfers"
        self.dict_args = args        
        
        return self.process_rpc()
        
        
    def get_rpc_methods(self):
        """
        This method MAY be used by a CPE or ACS to discover the set of methods
        supported by the ACS or CPE it is in communication with.
        This list MUST include all the supported methods, both standard methods
        and vendor-specific methods.

        return = (ret, str_data)
        """
        self.rpc_name = "GetRPCMethods"
        self.dict_args = {}        
        
        return self.process_rpc()

            
    def get_parameter_attributes(self, **args):
        """
        This method MAY be used by an ACS to read the attributes associated with
        one or more CPE Parameter.
        This method have one arguments ,the type is string.
        """
        self.rpc_name = "GetParameterAttributes"
        self.dict_args = args        
        
        return self.process_rpc()

                
    def get_parameter_names(self, **args):
        """
        This method MAY be used by an ACS to discover the Parameters accessible on a 
        particular CPE.
        This method have two arguments ,first type sting ,second boolean.
        """
        self.rpc_name = "GetParameterNames"
        self.dict_args = args        
        
        return self.process_rpc()                                 
        
                          
    def get_parameter_values(self, **args):
        """
        This method MAY be used by an ACS to obtain the value of one or more CPE 
        Parameters.
        This method have one arguments,the type is list .
        """
        self.rpc_name = "GetParameterValues"
        self.dict_args = args        
                
        return self.process_rpc()

        
    def reboot(self, **args):
        """
        This method causes the CPE to reboot, and calls for use of extreme caution.  The CPE 
        MUST send the method response and complete the remainder of the session prior to rebooting.
        This method have one arguments ,the type is string.
        """
        self.rpc_name = "Reboot"
        self.dict_args = args        
        
        return self.process_rpc()                        

        
    def  schedule_inform(self,  **args):
        """
        This method MAY be used by an ACS to request the CPE to schedule a one-time Inform 
        method call (separate from its periodic Inform method calls) sometime in the future.
        This method have two arguments ,first type is unsignedInt,second string
        """
        self.rpc_name = "ScheduleInform"
        self.dict_args = args        
        
        return self.process_rpc()
        

    def schedule_download(self, **args):
        """
        This method MAY be used by the ACS to cause the CPE to download a specified file 
        from the designated location and apply it within either one or two specified time windows.
        The CPE MUST support two time windows.
        This method have eight arguments ,they type are string(32),string(64),string(256),
        string(256),string(256),unsignedInt,string(256),TimeWin-dowStr-uct[1:2].
        """
        self.rpc_name = "ScheduleDownload"
        self.dict_args = args        
        
        return self.process_rpc()                             


    def set_parameter_attributes(self, **args):
        """
        This method MAY be used by an ACS to modify attributes associated with
        one or more CPE Parameter.
        This method have one arguments,the type is SetParameterAttributesStruct.
        
        t(ParameterList=[dict(name='ksdjf',ljfls='gjd'),dict(name='dkjf')])
        """
        self.rpc_name ="SetParameterAttributes"
        self.dict_args = args        
        
        return self.process_rpc()


    def set_parameter_values(self, **args):
        """
        This method MAY be used by an ACS to modify the value of one or more CPE
        Parameters.
        This method have two arguments, first type ParameterValueStruct,other type string .
        """
        self.rpc_name = "SetParameterValues"
        self.dict_args = args        
        
        return self.process_rpc()
    

    def set_vouchers(self, **args):
        """
        This method MAY be used by an ACS to set one or more option Vouchers in the CPE.
        This method have one argument,the type is baiss64[]
        """
        self.rpc_name = "SetVouchers"
        self.dict_args = args        
        
        return self.process_rpc()   


    def upload(self, **args):
        """
        This method MAY be used by the ACS to cause the CPE to upload a specified
        file to the designated location.
        This method have six arguments ,The type is dict.
        """
        self.rpc_name = "Upload"
        self.dict_args = args        
        
        return self.process_rpc()
              

    def connection_request(self):
        """
        """
        self.rpc_name = "connection_request"
        self.dict_args = {}        
        
        return self.process_rpc()


    def process_rpc(self):
        """
        """
        ret         = ERR_FAIL
        str_data    = ""

        usercmd1 = usercmd.Usercmd(self.ip, self.port, self.page, self.sender, self.worklist_id)
        
        ret, str_data = usercmd1.process_rpc(self.sn, self.rpc_name, self.dict_args)

        return ret, str_data
        
    
# --------------------------------------------------------------
class UserWorklist():
    
    def __init__(self, cmd="", dict_args={}):
        self.cmd = cmd
        self.args = dict_args    


    def worklistprocess_build(self, **args):
        """
        """
        
        self.cmd = "MsgWorklistBuild"
        self.args = args
        
        return self.process_worklist() 
      
        
    def worklistprocess_bind_physical(self, **args):
        """
        """
        
        self.cmd = "MsgWorklistBindPhysical"
        self.args = args
        
        return self.process_worklist() 
    
    
    def worklistprocess_bind_logical(self, **args):
        """
        """
        
        self.cmd = "MsgWorklistBindLogical"
        self.args = args
        
        return self.process_worklist()
    
    
    def worklistprocess_execute(self, **args):
        """
        """

        self.cmd = "MsgWorklistExecute"
        self.args = args
                
        return self.process_worklist_exec()
    
    
    def worklistprocess_query(self, **args):
        """
        """
        
        self.cmd = "MsgWorklistQuery"
        self.args = args
        
        return self.process_worklist()
    
    
    def worklistprocess_download(self, **args):
        """
        """
        
        self.cmd = "MsgWorklistDownload"
        self.args = args
        
        return self.process_worklist()
    
        ret, data = self.process_worklist()
        if ret == ERR_FAIL:
            return ret, data
        return self._parse_worklist_data(data)    
    

    def process_worklist(self):
        """
        """
        ret         = ERR_FAIL
        str_data    = ""

        usercmd1 = usercmd.Usercmd()
        
        ret, str_data = usercmd1.process_worklist(self.cmd, self.args)

        return ret, str_data


    def process_worklist_exec(self):
        """
        """
        ret         = ERR_FAIL
        str_data    = ""

        usercmd1 = usercmd.Usercmd()
        
        ret, str_data = usercmd1.process_worklist_exec(self.cmd, self.args)

        return ret, str_data

    
    def _parse_worklist_data(self,worklist_download_obj):
        """
        """
        ret         = ERR_SUCCESS
        str_ret    = ""
        
        list_worklist_data = worklist_download_obj.domains
        list_worklist_domains = []
        try:
            for type_worklist in list_worklist_data:
                
                type_name = type_worklist.name
                list_worklist = type_worklist.wl_datafiles
                
                list_worklist_temp = []
                for worklist in list_worklist:
                    worklist_name = worklist.name
                    dict_args = worklist.dict_data
                    
                    list_temp = []
                    for args_name, tuple_args in dict_args.items():
                        list_data = [tuple_args[1], tuple_args[0], args_name]
                        list_temp.append(list_data)
                    
                    list_temp.sort()
                    list_worklist_temp.append((worklist_name,list_temp))      
                list_worklist_domains.append((type_name,list_worklist_temp))
        except Exception,e:
            str_ret = u"解析工单数据失败，详细信息：%s" % e
            return  ERR_FAIL,str_ret
        return ret, list_worklist_domains        


# --------------------------------------------------------------        
def config_remote_address(ip="" , port=""):
    """
    config agent http ip+port
    """
    ret         = ERR_FAIL
    str_data    = ""

    usercfg.AGENT_HTTP_IP       = ip
    usercfg.AGENT_HTTP_PORT     = port

    # new stragety        
    return query_version_is_ok()
   
   
def get_online_cpe(sn=""):
    """
    """
    ret         = ERR_FAIL
    str_data    = ""
    
    usercmd1 = usercmd.Usercmd()
    
    ret, str_data = usercmd1.process_get_online_cpe(sn)
            
    return ret, str_data


def query_cpe_info(sn="", from_gui_request_flag=False):
    """
    
    """
    
    ret         = ERR_FAIL
    str_data    = ""

    usercmd1 = usercmd.Usercmd()
    if from_gui_request_flag:
        usercmd1.set_request_source_from_tr069gui()
    
    ret, str_data = usercmd1.process_query_cpe_info(sn)
            
    return ret, str_data


def update_cpe_info(sn="", dict_item={}, from_gui_request_flag=False):
    """
    """
    
    ret         = ERR_FAIL
    str_data    = ""

    usercmd1 = usercmd.Usercmd()
    if from_gui_request_flag:
        usercmd1.set_request_source_from_tr069gui()
        
    ret, str_data = usercmd1.process_update_cpe_info(sn, dict_item)
            
    return ret, str_data


# --------------------------------------------------------------  
def wait_next_inform(sn, timeout):
    """
    customize user api
    """
    
    ret             = ERR_FAIL
    str_data        = ""
    ret_obj         = None  # event obj
    ret_out         = ""    # RF ret      

    for nwf in [1]:
    
        ret, str_data = init_wait_eventcode(sn, ["any_eventcode"], [])
        if (ret != ERR_SUCCESS):
            break
        ret_obj = str_data
        wait_eventcode_id = ret_obj.id_
            
        ret, str_data = start_wait_eventcode(sn, wait_eventcode_id)
        if (ret != ERR_SUCCESS):
            break

        ret, str_data = query_wait_eventcode(sn, wait_eventcode_id, timeout)
        if (ret != ERR_SUCCESS):
            break                    
    
        stop_wait_eventcode(sn, wait_eventcode_id)
            
    return ret, str_data


def init_wait_eventcode(sn, include_eventcodes, exclude_eventcodes):
    """
    """
    
    ret         = ERR_FAIL
    str_data    = ""

    usercmd1 = usercmd.Usercmd()
    
    ret, str_data = usercmd1.process_init_wait_eventcode(sn, include_eventcodes, exclude_eventcodes)
            
    return ret, str_data    


def start_wait_eventcode(sn, wait_eventcode_id):
    """
    """
    
    ret         = ERR_FAIL
    str_data    = ""

    usercmd1 = usercmd.Usercmd()
    
    ret, str_data = usercmd1.process_start_wait_eventcode(sn, wait_eventcode_id)
            
    return ret, str_data  


def check_result_and_stop_wait_eventcode(sn, wait_eventcode_id, timeout):
    """
    customize user api
    """
    
    ret         = ERR_FAIL
    str_data    = ""
    
    ret, str_data = query_wait_eventcode(sn, wait_eventcode_id, timeout)

    stop_wait_eventcode(sn, wait_eventcode_id)
            
    return ret, str_data 

    
def stop_wait_eventcode(sn, wait_eventcode_id):
    """
    """
    
    ret         = ERR_FAIL
    str_data    = ""

    usercmd1 = usercmd.Usercmd()
    
    ret, str_data = usercmd1.process_stop_wait_eventcode(sn, wait_eventcode_id)
            
    return ret, str_data 

    
def query_wait_eventcode(sn, wait_eventcode_id, timeout):
    """
    """
    
    ret         = ERR_FAIL
    str_data    = ""

    usercmd1 = usercmd.Usercmd()
    
    ret, str_data = usercmd1.process_query_wait_eventcode(sn, wait_eventcode_id, timeout)
            
    return ret, str_data 


def query_cpe_last_faults(sn):
    """
    """
    
    ret         = ERR_FAIL
    str_data    = ""

    usercmd1 = usercmd.Usercmd()
    
    ret, str_data = usercmd1.process_query_cpe_last_faults(sn)
            
    return ret, str_data
        


# nwf 2013-05-09; common interface
# nwf 2013-06-01; upgrade to id
def init_alarm(sn, parameterlist, limit_max, limit_min, timelist=1, mode=1):
    """

    """
    ret             = ERR_FAIL
    str_data        = ""

    usercmd1        = usercmd.Usercmd()
    event           = EV_INIT_ALARM_RQST

    obj                 = MsgAlarmInform(sn) 
    obj.parameterlist   = parameterlist
    obj.limit_max       = limit_max
    obj.limit_min       = limit_min
    obj.timelist        = timelist
    obj.mode            = mode
    
    ret, str_data   = usercmd1.process_alarm_inform(event, obj)
            
    return ret, str_data

    
def start_alarm(sn, alarm_id):
    """

    """
    ret             = ERR_FAIL
    str_data        = ""

    usercmd1        = usercmd.Usercmd()
    event           = EV_START_ALARM_RQST

    obj             = MsgAlarmInform(sn) 
    obj.id_         = alarm_id
    
    ret, str_data   = usercmd1.process_alarm_inform_start(event, obj)
            
    return ret, str_data


def stop_alarm(sn, alarm_id):
    """

    """
    ret             = ERR_FAIL
    str_data        = ""

    usercmd1        = usercmd.Usercmd()
    event           = EV_STOP_ALARM_RQST

    obj             = MsgAlarmInform(sn)   
    obj.id_         = alarm_id
        
    ret, str_data = usercmd1.process_alarm_inform_stop(event, obj)    
            
    return ret, str_data


def get_alarm_values(sn, alarm_id):
    """

    """
    ret             = ERR_FAIL
    str_data        = ""

    usercmd1        = usercmd.Usercmd()
    event           = EV_GET_ALARM_PARAMETER_RQST

    obj                 = MsgAlarmInform(sn)    
    obj.id_             = alarm_id
    
    ret, str_data   = usercmd1.process_alarm_inform(event, obj)
            
    return ret, str_data


def init_monitor(sn, parameterlist, timelist=1):
    """

    """
    ret             = ERR_FAIL
    str_data        = ""

    usercmd1        = usercmd.Usercmd()
    event           = EV_INIT_MONITOR_RQST

    obj                 = MsgMonitorInform(sn)    
    obj.parameterlist   = parameterlist
    obj.timelist        = timelist
    
    ret, str_data   = usercmd1.process_monitor_inform(event, obj)
            
    return ret, str_data
    

def start_monitor(sn, monitor_id):
    """

    """
    ret             = ERR_FAIL
    str_data        = ""

    usercmd1        = usercmd.Usercmd()
    event           = EV_START_MONITOR_RQST

    obj             = MsgMonitorInform(sn)    
    obj.id_         = monitor_id
    
    ret, str_data   = usercmd1.process_monitor_inform_start(event, obj)
            
    return ret, str_data


def stop_monitor(sn, monitor_id):
    """

    """
    ret             = ERR_FAIL
    str_data        = ""

    usercmd1        = usercmd.Usercmd()
    event           = EV_STOP_MONITOR_RQST

    obj             = MsgMonitorInform(sn)
    obj.id_         = monitor_id
    
    ret, str_data   = usercmd1.process_monitor_inform_stop(event, obj)
            
    return ret, str_data


def get_monitor_values(sn, monitor_id):
    """

    """
    ret             = ERR_FAIL
    str_data        = ""

    usercmd1        = usercmd.Usercmd()
    event           = EV_GET_MONITOR_PARAMETER_RQST
    
    obj                 = MsgMonitorInform(sn)
    obj.id_             = monitor_id
    
    ret, str_data   = usercmd1.process_monitor_inform(event, obj)
            
    return ret, str_data    


def close_tr069_acs():
    """
    """
    ret             = ERR_FAIL
    str_data        = ""

    usercmd1        = usercmd.Usercmd()
    
    ret, str_data   = usercmd1.process_close_tr069_acs()
            
    return ret, str_data     


def query_version_is_ok(version=""):
    """
    """
    ret             = ERR_FAIL
    str_data        = ""

    if (not version):
        try:
            # rf lib 
            import  TR069.testlibversion        as testlibversion 
            version = testlibversion.VERSION
        except Exception, e:
            pass

    usercmd1        = usercmd.Usercmd()
    
    ret, str_data   = usercmd1.process_query_version_is_ok(version)
            
    return ret, str_data 


def query_last_session_soap(sn):
    """
    """
    ret             = ERR_FAIL
    str_data        = ""

    usercmd1        = usercmd.Usercmd()
    
    ret, str_data   = usercmd1.process_query_last_session_soap(sn)
            
    return ret, str_data 
    

def query_cpe_interface_version(sn):
    """
    """
    ret             = ERR_FAIL
    str_data        = ""

    usercmd1        = usercmd.Usercmd()
    
    ret, str_data   = usercmd1.process_query_cpe_interface_version(sn)
            
    return ret, str_data 
    


# ---------------------------------------------------------------

def test_rpc():


    if (0):
        ret, str_data = user.get_rpc_methods();
        print str_data

    # rpc
    if (1):
        dict_data = {"ParameterList": [
                        dict(Name="InternetGatewayDevice.ManagementServer.Password1", 
                             Value="admin"), 
                        dict(Name="InternetGatewayDevice.ManagementServer.ConnectionRequestPassword1", 
                             Value="admin")]}
        ret, str_data  = user.set_parameter_values(ParameterList=dict_data.get("ParameterList"))
        print str_data
    
    if (0):
        ret, str_data  = user.get_parameter_names(ParameterPath="InternetGatewayDevice.WANDevice.1.WANConnectionDevice1.")
        print str_data
    
    if (0):
        ret, str_data = user.connection_request();
        print str_data        


def test_worklist():
    global ID_
    
    user = UserWorklist()
    
   
    dict1 = {}
        
    ret = user.worklistprocess_download(**dict1)
    print ret
    
    
    dict_data = {"ParameterList": [
                    dict(Name="InternetGatewayDevice.ManagementServer.Password", 
                         Value="hgw"), 
                    dict(Name="InternetGatewayDevice.ManagementServer.ConnectionRequestPassword", 
                         Value="itms")]}

    
    dict1 = {}
    dict1["worklist_name"] = "Auto_SetParameterValue"
    dict1["dict_data"] = dict_data    
    x = user.worklistprocess_build(**dict1)
    #print x
    ID_ = x[1].id_
    
    dict1 = {}
    dict1["id_"] =ID_
    dict1["sn"] = SN    
    x = user.worklistprocess_bind_physical(**dict1)
    print x    
    
    
    dict1 = {}
    dict1["id_"] = ID_ 
    x = user.worklistprocess_execute(**dict1)
    print x
    
    dict1 = {}
    dict1["id_"] = ID_
    x = user.worklistprocess_query(**dict1)
    print x    
    


def test_query_cfg():
    pass

    if (1):
        
        
        
        ret, ret_data = query_cpe_last_faults(SN)
        print ret, ret_data
    

    if (0):
        dict_item={"worklist_domain":"ADSL2"}
        x = update_cpe_info(SN, dict_item)
        print x    

        x = query_cpe_info(SN)
        print x


def test_wait_eventcode():
    pass
    x = wait_next_inform(SN, 123)
    print x

def test_alarm():
    
    ret_api, ret_data = init_alarm(SN,
               "InternetGatewayDevice.WANDevice.1.WANConnectionDevice.2.WANIPConnection.1.Stats.EthernetPacketsReceived",
               2000, 3000)
    alarm_id = ret_data.id_
    ret_api, ret_data = start_alarm(SN, alarm_id)
    print ret_data


SN="00904C-2013012901"
user = UserRpc(sn = SN, 
ip=usercfg.AGENT_HTTP_IP, port=usercfg.AGENT_HTTP_PORT, page=usercfg.USER_PAGE, 
sender=KEY_SENDER_USER)

def test():
    pass


    test_alarm()

    #test_wait_eventcode()
    
    #test_rpc()
    test_worklist()
    
    #close_tr069_acs()

    x=query_last_session_soap(SN)
    print x
    
    #query_version_is_ok()
    
    #test_query_cfg()


        
if __name__ == '__main__':

    test()                       