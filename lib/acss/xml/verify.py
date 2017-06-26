#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: verify
#  function: verify the structures and elements in soap envelope of RPC methods' 
#            request and response whether adhere tr069 specification
#  Author: ATT development group
#  version: V1.0
#  date: 2012.08.21
#  change log:
#  lana     20120821     created
#  lana     20130828     修改CONNECTION_REQUEST_URL等的值，可以匹配其他根节点
# ***************************************************************************

import re
import types

import TR069.lib.common.logs.log as log 
import parse
from TR069.lib.common.rpcstruct import *

# xml namespace
SOAP_ENV = "{http://schemas.xmlsoap.org/soap/envelope/}"
XSD_NS = "{http://www.w3.org/2001/XMLSchema}"

# xsd::string
XSD_NS_STRING = XSD_NS + "string"

# soap envelope tag
SOAP_ENVELOPE_TAG = SOAP_ENV + "Envelope"

# fault message tag
SOAP_FAULT_TAG = SOAP_ENV + 'Fault'

# execution result
VERIFY_SUC = 0
VERIFY_FAIL = -1
VERIFY_ERR_UNSUPPORT_RPC_METHOD = -2

# check all parameters of RPC whether adhere to specification, if set to 0, don't check  
CHECK_PARAMETERS_INTEGRALITY = 1
CHECK_ARRAY_SIZE = 0

# the number of parameters in RPC
NUM_OF_INFORM_PARAMETERS = 6
NUM_OF_TRANSFER_COMPLETE_PARAMETERS = 4
NUM_OF_AUTONOMOUS_TRANSFER_COMPLETE_PARAMETERS = 9
NUM_OF_DOWNLOAD_RESPONSE_PARAMETERS = 3
NUM_OF_KICKED_PARAMETERS = 4
NUM_OF_FAULT_PARAMETERS = 3

# inform message parameters name
CONNECTION_REQUEST_URL = ".ManagementServer.ConnectionRequestURL"
DEVICE_HARDWARE_VERSION = ".DeviceInfo.HardwareVersion"
DEVICE_SOFTWARE_VERSION = ".DeviceInfo.SoftwareVersion"




class Verify:
    """
    verify the structures and elements in soap whether adhere to tr069 specification
    """
    
    def __init__(self):
        """
        initial: create parse object
        """
        self.result = None
        self.cur_RPC_name = None
        self.cur_cwmp_version = None
    
    def check_soap_msg(self, xml_src):
        """
        verify soap msg, how mandy soap envelope in xml_src,
        the structure of soap body whether valid
        """
        
        if xml_src == "":
            return VERIFY_FAIL

        # if xml_src include "\r\n\r","\r", delete "\r"
        #xml_src = xml_src.replace("\r", "")
        index = xml_src.find('<')
        if  index != 0:
            xml_src = xml_src[index:]
        
        try:
            self.soap_list = parse.analyze_soap_envelope(xml_src, SOAP_ENVELOPE_TAG)
            if self.soap_list == None:
                log.debug_err("This message does not adhere to tr069 SOAP envelope specification")
                return VERIFY_FAIL
            elif len(self.soap_list) == 0:
                log.debug_err("This message does not include SOAP envelope")
                return VERIFY_FAIL
            elif len(self.soap_list) > 1:
                log.debug_err("Do not support more than one SOAP envelope in one message now")
                return VERIFY_FAIL
            else:
                # get envelope children object by object in returned soap_list
                self.envelope_children = parse.get_children_list(self.soap_list[0])
                # soap envelope object whether have header and body two children objects
                if len(self.envelope_children) == 2:
                    # parse and verify soap header
                    ret = self.check_soap_header(self.envelope_children[0])
                    if ret != VERIFY_SUC:
                        log.debug_err("invalid soap header")
                        return VERIFY_FAIL
                    
                    # parse and verify soap body
                    ret = self.check_soap_body(self.envelope_children[1])
                    
                elif len(self.envelope_children) == 1:
                    # maybe this soap envelope only have body
                    ret = self.check_soap_body(self.envelope_children[0])
                    
                else:
                    log.debug_err("Unsupport soap envelope structure!")
                    return VERIFY_FAIL
        except Exception, e:
            err_info = "check soap msg occures exception:%s" % e
            log.debug_err(err_info)
            return VERIFY_FAIL
        
        return ret
    
    def check_soap_header(self, header_element):
        """
        verify the structures of soap header
        """
        
        # soap header useful data
        self.soap_header_cwmp_id = None
        
        
        # parse whole structure
        ret_list = parse.get_children_value(header_element)
        
        # check parameter number of soap header
        if CHECK_PARAMETERS_INTEGRALITY == 1:
            if len(ret_list) != 1:
                log.debug_err("Incomplete soap header:",ret_list)
                return VERIFY_FAIL
        
        if ret_list[0][0] != "":
            # get current cwmp version from namespace, because of can not get it from SOAP_envelope attribute.
            pat = 'cwmp-[0-9]+-[0-9]+'
            list_cwmp_version = re.findall(pat, ret_list[0][0])
            if list_cwmp_version != []:
                self.cur_cwmp_version = list_cwmp_version[0]
            else:
                log.debug_err("invalid soap header's element:", ret_list[0][0])
                return VERIFY_FAIL
            
            # get cwmp namespace prefix
            self.cwmp_namespace_prefix = ret_list[0][0][0:ret_list[0][0].find('}')+1]
            
            # get header element name
            header_cwmp_id_tag = ret_list[0][0][ret_list[0][0].find('}')+1:
                                                 len(ret_list[0][0])]
            if header_cwmp_id_tag == "ID":
                self.soap_header_cwmp_id = ret_list[0][1]
            else:
                log.debug_err("invalid soap header's element:", ret_list[0][0])
                return VERIFY_FAIL
        else:
            log.debug_err("invalid soap header's element:", ret_list[0][0])
            return VERIFY_FAIL
        
        
        return VERIFY_SUC



    def check_soap_body(self,body_element):
        """
        verify the structures of soap body of different RPC whether valid
        """
        # get body children object, it's RPC method object
        self.body_children = parse.get_children_list(body_element)
        if len(self.body_children) != 1:
            return VERIFY_FAIL
        
        # get the first element of returned list
        body_children_name = parse.get_children_name_list(body_element)[0]
        
        # Fault message's namespace prefix is "SOAP-ENV", different from the other RPC methods
        if body_children_name == SOAP_FAULT_TAG:
            self.cur_RPC_name = 'Fault'
            ret = self.check_fault_struct(self.body_children[0])
            return ret
        
        # strip namespace prefix, get RPC name
        self.cur_RPC_name = body_children_name[body_children_name.find('}')+1:
                                                 len(body_children_name)]
        
        # call diffent method verify different RPC method structure by RPC method name
        if self.cur_RPC_name == 'GetRPCMethodsResponse':
            ret = self.check_get_RPC_methods_response_struct(self.body_children[0])
        
            
        elif self.cur_RPC_name == 'Inform':
            ret = self.check_inform_struct(self.body_children[0])
            
        elif self.cur_RPC_name == 'TransferComplete':
            ret = self.check_transfer_complete_struct(self.body_children[0])
        
        elif self.cur_RPC_name == 'AutonomousTransferComplete':
            ret = self.check_autonomous_transfer_complete_struct(self.body_children[0])
        
            
        elif self.cur_RPC_name == 'SetParameterValuesResponse':
            ret = self.check_set_parameter_values_response_struct(self.body_children[0])
            
        elif self.cur_RPC_name == 'GetParameterValuesResponse':
            ret = self.check_get_parameter_values_response_struct(self.body_children[0])
            
        elif self.cur_RPC_name == 'GetParameterNamesResponse':
            ret = self.check_get_parameter_names_response_struct(self.body_children[0])
            
        elif self.cur_RPC_name == 'GetParameterAttributesResponse':
            ret = self.check_get_parameter_attributes_response_struct(self.body_children[0])
            
        elif self.cur_RPC_name == 'AddObjectResponse':
            ret = self.check_add_object_response_struct(self.body_children[0])
            
        elif self.cur_RPC_name == 'DeleteObjectResponse':
            ret = self.check_delete_object_response_struct(self.body_children[0])
                
        elif self.cur_RPC_name == 'DownloadResponse':
            ret = self.check_download_response_struct(self.body_children[0])
            
            
        elif self.cur_RPC_name == 'GetQueuedTransfersResponse':
            ret = self.get_queued_transfer_response_struct(self.body_children[0])
            
        elif self.cur_RPC_name == 'GetOptionsResponse':
            ret = self.get_options_response_struct(self.body_children[0])
        
        elif self.cur_RPC_name == 'UploadResponse':
            ret = self.check_upload_response_struct(self.body_children[0])
            
        elif self.cur_RPC_name == 'GetAllQueuedTransfersResponse':
            ret = self.check_get_all_queued_transfers_response_struct(self.body_children[0])
            
            
        elif self.cur_RPC_name == 'Kicked':
            ret = self.check_kicked_struct(self.body_children[0])
            
        elif self.cur_RPC_name == 'RequestDownload':
            ret = self.check_request_download_struct(self.body_children[0])

        elif self.cur_RPC_name == 'DUStateChangeComplete':
            ret = self.check_DU_state_change_complete_struct(self.body_children[0])

        elif self.cur_RPC_name == 'AutonomousDUStateChangeComplete':
            ret = self.check_autonomous_DU_state_change_complete_struct(self.body_children[0])
        
        elif self.cur_RPC_name == 'GetRPCMethods' or \
             self.cur_RPC_name == 'SetParameterAttributesResponse' or \
             self.cur_RPC_name == 'RebootResponse' or \
             self.cur_RPC_name == 'ScheduleInformResponse' or \
             self.cur_RPC_name == 'SetVouchersResponse' or \
             self.cur_RPC_name == 'FactoryResetResponse' or \
             self.cur_RPC_name == 'ScheduleDownloadResponse' or \
             self.cur_RPC_name == 'CancelTransferResponse' or \
             self.cur_RPC_name == 'ChangeDUStateResponse':
            
            ret = self.check_no_parameter_response_struct(self.body_children[0])
            
        else:
            log.debug_err("Now do not support RPC method:" + body_children_name)
            return VERIFY_ERR_UNSUPPORT_RPC_METHOD
        return ret
    

    def check_get_RPC_methods_response_struct(self, element):
        """
        check GetRPCMethodsResponse struct whether adhere to specification,
        and get some user useful values
        """
        log.debug_info("GetRPCMethodsResponse message")
        
        # create GetRPCMethodsResponse object
        self.result = GetRPCMethodsResponse()
        
        
        # parse whole structure
        ret_list = parse.get_children_value(element)
        
        # GetRPCMethodsResponse have only one parameter "MethodList"
        if CHECK_PARAMETERS_INTEGRALITY == 1:
            if len(ret_list) != 1:
                log.debug_err("Incomplete GetRPCMethodsResponse struct:",ret_list)
                return VERIFY_FAIL
        
        tmp_list = ret_list[0]
        # Judge parameter name
        if tmp_list[0] == "MethodList":
            
            if type(tmp_list[1]) == types.ListType:
            
                tmp_sub_list = tmp_list[1]
                # Judge the number of MethodList's sub element
                # get defined array size by attribute of MethodList
                RPC_methods_list_len = self.get_array_size(element, "MethodList")
                if CHECK_ARRAY_SIZE == 1:
                    if len(tmp_sub_list) != RPC_methods_list_len:
                        log.debug_err("invalid MethodList struct,the defined array size is ",
                                       RPC_methods_list_len,
                                       "but the number of array element is",
                                       len(tmp_sub_list))
                        return VERIFY_FAIL
                
                for i in range(len(tmp_sub_list)):
                    # Judge the name of MethodList's sub element
                    if (tmp_sub_list[i][0] == "string") or (
                        tmp_sub_list[i][0] == XSD_NS_STRING):
                        #  save the value of MethodList's sub element
                        self.result.MethodList.append(tmp_sub_list[i][1])
                    else:
                        log.debug_err("invalid MethodList struct element:", tmp_sub_list[i][0])
                        return VERIFY_FAIL
        else:
            log.debug_err("invalid GetRPCMethodsResponse parameter:",tmp_list[0])
            return VERIFY_FAIL
        
        
        return VERIFY_SUC
    

    def check_inform_struct(self, element):
        """
        check inform struct whether adhere to specification,
        and get some user useful values
        """
        log.debug_info("inform message")
        
        # create object to save parse results
        self.result = Inform()
        self.result.DeviceId = DeviceIdStruct()
        
        
        # parse whole inform structure
        ret_list = parse.get_children_value(element)
        
        # check the number of parameter whether adhere to specification
        if CHECK_PARAMETERS_INTEGRALITY == 1:
            if len(ret_list) != NUM_OF_INFORM_PARAMETERS:
                log.debug_err("Incomplete inform message")
                return VERIFY_FAIL
        
        # get value of each paramenter	
        for i in range(len(ret_list)):
            tmp_list = ret_list[i]
            if tmp_list[0] == "DeviceId":
                tmp_sub_list = tmp_list[1]
                for j in range(len(tmp_sub_list)):
                    if tmp_sub_list[j][0] == "Manufacturer":
                        self.result.DeviceId.Manufacturer = tmp_sub_list[j][1]
                    elif tmp_sub_list[j][0] == "OUI":
                        self.result.DeviceId.OUI = tmp_sub_list[j][1]
                    elif tmp_sub_list[j][0] == "ProductClass":
                        self.result.DeviceId.ProductClass = tmp_sub_list[j][1]
                    elif tmp_sub_list[j][0] == "SerialNumber":
                        self.result.DeviceId.SerialNumber = tmp_sub_list[j][1]
                    else:
                        log.debug_err("invalid DeviceId struct element:", tmp_sub_list[j][0])
                        return VERIFY_FAIL
            elif tmp_list[0] == "Event":
                if type(tmp_list[1]) == types.ListType:
                    tmp_sub_list = tmp_list[1]
                    
                    if CHECK_ARRAY_SIZE == 1:
                        inform_event_eventstruct_len = self.get_array_size(element, "Event")
                        if len(tmp_sub_list) != inform_event_eventstruct_len:
                            log.debug_err("invalid inform EventStruct,the defined array size is ",
                                           inform_event_eventstruct_len,
                                           "but the number of array element is",
                                           len(tmp_sub_list))
                            return VERIFY_FAIL
                    for j in range(len(tmp_sub_list)):
                        if (type(tmp_sub_list[j][1]) == types.ListType) and (
                            tmp_sub_list[j][0] == "EventStruct"):
                            #create EventStruct object
                            event_struct_object = EventStruct()
                            
                            if tmp_sub_list[j][1][0][0] == "EventCode":
                                
                                event_struct_object.EventCode = tmp_sub_list[j][1][0][1]
                            else:
                                log.debug_err("invalid EventStruct sub element:", tmp_sub_list[j][1][0][0])
                                return VERIFY_FAIL
                            if tmp_sub_list[j][1][1][0] == "CommandKey":
                                
                                event_struct_object.CommandKey = tmp_sub_list[j][1][1][1]
                            else:
                                log.debug_err("invalid EventStruct sub element:", tmp_sub_list[j][1][1][0])
                                return VERIFY_FAIL
                            
                            self.result.Event.append(event_struct_object)
                        else:
                            log.debug_err("invalid Event sub element:",
                                           tmp_sub_list[j][0],
                                           tmp_sub_list[j][1])
                            return VERIFY_FAIL
                        
            elif tmp_list[0] == "MaxEnvelopes":
                self.result.MaxEnvelopes = tmp_list[1]
            elif tmp_list[0] == "CurrentTime":
                self.result.CurrentTime = tmp_list[1]
            elif tmp_list[0] == "RetryCount":
                self.result.RetryCount = tmp_list[1]
            elif tmp_list[0] == "ParameterList":
                
                if type(tmp_list[1] == types.ListType):
                    tmp_sub_list = tmp_list[1]
                    
                    if CHECK_ARRAY_SIZE == 1:
                        inform_parameterlist_len = self.get_array_size(element, "ParameterList")
                        if len(tmp_sub_list) != inform_parameterlist_len:
                            log.debug_err("invalid inform ParameterValueStruct,the defined array size is ",
                                           inform_parameterlist_len,
                                          "but the number of array element is",
                                          len(tmp_sub_list))
                            return VERIFY_FAIL
                    for j in range(len(tmp_sub_list)):
                        if (type(tmp_sub_list[j][1]) == types.ListType) and (
                            tmp_sub_list[j][0] == "ParameterValueStruct"):
                            #create ParameterValueStruct object
                            parameterlist_struct_object = ParameterValueStruct()
                            
                            if (tmp_sub_list[j][1][0][0] == "Name") and (
                                tmp_sub_list[j][1][1][0] == "Value"):
                                
                                # get value type from the atrribute dict
                                value_type = tmp_sub_list[j][1][1][2].values()[0]
                                # strip namespace prefix "xsd:"
                                value_type = value_type[value_type.find(':')+1:
                                                        len(value_type)]
                                
                                # save name,value, type
                                parameterlist_struct_object.Name = tmp_sub_list[j][1][0][1]
                                parameterlist_struct_object.Value = tmp_sub_list[j][1][1][1]
                                parameterlist_struct_object.Value_type = value_type
                                
                                self.result.ParameterList.append(parameterlist_struct_object)
                                
                                # save special name's value
                                if tmp_sub_list[j][1][0][1].find(CONNECTION_REQUEST_URL) != -1:
                                    self.result.DeviceId.ConnectionRequestURL = \
                                        tmp_sub_list[j][1][1][1]
                                if tmp_sub_list[j][1][0][1].find(DEVICE_HARDWARE_VERSION) != -1:
                                    self.result.DeviceId.Hardwareversion = \
                                        tmp_sub_list[j][1][1][1]
                                if tmp_sub_list[j][1][0][1].find(DEVICE_SOFTWARE_VERSION) != -1:
                                    self.result.DeviceId.Softwareversion = \
                                        tmp_sub_list[j][1][1][1]
                                    
                            else:
                                log.debug_err("invalid ParameterValueStruct sub element:",
                                              tmp_sub_list[j][1][0][0],tmp_sub_list[j][1][1][0])
                                return VERIFY_FAIL
                        else:
                            log.debug_err("invalid ParameterValueStruct in inform RPC:",
                                   tmp_sub_list[j][0],tmp_sub_list[j][1])
                            return VERIFY_FAIL
            else:
                log.debug_err("invalid paramenters in inform RPC:", tmp_list[0])
                return VERIFY_FAIL		
            
        return VERIFY_SUC
    
    def check_transfer_complete_struct(self, element):
        """
        check TransferComplete struct whether adhere to specification,
        and get some user useful values
        """
        log.debug_info("TransferComplete message")
        
        # create TransferComplete object
        self.result = TransferComplete()
        
        
        # parse whole structure
        ret_list = parse.get_children_value(element)
        
        # check the number of parameter whether adhere to specification
        if CHECK_PARAMETERS_INTEGRALITY == 1:
            if len(ret_list) != NUM_OF_TRANSFER_COMPLETE_PARAMETERS:
                log.debug_err("Incomplete TransferComplete message")
                return VERIFY_FAIL
        
        # get value of each paramenter
        for i in range(len(ret_list)):
            tmp_list = ret_list[i]
            if tmp_list[0] == "CommandKey":
                self.result.CommandKey = tmp_list[1]
            elif tmp_list[0] == "FaultStruct":
                self.result.FaultStruct = FaultStruct()
                
                tmp_sub_list = tmp_list[1]
                if tmp_sub_list[0][0] == "FaultCode":
                    self.result.FaultStruct.FaultCode = tmp_sub_list[0][1]
                else:
                    log.debug_err("invalid paramenters in FaultStruct:",tmp_sub_list[0][0])
                    return VERIFY_FAIL
                
                if tmp_sub_list[1][0] == "FaultString":
                    self.result.FaultStruct.FaultString = tmp_sub_list[1][1]
                else:
                    log.debug_err("invalid paramenters in FaultStruct:",tmp_sub_list[1][0])
                    return VERIFY_FAIL
                
            elif tmp_list[0] == "StartTime":
                self.result.StartTime = tmp_list[1]
            elif tmp_list[0] == "CompleteTime":
                self.result.CompleteTime = tmp_list[1]
            else:
                log.debug_err("invalid paramenters in transfer complete RPC:",tmp_list[0])
                return VERIFY_FAIL
            
        
        return VERIFY_SUC
    
    def check_autonomous_transfer_complete_struct(self, element):
        """
        check AutonomousTransferComplete struct whether adhere to specification,
        and get some user useful values
        """
        log.debug_info("AutonomousTransferComplete message")
        
        # create AutonomousTransferComplete object
        self.result = AutonomousTransferComplete()
        self.result.FaultStruct = FaultStruct()
        
        # parse whole structure
        ret_list = parse.get_children_value(element)
        
        # check the number of parameter whether adhere to specification
        if CHECK_PARAMETERS_INTEGRALITY == 1:
            if len(ret_list) != NUM_OF_AUTONOMOUS_TRANSFER_COMPLETE_PARAMETERS:
                log.debug_err("Incomplete AutonomousTransferComplete message")
                return VERIFY_FAIL
        
        # get value of each paramenter
        for i in range(len(ret_list)):
            tmp_list = ret_list[i]
            if tmp_list[0] == "AnnounceURL":
                self.result.AnnounceURL = tmp_list[1]
            elif tmp_list[0] == "TransferURL":
                self.result.TransferURL = tmp_list[1]
            elif tmp_list[0] == "IsDownload":
                self.result.IsDownload = tmp_list[1]
            elif tmp_list[0] == "FileType":
                self.result.FileType = tmp_list[1]
            elif tmp_list[0] == "FileSize":
                self.result.FileSize = tmp_list[1]
            elif tmp_list[0] == "TargetFileName":
                self.result.TargetFileName = tmp_list[1]
            elif tmp_list[0] == "FaultStruct":
                tmp_sub_list = tmp_list[1]
                if tmp_sub_list[0][0] == "FaultCode":
                    self.result.FaultStruct.FaultCode = tmp_sub_list[0][1]
                else:
                    log.debug_err("invalid paramenters in FaultStruct:",tmp_sub_list[0][0])
                    return VERIFY_FAIL
                
                if tmp_sub_list[1][0] == "FaultString":
                    self.result.FaultStruct.FaultString = tmp_sub_list[1][1]
                else:
                    log.debug_err("invalid paramenters in FaultStruct:",tmp_sub_list[1][0])
                    return VERIFY_FAIL
            elif tmp_list[0] == "StartTime":
                self.result.StartTime = tmp_list[1]
            elif tmp_list[0] == "CompleteTime":
                self.result.CompleteTime = tmp_list[1]
            else:
                log.debug_err("invalid paramenters in autonomous transfer \
                       complete message:",tmp_list[0])
                return VERIFY_FAIL
        
        return VERIFY_SUC
    
    
    def check_get_parameter_names_response_struct(self, element):
        """
        check GetParameterNamesResponse struct whether adhere to specification,
        and get some user useful values
        """
        log.debug_info("GetParameterNamesResponse message")
        
        # creat GetParameterNamesResponse object
        self.result = GetParameterNamesResponse()
        
        
        # parse whole structure
        ret_list = parse.get_children_value(element)
        
        if CHECK_PARAMETERS_INTEGRALITY == 1:
            if len(ret_list) != 1:
                log.debug_err("Incomplete GetParameterNamesResponse struct:",ret_list)
                return VERIFY_FAIL

        tmp_list = ret_list[0]
        if tmp_list[0] == "ParameterList":
            if type(tmp_list[1]) == types.ListType:
                tmp_sub_list = tmp_list[1]
                if CHECK_ARRAY_SIZE == 1:
                    # get defined array size
                    get_parameter_names_resp_list_len = \
                        self.get_array_size(element, "ParameterList")
                    # Judge the number of ParameterList sub element
                    if len(tmp_sub_list) != get_parameter_names_resp_list_len:
                        log.debug_err("invalid ParameterInfoStruct,the defined array size is ",
                                get_parameter_names_resp_list_len,
                                "but the number of array element is",
                                len(tmp_sub_list))
                        return VERIFY_FAIL
                
                for i in range(len(tmp_sub_list)):
                    if (type(tmp_sub_list[i][1]) == types.ListType) and (
                        tmp_sub_list[i][0] == "ParameterInfoStruct"):
                        
                        # create ParameterInfoStruct object
                        obj_para_info_struct = ParameterInfoStruct()
                        
                        if (tmp_sub_list[i][1][0][0] == "Name") and (
                            tmp_sub_list[i][1][1][0] == "Writable"):
                            
                            obj_para_info_struct.Name = tmp_sub_list[i][1][0][1]
                            obj_para_info_struct.Writable = tmp_sub_list[i][1][1][1]
                            
                        else:
                            log.debug_err("invalid ParameterInfoStruct in GetParameterNamesResponse:",
                                   tmp_sub_list[i][1][0][0],tmp_sub_list[i][1][1][0])
                            return VERIFY_FAIL
                        
                        # save ParameterInfoStruct
                        self.result.ParameterList.append(obj_para_info_struct)
                        
                    else:
                        log.debug_err("invalid GetParameterNamesResponse struct:",
                               tmp_sub_list[i][0],tmp_sub_list[i][1])
                        return VERIFY_FAIL
        else:
            log.debug_err("invalid GetParameterNamesResponse struct:",tmp_list[0])
            return VERIFY_FAIL
        
        return VERIFY_SUC
    
    def check_set_parameter_values_response_struct(self, element):
        """
        check SetParameterValuesResponse struct whether adhere to specification,
        and get some user useful values
        """
        log.debug_info("SetParameterValuesResponse message")
        
        # create SetParameterValuesResponse object
        self.result = SetParameterValuesResponse()
        
        # parse whole structure
        ret_list = parse.get_children_value(element)
        
        if CHECK_PARAMETERS_INTEGRALITY == 1:
            if len(ret_list) != 1:
                log.debug_err("invalid SetParameterValuesResponse struct:",ret_list)
                return VERIFY_FAIL
        
        if ret_list[0][0] == "Status":
            self.result.Status = ret_list[0][1]
        else:
            log.debug_err("invalid SetParameterValuesResponse struct:",ret_list[0][0])
            return VERIFY_FAIL	
        
        return VERIFY_SUC
    
    def check_get_parameter_values_response_struct(self, element):
        """
        check GetParameterValuesResponse struct whether adhere to specification,
        and get some user useful values
        """
        log.debug_info("GetParameterValuesResponse message")
        
        # create GetParameterValuesResponse object
        self.result = GetParameterValuesResponse()
        
        
        # parse whole structure
        ret_list = parse.get_children_value(element)
        
        if CHECK_PARAMETERS_INTEGRALITY == 1:
            if len(ret_list) != 1:
                log.debug_err("invalid GetParameterValuesResponse struct:",ret_list)
                return VERIFY_FAIL
            
        tmp_list = ret_list[0]
        if tmp_list[0] == "ParameterList":
            if type(tmp_list[1]) == types.ListType:
                tmp_sub_list = tmp_list[1]
                if CHECK_ARRAY_SIZE == 1:
                    # get defined array size
                    get_parameter_values_resp_list_len = \
                        self.get_array_size(element, "ParameterList")
                    # Judge the number of ParameterList sub element
                    if len(tmp_sub_list) != get_parameter_values_resp_list_len:
                        log.debug_err("invalid ParameterValueStruct,the defined array size is ",
                                      get_parameter_values_resp_list_len,
                                      "but the number of array element is",
                                      len(tmp_sub_list))
                        return VERIFY_FAIL
                
                for i in range(len(tmp_sub_list)):
                    if (type(tmp_sub_list[i][1]) == types.ListType) and (
                        tmp_sub_list[i][0] == "ParameterValueStruct"):
                        
                        # create ParameterValueStruct object
                        obj_para_value_struct = ParameterValueStruct()
                        
                        if (tmp_sub_list[i][1][0][0] == "Name") and (
                            tmp_sub_list[i][1][1][0] == "Value"):
                            
                            # get value type from the atrribute dict
                            value_type = tmp_sub_list[i][1][1][2].values()[0]
                            # strip namespace prefix "xsd:"
                            value_type = value_type[value_type.find(':')+1:len(value_type)]
                                
                            # save name,value, type
                            obj_para_value_struct.Name = tmp_sub_list[i][1][0][1]
                            obj_para_value_struct.Value = tmp_sub_list[i][1][1][1]
                            obj_para_value_struct.Value_type = value_type
                            
                        else:
                            log.debug_err("invalid ParameterValueStruct element:",
                                           tmp_sub_list[i][1][0][0],tmp_sub_list[i][1][1][0])
                            return VERIFY_FAIL
                        
                        self.result.ParameterList.append(obj_para_value_struct)
                    else:
                        log.debug_err("invalid GetParameterValuesResponse struct:",
                                       tmp_sub_list[i][0],tmp_sub_list[i][1])
                        return VERIFY_FAIL
        else:
            log.debug_err("invalid GetParameterValuesResponse struct:",tmp_list[0])
            return VERIFY_FAIL
        
        return VERIFY_SUC
    
    def check_get_parameter_attributes_response_struct(self, element):
        """
        check GetParameterAttributesResponse struct whether adhere to specification,
        and get some user useful values
        """
        log.debug_info("GetParameterAttributesResponse message")
        
        # create GetParameterAttributesResponse object
        self.result = GetParameterAttributesResponse()
        
        
        # parse whole structure
        ret_list = parse.get_children_value(element)
        
        if CHECK_PARAMETERS_INTEGRALITY == 1:
            if len(ret_list) != 1:
                log.debug_err("invalid GetParameterAttributesResponse struct:",ret_list)
                return VERIFY_FAIL
            
        tmp_list = ret_list[0]
        if tmp_list[0] == "ParameterList":
            if type(tmp_list[1]) == types.ListType:
                tmp_sub_list = tmp_list[1]
                if CHECK_ARRAY_SIZE == 1:
                    # get defined array size
                    get_parameter_attrib_resp_list_len = \
                        self.get_array_size(element, "ParameterList")
                    # Judge the number of parameterlist sub element
                    if len(tmp_sub_list) != get_parameter_attrib_resp_list_len:
                        log.debug_err("invalid ParameterAttributeStruct,the defined array size is ",
                                       get_parameter_attrib_resp_list_len,
                                       "but the number of array element is",
                                       len(tmp_sub_list))
                        return VERIFY_FAIL
                
                # get children node list of ParameterList to get accesslist's size
                # first get ParameterList node object
                parameterlist_node_obj = parse.get_children_list(element)[0]
                # get parameterList's children node list
                children_obj_list = parse.get_children_list(parameterlist_node_obj)
                
                for i in range(len(tmp_sub_list)):
                    if (type(tmp_sub_list[i][1]) == types.ListType) and (
                        tmp_sub_list[i][0] == "ParameterAttributeStruct"):
                        
                        # create ParameterAttributeStruct object
                        obj_para_attrib_struct = ParameterAttributeStruct()
                        
                        if (tmp_sub_list[i][1][0][0] == "Name") and (
                            tmp_sub_list[i][1][1][0] == "Notification") and (
                            tmp_sub_list[i][1][2][0] == "AccessList"):
                            
                            # reset tmp_accesslist,
                            tmp_accesslist = []
                            
                            if CHECK_ARRAY_SIZE == 1:
                                # check AccessList's size
                                get_parameter_attrib_resp_accesslist_len = \
                                    self.get_array_size(children_obj_list[i], "AccessList")
                                
                                if type(tmp_sub_list[i][1][2][1]) != types.ListType:
                                    len_accesslist = 0
                                else:
                                    len_accesslist = len(tmp_sub_list[i][1][2][1])
                                
                                if get_parameter_attrib_resp_accesslist_len != 0 and \
                                   get_parameter_attrib_resp_accesslist_len == \
                                   len_accesslist:
                                    # save accesslist children node value to tmp_accesslist
                                    tmp_access_sub_list = tmp_sub_list[i][1][2][1]
                                    for j in range(len(tmp_access_sub_list)):
                                        if tmp_access_sub_list[j][0] == "string" or \
                                           tmp_access_sub_list[j][0] == XSD_NS_STRING:
                                            
                                            tmp_accesslist.append(tmp_access_sub_list[j][1])
                                        else:
                                            log.debug_err("valid accesslist children node type:",
                                                          tmp_access_sub_list[j][0])
                                            return VERIFY_FAIL
                                elif len_accesslist == 0 and get_parameter_attrib_resp_accesslist_len == 0:
                                    pass
                                else:
                                    
                                    log.debug_err("invalid AccessList struct, the defined array size is",
                                                  get_parameter_attrib_resp_accesslist_len,
                                                  "but have array element is",
                                                  tmp_sub_list[i][1][2][1])
                                    return VERIFY_FAIL
                            else:
                                # None: <AccessList SOAP-ENC:arrayType="xsd:string[0]"></AccessList>
                                # '/n':<AccessList SOAP-ENC:arrayType="xsd:string[0]">
                                #      </AccessList>
                                # if type is not list, it maybe None or '/n'
                                if types.ListType != type(tmp_sub_list[i][1][2][1]):
                                    len_accesslist = 0
                                else:
                                    len_accesslist = len(tmp_sub_list[i][1][2][1])
                                    
                                if len_accesslist == 0:
                                    
                                    pass
                                elif len_accesslist > 0:
                                    # save accesslist children node value to tmp_accesslist
                                    tmp_access_sub_list = tmp_sub_list[i][1][2][1]
                                    for j in range(len(tmp_access_sub_list)):
                                        if tmp_access_sub_list[j][0] == "string" or \
                                           tmp_access_sub_list[j][0] == XSD_NS_STRING:
                                            
                                            tmp_accesslist.append(tmp_access_sub_list[j][1])
                                        else:
                                            log.debug_err("valid accesslist children node type:",
                                                          tmp_access_sub_list[j][0])
                                            return VERIFY_FAIL
                                        
                            obj_para_attrib_struct.Name = tmp_sub_list[i][1][0][1]
                            obj_para_attrib_struct.Notification = tmp_sub_list[i][1][1][1]
                            obj_para_attrib_struct.AccessList = tmp_accesslist
                            
                            self.result.ParameterList.append(obj_para_attrib_struct)
                        else:
                            log.debug_err("invalid ParameterAttributeStruct in \
                                           GetParameterAttributesResponse:",
                                           tmp_sub_list[i][1][0][0],
                                           tmp_sub_list[i][1][1][0],
                                           tmp_sub_list[i][1][2][0])
                            return VERIFY_FAIL
                    else:
                        log.debug_err("invalid GetParameterAttributesResponse struct:",
                                       tmp_sub_list[i][0],tmp_sub_list[i][1])
                        return VERIFY_FAIL
        else:
            log.debug_err("invalid GetParameterAttributesResponse struct:",tmp_list[0])
            return VERIFY_FAIL
        
        return VERIFY_SUC
    
    def check_add_object_response_struct(self, element):
        """
        check AddObjectResponse struct whether adhere to specification,
        and get some user useful values
        """
        log.debug_info("AddObjectResponse message")
        
        # create AddObjectResponse object
        self.result = AddObjectResponse()
        
        
        # parse whole structure
        ret_list = parse.get_children_value(element)
        
        if CHECK_PARAMETERS_INTEGRALITY == 1:
            if len(ret_list) != 2:
                log.debug_err("invalid AddObjectResponse struct:",ret_list)
                return VERIFY_FAIL
            
        for i in range(len(ret_list)):
            if ret_list[i][0] == "InstanceNumber":
                self.result.InstanceNumber = ret_list[i][1]
            elif ret_list[i][0] == "Status":
                self.result.Status = ret_list[i][1]
            else:
                log.debug_err("invalid AddObjectResponse parameter:",ret_list[0][0])
                return VERIFY_FAIL
        
        return VERIFY_SUC
    
    def check_delete_object_response_struct(self, element):
        """
        check DeleteObjectResponse struct whether adhere to specification,
        and get some user useful values
        """
        log.debug_info("DeleteObjectResponse message")
        
        # create DeleteObjectResponse object
        self.result = DeleteObjectResponse()
        
        
        # parse whole structure
        ret_list = parse.get_children_value(element)
        
        if CHECK_PARAMETERS_INTEGRALITY == 1:
            if len(ret_list) != 1:
                log.debug_err("invalid DeleteObjectResponse struct:",ret_list)
                return VERIFY_FAIL
            
        if ret_list[0][0] == "Status":
            self.result.Status = ret_list[0][1]
        else:
            log.debug_err("invalid DeleteObjectResponse struct:",ret_list[0][0])
            return VERIFY_FAIL
            
        return VERIFY_SUC
    
    def check_download_response_struct(self, element):
        """
        check DownloadResponse struct whether adhere to specification,
        and get some user useful values
        """
        log.debug_info("DownloadResponse message")
        
        # create DownloadResponse object
        self.result = DownloadResponse()
        
        
        # parse whole structure
        ret_list = parse.get_children_value(element)
        
        if CHECK_PARAMETERS_INTEGRALITY == 1:
            if len(ret_list) != NUM_OF_DOWNLOAD_RESPONSE_PARAMETERS:
                log.debug_err("Incompete DownloadResponse struct:",ret_list)
                return VERIFY_FAIL
        
        for i in range(len(ret_list)):
            if ret_list[i][0] == "Status":
                self.result.Status = ret_list[i][1]
            elif ret_list[i][0] == "StartTime":
                self.result.StartTime = ret_list[i][1]
            elif ret_list[i][0] == "CompleteTime":
                self.result.CompleteTime = ret_list[i][1]
            else:
                log.debug_err("invalid DownloadResponse parameter: ", ret_list[i][0])
        
        return VERIFY_SUC
    

    def get_queued_transfer_response_struct(self, element):
        """
        check GetQueuedTransferResponse struct whether adhere to specification,
        and get some user useful values
        """
        log.debug_info("GetQueueTransferResponse message")
        
        # create GetQueuedTransferResponse object
        self.result = GetQueuedTransfersResponse()
        
        
        # parse whole structure
        ret_list = parse.get_children_value(element)
        
        if CHECK_PARAMETERS_INTEGRALITY == 1:
            if len(ret_list) != 1:
                log.debug_err("Incomplete GetQueueTransferResponse struct:",ret_list)
                return VERIFY_FAIL
        
        tmp_list = ret_list[0]
        if tmp_list[0] == "TransferList":
            if type(tmp_list[1]) == types.ListType:
                tmp_sub_list = tmp_list[1]
                if CHECK_ARRAY_SIZE == 1:
                    # get defined array size
                    get_queued_transfer_resp_list_len = \
                        self.get_array_size(element, "TransferList")
                    
                    if len(tmp_sub_list) != get_queued_transfer_resp_list_len:
                        log.debug_err("invalid QueuedTransferStruct,the defined array size is ",
                                      get_queued_transfer_resp_list_len,
                                      "but the number of array element is",
                                      len(tmp_sub_list))
                        return VERIFY_FAIL
                    
                for i in range(len(tmp_sub_list)):
                    if (tmp_sub_list[i][0] == "QueuedTransferStruct") and (
                        type(tmp_sub_list[i][1]) == types.ListType):
                        
                        # create QueuedTransferStruct object
                        obj_queued_transfer_struct = QueuedTransferStruct()
                        
                        if (tmp_sub_list[i][1][0][0] == "CommandKey") and (
                            tmp_sub_list[i][1][1][0] == "State"):
                            
                            obj_queued_transfer_struct.CommandKey = tmp_sub_list[i][1][0][1]
                            obj_queued_transfer_struct.State = tmp_sub_list[i][1][1][1]
                            
                        else:
                            log.debug_err("invalid QueuedTransferStruct element:",
                                          tmp_sub_list[i][1][0][0],
                                          tmp_sub_list[i][1][1][0])
                            return VERIFY_FAIL
                        
                        self.result.TransferList.append(obj_queued_transfer_struct)
                    else:
                        log.debug_err("invalid TransferList element ,",
                                       tmp_sub_list[i][0],tmp_sub_list[i][1])
                        return VERIFY_FAIL
        else:
            log.debug_err("invalid GetQueuedTransferResponse parameter:", tmp_list[0])
        
        return VERIFY_SUC
        
    
    def get_options_response_struct(self, element):
        """
        check GetOptionsResponse struct whether adhere to specification,
        and get some user useful values
        """
        log.debug_info("GetOptionsResponse message")
        
        # create GetOptionsResponse object
        self.result = GetOptionsResponse()
        
        
        # parse whole structure
        ret_list = parse.get_children_value(element)
        
        if CHECK_PARAMETERS_INTEGRALITY == 1:
            if len(ret_list) != 1:
                log.debug_err("Incomplete GetOptionsResponse struct:",ret_list)
                return VERIFY_FAIL
        
        tmp_list = ret_list[0]
        if tmp_list[0] == "OptionList":
            if type(tmp_list[1]) == types.ListType:
                tmp_sub_list = tmp_list[1]
                
                if CHECK_ARRAY_SIZE == 1:
                    # get defined array size
                    get_options_resp_list_len = \
                        self.get_array_size(element, "OptionList")
    
                    if len(tmp_sub_list) != get_options_resp_list_len:
                        log.debug_err("invalid OptionList struct,the defined array size is ",
                                      get_options_resp_list_len,
                                      "but the number of array element is",
                                      len(tmp_sub_list))
                        return VERIFY_FAIL
                    
                for i in range(len(tmp_sub_list)):
                    if (tmp_sub_list[i][0] == "OptionStruct") and (
                        type(tmp_sub_list[i][1]) == types.ListType):
                        
                        # create OptionStruct object
                        obj_options_struct = OptionStruct()
                        
                        if (tmp_sub_list[i][1][0][0] == "OptionName") and (
                            tmp_sub_list[i][1][1][0] == "VoucherSN") and (
                            tmp_sub_list[i][1][2][0] == "State") and (
                            tmp_sub_list[i][1][3][0] == "Mode") and (
                            tmp_sub_list[i][1][4][0] == "StartDate") and (
                            tmp_sub_list[i][1][5][0] == "ExpirationDate") and (
                            tmp_sub_list[i][1][6][0] == "IsTransferable"):
                            
                            # save OptionStruct data
                            obj_options_struct.OptionName = tmp_sub_list[i][1][0][1]
                            obj_options_struct.VoucherSN = tmp_sub_list[i][1][1][1]
                            obj_options_struct.State = tmp_sub_list[i][1][2][1]
                            obj_options_struct.Mode = tmp_sub_list[i][1][3][1]
                            obj_options_struct.StartDate = tmp_sub_list[i][1][4][1]
                            obj_options_struct.ExpirationDate = tmp_sub_list[i][1][5][1]
                            obj_options_struct.IsTransferable = tmp_sub_list[i][1][6][1]
                            
                        else:
                            log.debug_err("invalid GetOptionsResponse  element:",
                                          tmp_sub_list[i][1][0][0],
                                          tmp_sub_list[i][1][1][0],
                                          tmp_sub_list[i][1][2][0],
                                          tmp_sub_list[i][1][3][0],
                                          tmp_sub_list[i][1][4][0],
                                          tmp_sub_list[i][1][5][0],
                                          tmp_sub_list[i][1][6][0])
    
                            return VERIFY_FAIL
                        
                        # append OptionStruct data to OptionList
                        self.result.OptionList.append(obj_options_struct)
                    else:
                        log.debug_err("invalid OptionList element ,",
                                       tmp_sub_list[i][0],tmp_sub_list[i][1])
                        return VERIFY_FAIL
        else:
            log.debug_err("invalid GetOptionsResponse parameter:", tmp_list[0])
        
        return VERIFY_SUC

    def check_upload_response_struct(self, element):
        """
        check UploadResponse struct whether adhere to specification,
        and get some user useful values
        """
        log.debug_info("UploadResponse message")
        
        # create UploadResponse object
        self.result = UploadResponse()
        
        
        # parse whole structure
        ret_list = parse.get_children_value(element)
        
        if CHECK_PARAMETERS_INTEGRALITY == 1:
            if len(ret_list) != 3:
                log.debug_err("Incomplete UploadResponse struct:",ret_list)
                return VERIFY_FAIL
        
        for i in range(len(ret_list)):
            if ret_list[i][0] == "Status":
                self.result.Status = ret_list[i][1]
            elif ret_list[i][0] == "StartTime":
                self.result.StartTime = ret_list[i][1]
            elif ret_list[i][0] == "CompleteTime":
                self.result.CompleteTime = ret_list[i][1]
            else:
                log.debug_err("invalid UploadResponse parameter: ", ret_list[i][0])
        
        return VERIFY_SUC
    
    def check_get_all_queued_transfers_response_struct(self, element):
        """
        check GetAllQueuedTransferResponse struct whether adhere to specification,
        and get some user useful values
        """
        log.debug_info("GetAllQueueTransferResponse message")
        
        # create GetallQueuedTransferResponse object
        self.result = GetAllQueuedTransfersResponse()
        
        
        # parse whole structure
        ret_list = parse.get_children_value(element)
        
        
        if CHECK_PARAMETERS_INTEGRALITY == 1:
            if len(ret_list) != 1:
                log.debug_err("Incomplete GetAllQueueTransferResponse struct:",ret_list)
                return VERIFY_FAIL
        
        tmp_list = ret_list[0]
        if tmp_list[0] == "TransferList":
            if type(tmp_list[1]) == types.ListType:
                tmp_sub_list = tmp_list[1]
                
                if CHECK_ARRAY_SIZE == 1:
                    # get defined array size
                    get_all_queued_transfer_resp_list_len = \
                        self.get_array_size(element, "TransferList")
                        
                    if len(tmp_sub_list) != get_all_queued_transfer_resp_list_len:
                        log.debug_err("invalid AllQueuedTransferStruct,the defined array size is ",
                                      get_all_queued_transfer_resp_list_len,
                                      "but the number of array element is",
                                      len(tmp_sub_list))
                        return VERIFY_FAIL
                    
                for i in range(len(tmp_sub_list)):
                    if (tmp_sub_list[i][0] == "AllQueuedTransferStruct") and (
                        type(tmp_sub_list[i][1]) == types.ListType):
                        
                        # create AllQueuedTransferStruct object
                        obj_all_queued_transfer_struct = AllQueuedTransferStruct()
                        
                        if (tmp_sub_list[i][1][0][0] == "CommandKey") and (
                            tmp_sub_list[i][1][1][0] == "State") and (
                            tmp_sub_list[i][1][2][0] == "IsDownload") and (
                            tmp_sub_list[i][1][3][0] == "FileType") and (
                            tmp_sub_list[i][1][4][0] == "FileSize") and (
                            tmp_sub_list[i][1][5][0] == "TargetFileName"):
                            
                            # save AllQueuedTransferStruct data
                            obj_all_queued_transfer_struct.CommandKey = tmp_sub_list[i][1][0][1]
                            obj_all_queued_transfer_struct.State = tmp_sub_list[i][1][1][1]
                            obj_all_queued_transfer_struct.IsDownload = tmp_sub_list[i][1][2][1]
                            obj_all_queued_transfer_struct.FileType = tmp_sub_list[i][1][3][1]
                            obj_all_queued_transfer_struct.FileSize = tmp_sub_list[i][1][4][1]
                            obj_all_queued_transfer_struct.TargetFileName = tmp_sub_list[i][1][5][1]
                            
                        else:
                            log.debug_err("invalid AllQueuedTransferStruct element:",
                                          tmp_sub_list[i][1][0][0],
                                          tmp_sub_list[i][1][1][0],
                                          tmp_sub_list[i][1][2][0],
                                          tmp_sub_list[i][1][3][0],
                                          tmp_sub_list[i][1][4][0],
                                          tmp_sub_list[i][1][5][0])
                            return VERIFY_FAIL
                        
                        # append AllQueuedTransferStruct to TransferList
                        self.result.TransferList.append(obj_all_queued_transfer_struct)
                    else:
                        log.debug_err("invalid TransferList element ,",
                                      tmp_sub_list[i][0],tmp_sub_list[i][1])
                        return VERIFY_FAIL
        else:
            log.debug_err("invalid GetQueuedTransferResponse parameter:", tmp_list[0])
        
        return VERIFY_SUC
    

    def check_kicked_struct(self, element):
        """
        check Kicked struct whether adhere to specification,
        and get some user useful values
        """
        log.debug_info("Kicked message")
        
        # create Kicked object
        self.result = Kicked()
        
        
        # parse whole structure
        ret_list = parse.get_children_value(element)
        
        if CHECK_PARAMETERS_INTEGRALITY == 1:
            if len(ret_list) != NUM_OF_KICKED_PARAMETERS:
                log.debug_err("Incomplete Kicked struct:",ret_list)
                return VERIFY_FAIL
        
        for i in range(len(ret_list)):
            if ret_list[i][0] == "Command":
                self.result.Command = ret_list[i][1]
            elif ret_list[i][0] == "Referer":
                self.result.Referer = ret_list[i][1]
            elif ret_list[i][0] == "Arg":
                self.result.Arg = ret_list[i][1]
            elif ret_list[i][0] == "Next":
                self.result.Next = ret_list[i][1]
            else:
                log.debug_err("invalid Kicked parameter:",ret_list[0][0])
                return VERIFY_FAIL
        
        return VERIFY_SUC
    
    def check_request_download_struct(self, element):
        """
        check RequestDownload struct whether adhere to specification,
        and get some user useful values
        """
        log.debug_info("RequestDownload message")
        
        # create RequestDownload object
        self.result = RequestDownload()
        
        
        # parse whole structure
        ret_list = parse.get_children_value(element)
        
        
        if CHECK_PARAMETERS_INTEGRALITY == 1:
            if len(ret_list) != 2:
                log.debug_err("Incomplete RequestDownload struct:",ret_list)
                return VERIFY_FAIL
        
        for i in range(len(ret_list)):
            tmp_list = ret_list[i]
            
            if tmp_list[0] == "FileType":
                self.result.FileType = tmp_list[1]
                
            elif tmp_list[0] == "FileTypeArg":
                if type(tmp_list[1]) == types.ListType:
                    
                    tmp_sub_list = tmp_list[1]
                    if CHECK_ARRAY_SIZE == 1:
                        request_download_filetype_arg_list_len = \
                            self.get_array_size(element, "FileTypeArg")
                        
                        if len(tmp_sub_list) != request_download_filetype_arg_list_len:
                            log.debug_err("invalid RequestDownload FileTypeArg struct, \
                                          the defined array size is ",
                                          request_download_filetype_arg_list_len,
                                          "but the number of array element is",
                                          len(tmp_sub_list))
                            return VERIFY_FAIL
                    for j in range(len(tmp_sub_list)):
                        if (type(tmp_sub_list[j][1]) == types.ListType) and (
                            tmp_sub_list[j][0] == "ArgStruct"):
                            
                            # create ArgStruct object
                            obj_arg_struct = ArgStruct()
                            
                            if (tmp_sub_list[j][1][0][0] == "Name") and (
                                tmp_sub_list[j][1][1][0] == "Value"):
                                
                                # save ArgStruct date
                                obj_arg_struct.Name = tmp_sub_list[j][1][0][1]
                                obj_arg_struct.Value = tmp_sub_list[j][1][1][1]
                                
                            else:
                                log.debug_err("invalid ArgStruct:",
                                               tmp_sub_list[j][1][0][0],
                                               tmp_sub_list[j][1][1][0])
                                return VERIFY_FAIL
                            
                            # append ArgStruct to FileTypeArg
                            self.result.FileTypeArg.append(obj_arg_struct)
                else:
                    log.debug_err("invalid FileTypeArg paramter,it should have sub element")
            else:
                log.debug_err("invalid RequestDownload parameter:",ret_list[0][0])
                return VERIFY_FAIL
        
        return VERIFY_SUC

    def check_DU_state_change_complete_struct(self, element):
        """
        check DUStateChangeComplete struct whether adhere to specification,
        and get some user useful values
        """
        log.debug_info("DUStateChangeComplete useful message")
        
        # create DUStateChangeComplete object
        self.result = DUStateChangeComplete()
        
        
        # parse whole structure
        ret_list = parse.get_children_value(element)
        
        if CHECK_PARAMETERS_INTEGRALITY == 1:
            if len(ret_list) != 2:
                log.debug_err("Incomplete DUStateChangeComplete struct:", ret_list)
                return VERIFY_FAIL
            
        for i in range(len(ret_list)):
            tmp_list = ret_list[i]
            if tmp_list[0] == "Results":
                if type(tmp_list[1]) == types.ListType:
                    tmp_sub_list = tmp_list[1]
                    
                    if CHECK_ARRAY_SIZE == 1:
                        # get defined array size
                        DU_state_change_complete_results_list_len = \
                            self.get_array_size(element, "Results")
                        
                        if len(tmp_sub_list) != DU_state_change_complete_results_list_len:
                            log.debug_err("invalid Results struct,the defined array size is ",
                                          DU_state_change_complete_results_list_len,
                                          "but the number of array element is",
                                          len(tmp_sub_list))
                            return VERIFY_FAIL
                        
                    for j in range(len(tmp_sub_list)):
                        if (type(tmp_sub_list[j][1]) == types.ListType) and (
                            tmp_sub_list[j][0] == "OpResultStruct"):
                            
                            # create OpResultStruct object to save parsed data
                            obj_op_result_struct = OpResultStruct()
                            obj_op_result_struct.Fault = FaultStruct()
                            
                            if (tmp_sub_list[j][1][0][0] == "UUID") and (
                                tmp_sub_list[j][1][1][0] == "DeploymentUnitRef") and (
                                tmp_sub_list[j][1][2][0] == "Version") and (
                                tmp_sub_list[j][1][3][0] == "CurrentState") and (
                                tmp_sub_list[j][1][4][0] == "Resolved") and (
                                tmp_sub_list[j][1][5][0] == "ExecutionUnitRefList") and (
                                tmp_sub_list[j][1][6][0] == "StartTime") and (
                                tmp_sub_list[j][1][7][0] == "CompleteTime") and (
                                tmp_sub_list[j][1][8][0] == "Fault"):
                                
                                fault_list = tmp_sub_list[j][1][8][1]
                                if (fault_list[0][0] == "FaultCode") and (
                                    fault_list[1][0] == "FaultString"):
                                    
                                    obj_op_result_struct.Fault.FaultCode = fault_list[0][1]
                                    obj_op_result_struct.Fault.FaultString = fault_list[1][1]
                                    
                                else:
                                    log.debug_err("invalid fault struct:",
                                                  fault_list[0][0],
                                                  fault_list[1][0])
                                
                                obj_op_result_struct.UUID = tmp_sub_list[j][1][0][1]
                                obj_op_result_struct.DeploymentUnitRef = tmp_sub_list[j][1][1][1]
                                obj_op_result_struct.Version = tmp_sub_list[j][1][2][1]
                                obj_op_result_struct.CurrentState = tmp_sub_list[j][1][3][1]
                                obj_op_result_struct.Resolved = tmp_sub_list[j][1][4][1]
                                obj_op_result_struct.ExecutionUnitRefList = tmp_sub_list[j][1][5][1]
                                obj_op_result_struct.StartTime = tmp_sub_list[j][1][6][1]
                                obj_op_result_struct.CompleteTime = tmp_sub_list[j][1][7][1]
                                
                            else:
                                log.debug_err("invalid Results in DUStateChangeComplete:",
                                                tmp_sub_list[j][1][0][0],tmp_sub_list[j][1][1][0],
                                                tmp_sub_list[j][1][2][0],tmp_sub_list[j][1][3][0],
                                                tmp_sub_list[j][1][4][0],tmp_sub_list[j][1][5][0],
                                                tmp_sub_list[j][1][6][0],tmp_sub_list[j][1][7][0],
                                                tmp_sub_list[j][1][8][0])
                                
                                return VERIFY_FAIL
                            
                            # append OpResultStruct to Results
                            self.result.Results.append(obj_op_result_struct)
                        else:
                            log.debug_err("invalid Results struct:",
                                          tmp_sub_list[j][0],tmp_sub_list[j][1])
                            return VERIFY_FAIL
                    
            elif tmp_list[0] == "CommandKey":
                self.result.CommandKey = tmp_list[1]
            else:
                log.debug_err("invalid DUStateChangeComplete parameter:", tmp_list[0])
                return VERIFY_FAIL
        
        return VERIFY_SUC
    
    def check_autonomous_DU_state_change_complete_struct(self, element):
        """
        check AutonomousDUStateChangeComplete struct whether adhere to specification,
        and get some user useful values
        """
        log.debug_info("AutonomousDUStateChangeComplete message")
        
        # create AutonomousDUStateChangeComplete object to save parsed result
        self.result = AutonomousDUStateChangeComplete()
        
        
        # parse whole structure
        ret_list = parse.get_children_value(element)
        
        
        if CHECK_PARAMETERS_INTEGRALITY == 1:
            if len(ret_list) != 1:
                log.debug_err("Incomplete AutonomousDUStateChangeComplete struct:", ret_list)
                return VERIFY_FAIL
        
        for i in range(len(ret_list)):
            tmp_list = ret_list[i]
            if tmp_list[0] == "Results":
                if type(tmp_list[1]) == types.ListType:
                    tmp_sub_list = tmp_list[1]
                    
                    if CHECK_ARRAY_SIZE == 1:
                        # get defined array size
                        autonomous_DU_state_change_complete_results_list_len = \
                            self.get_array_size(element, "Results")
                        
                        if len(tmp_sub_list) != autonomous_DU_state_change_complete_results_list_len:
                            log.debug_err("invalid Results struct,the defined array size is ",
                                          autonomous_DU_state_change_complete_results_list_len,
                                          "but the number of array element is",
                                          len(tmp_sub_list))
                            return VERIFY_FAIL
                        
                    for j in range(len(tmp_sub_list)):
                        if (type(tmp_sub_list[j][1]) == types.ListType) and (
                            tmp_sub_list[j][0] == "AutonOpResultStruct"):
                            
                            # create AutonOpResultStruct object to save parsed data
                            obj_auton_op_result_struct = AutonOpResultStruct()
                            obj_auton_op_result_struct.Fault = FaultStruct()
                                
                            if (tmp_sub_list[j][1][0][0] == "UUID") and (
                                tmp_sub_list[j][1][1][0] == "DeploymentUnitRef") and (
                                tmp_sub_list[j][1][2][0] == "Version") and (
                                tmp_sub_list[j][1][3][0] == "CurrentState") and (
                                tmp_sub_list[j][1][4][0] == "Resolved") and (
                                tmp_sub_list[j][1][5][0] == "ExecutionUnitRefList") and (
                                tmp_sub_list[j][1][6][0] == "StartTime") and (
                                tmp_sub_list[j][1][7][0] == "CompleteTime") and (
                                tmp_sub_list[j][1][8][0] == "Fault") and (
                                tmp_sub_list[j][1][9][0] == "OperationPerformed"):
                                
                                fault_list = tmp_sub_list[j][1][8][1]
                                if (fault_list[0][0] == "FaultCode") and (
                                    fault_list[1][0] == "FaultString"):
                                    
                                    obj_auton_op_result_struct.Fault.FaultCode = fault_list[0][1]
                                    obj_auton_op_result_struct.Fault.FaultString = fault_list[1][1]
                                    
                                else:
                                    log.debug_err("invalid fault struct:",
                                                  fault_list[0][0],
                                                  fault_list[1][0])
                                
                                obj_auton_op_result_struct.UUID = tmp_sub_list[j][1][0][1]
                                obj_auton_op_result_struct.DeploymentUnitRef = tmp_sub_list[j][1][1][1]
                                obj_auton_op_result_struct.Version = tmp_sub_list[j][1][2][1]
                                obj_auton_op_result_struct.CurrentState = tmp_sub_list[j][1][3][1]
                                obj_auton_op_result_struct.Resolved = tmp_sub_list[j][1][4][1]
                                obj_auton_op_result_struct.ExecutionUnitRefList = tmp_sub_list[j][1][5][1]
                                obj_auton_op_result_struct.StartTime = tmp_sub_list[j][1][6][1]
                                obj_auton_op_result_struct.CompleteTime = tmp_sub_list[j][1][7][1]
                                obj_auton_op_result_struct.OperationPerformed = tmp_sub_list[j][1][9][1]
                                
                            else:
                                log.debug_err("invalid Results in DUStateChangeComplete:",
                                                tmp_sub_list[j][1][0][0],tmp_sub_list[j][1][1][0],
                                                tmp_sub_list[j][1][2][0],tmp_sub_list[j][1][3][0],
                                                tmp_sub_list[j][1][4][0],tmp_sub_list[j][1][5][0],
                                                tmp_sub_list[j][1][6][0],tmp_sub_list[j][1][7][0],
                                                tmp_sub_list[j][1][8][0],tmp_sub_list[j][1][9][0])
                                
                                return VERIFY_FAIL
                            
                            # append AutonOpResultStruct to Results
                            self.result.Results.append(obj_auton_op_result_struct)
                            
                        else:
                            log.debug_err("invalid Results struct:",
                                           tmp_sub_list[j][0],
                                           tmp_sub_list[j][1])
                            return VERIFY_FAIL
                        
            else:
                log.debug_err("invalid AutonmouseDUStateChangeComplete parameter:",
                              tmp_list[0])
                return VERIFY_FAIL
        
        return VERIFY_SUC
    
    
    def check_no_parameter_response_struct(self, element):
        """
        check response message have no parameter whether adhere to specification
        """
        log.debug_info("no paramete response message")
        
        # parse whole structure
        ret_list = parse.get_children_value(element)
        
        
        if ret_list != None:
            log.debug_err("invalid no paramete response struct:", ret_list)
            return VERIFY_FAIL
        
        return VERIFY_SUC
    

    def check_fault_struct(self, element):
        """
        check Fault struct whether adhere to specification,
        and get some user useful values
        """
        log.debug_info("Fault message")
        
        # create Fault object to save parsed results
        self.result = Fault()
        
        # cwmp:Fault tag
        CWMP_FAULT_TAG = self.cwmp_namespace_prefix + "Fault"
       
        # parse whole structure
        ret_list = parse.get_children_value(element)
        
        if CHECK_PARAMETERS_INTEGRALITY == 1:
            if len(ret_list) != NUM_OF_FAULT_PARAMETERS:
                log.debug_err("Incomplete Fault struct:", ret_list)
                return VERIFY_FAIL
        
        for i in range(len(ret_list)):
            tmp_list = ret_list[i]
            
            if tmp_list[0] == "faultcode":
                self.result.faultcode = tmp_list[1]
                
            elif tmp_list[0] == "faultstring":
                self.result.faultstring = tmp_list[1]
                
            elif tmp_list[0] == "detail":
                if (len(tmp_list[1]) == 1 and
                    tmp_list[1][0][0] == CWMP_FAULT_TAG):
                    
                    # create CWMPFaultStruct object
                    self.result.detail = CWMPFaultStruct()
                    
                    tmp_sub_list = tmp_list[1][0][1]
                    if len(tmp_sub_list) == 2:
                        
                        if (tmp_sub_list[0][0] == "FaultCode") and (
                            tmp_sub_list[1][0] == "FaultString"):
                            
                            self.result.detail.FaultCode = tmp_sub_list[0][1]
                            self.result.detail.FaultString = tmp_sub_list[1][1]
                        else:
                            log.debug_err("invalid detail struct:",
                                           tmp_sub_list[j][0])
                    elif len(tmp_sub_list) >= 3:
                        if (tmp_sub_list[0][0] == "FaultCode") and (
                            tmp_sub_list[1][0] == "FaultString"):
                            
                            self.result.detail.FaultCode = tmp_sub_list[0][1]
                            self.result.detail.FaultString = tmp_sub_list[1][1]
                        else:
                            log.debug_err("invalid detail struct:",
                                          tmp_sub_list[j][0])
                            
                        for j in range(2,len(tmp_sub_list)):
                            # create SetParameterValuesFaultStruct object
                            obj_set_para_values_fault_struct = SetParameterValuesFaultStruct()
                            
                            if tmp_sub_list[j][0] == "SetParameterValuesFault":
                                if len(tmp_sub_list[j][1]) == 1:
                                    if tmp_sub_list[j][1][0][0] == "ParameterName":
                                        obj_set_para_values_fault_struct.ParameterName = \
                                                              tmp_sub_list[j][1][0][1]
                                    else:
                                        log.debug_err("invalid setparametervaluesfault struct:",
                                                        tmp_sub_list[j][1][0][0])
                                        return VERIFY_FAIL
                                        
                                else:
                                    if (tmp_sub_list[j][1][0][0] == "ParameterName") and (
                                        tmp_sub_list[j][1][1][0] == "FaultCode") and (
                                        tmp_sub_list[j][1][2][0] == "FaultString"):
                                        
                                        obj_set_para_values_fault_struct.ParameterName = \
                                                              tmp_sub_list[j][1][0][1]
                                        obj_set_para_values_fault_struct.FaultCode = \
                                                              tmp_sub_list[j][1][1][1]
                                        obj_set_para_values_fault_struct.FaultString = \
                                                              tmp_sub_list[j][1][2][1]
                                        
                                    else:
                                        log.debug_err("invalid setparametervaluesfault struct:",
                                                        tmp_sub_list[j][1][0][0],
                                                        tmp_sub_list[j][1][1][0],
                                                        tmp_sub_list[j][1][2][0])
                                        return VERIFY_FAIL
                            
                            else:
                                log.debug_err("invalid detail struct:",
                                               tmp_sub_list[j][0])
                                return VERIFY_FAIL
                            
                            self.result.detail.SetParameterValuesFaultList.append(
                                                    obj_set_para_values_fault_struct)
                    else:
                        log.debug_err("invalid detail fault struct, the paramenter less than two.")
                        return VERIFY_FAIL
                    
                else:
                    log.debug_err("invalid detail struct:", tmp_list[1][0][0])
                    return VERIFY_FAIL
            else:
                log.debug_err("invalid fault parameters", tmp_list[0])
                return VERIFY_FAIL
        
        return VERIFY_SUC

    
    def get_array_size(self, element, array_parents_name):
        """
        get array size of array_parents_name's array type struct,if don't find,
        return None
        """
        ret_attrib = parse.get_element_attribute(element, array_parents_name)
        pat = '\[[0-9]+\]'
        for attrib in ret_attrib.values():
            # find "[num]"
            ret_findall = re.findall(pat, attrib)
            if len(ret_findall) == 1:
                # trim '['and']',convert string num to int
                return int(ret_findall[0][1:-1])
            else:
                return None



# test	
def test(rpc_flag, xml_src):
    #  create an instance of class and binding all object methods to varialbles
    #  then we don't need to create instance everytime when we call the class's method
    try:
        g_verify
    except NameError:
        g_verify = Verify()
        
        check_soap_msg = g_verify.check_soap_msg
    
    print_flag = rpc_flag
    ret = check_soap_msg(xml_src)
    print ret
    print "soap header cwmp id:", g_verify.soap_header_cwmp_id
    print "cur cwmp version:", g_verify.cur_cwmp_version
    print "cur RPC name is :", g_verify.cur_RPC_name
    if print_flag == "inform":
        print "inform_currenttime: ", g_verify.result.CurrentTime
        print "inform_retrycount: ", g_verify.result.RetryCount
        print "inform_device_manufacturer: ", g_verify.result.DeviceId.Manufacturer
        print "inform_device_OUI: ", g_verify.result.DeviceId.OUI
        print "inform_device_productclass: ", g_verify.result.DeviceId.ProductClass
        print "inform_device_serialnumber: ", g_verify.result.DeviceId.SerialNumber
        for i in range(len(g_verify.result.Event)):
            print "inform_event_commandkey: ", g_verify.result.Event[i].CommandKey
            print "inform_event_eventcode: ", g_verify.result.Event[i].EventCode
        
        print "inform_maxenvelopes: ", g_verify.result.MaxEnvelopes
        print "inform_parameterlist:"
        for i in range(len(g_verify.result.ParameterList)):
            print g_verify.result.ParameterList[i].Name, \
                  g_verify.result.ParameterList[i].Value, \
                  g_verify.result.ParameterList[i].Value_type
        
        print "inform_device_connectionrequestURL:", g_verify.result.DeviceId.ConnectionRequestURL
        print "inform_device_hardwareversion: ", g_verify.result.DeviceId.Hardwareversion
        print "inform_device_softwareversion: ", g_verify.result.DeviceId.Softwareversion
    elif print_flag == "transfer_complete":
        print "transfer_complete_commandkey: ", g_verify.result.CommandKey
        print "transfer_complete_faultcode: ", g_verify.result.FaultStruct.FaultCode
        print "transfer_complete_faultstring: ", g_verify.result.FaultStruct.FaultString
        print "transfer_complete_starttime: ", g_verify.result.StartTime
        print "transfer_complete_completetime: ", g_verify.result.CompleteTime
    elif print_flag == "get_RPC_Method_RESP":
        print "RPC methods list:", g_verify.result.MethodList
    elif print_flag == "get_parameter_Names_RESP":
        print "get parameter names resp list:"
        for i in range(len(g_verify.result.ParameterList)):
            print g_verify.result.ParameterList[i].Name, \
                  g_verify.result.ParameterList[i].Writable
    elif print_flag == "set_parameter_values_RESP":
        print "set parameter values resp status:", g_verify.result.Status
    elif print_flag == "get_parameter_values_RESP":
        print "get parameter values resp list:"
        for i in range(len(g_verify.result.ParameterList)):
            print g_verify.result.ParameterList[i].Name, \
                  g_verify.result.ParameterList[i].Value, \
                  g_verify.result.ParameterList[i].Value_type
        
    elif print_flag == "get_parameter_attrib_RESP":
        print "get parameter attrib resp list:"
        for i in range(len(g_verify.result.ParameterList)):
            print g_verify.result.ParameterList[i].Name, \
                  g_verify.result.ParameterList[i].Notification, \
                  g_verify.result.ParameterList[i].AccessList
        
    elif print_flag == "add_object_RESP":
        print "add object resp instance number:", g_verify.result.InstanceNumber
        print "add object resp status:", g_verify.result.Status
    elif print_flag == "delete_object_RESP":
        print "delete object resp status:", g_verify.result.Status
    elif print_flag == "download_RESP":
        print "download resp status:", g_verify.result.Status
        print "download resp starttime:", g_verify.result.StartTime
        print "download resp completetime:", g_verify.result.CompleteTime
    elif print_flag == "upload_RESP":
        print "upload resp status:", g_verify.result.Status
        print "upload resp starttime:", g_verify.result.StartTime
        print "upload resp completetime:", g_verify.result.CompleteTime
    
    elif print_flag == "Fault":
        print "fault code:", g_verify.result.faultcode
        print "fault string:", g_verify.result.faultstring
        print "detail fault code", g_verify.result.detail.FaultCode
        print "detail fault string:", g_verify.result.detail.FaultString
        print "detail SetParameterValuesFault list:"
        for i in range(len(g_verify.result.detail.SetParameterValuesFaultList)):
            print g_verify.result.detail.SetParameterValuesFaultList[i].ParameterName, \
                  g_verify.result.detail.SetParameterValuesFaultList[i].FaultCode, \
                  g_verify.result.detail.SetParameterValuesFaultList[i].FaultString
        
    else:
        pass
    
if __name__ == '__main__':
    
    test("Fault", open("F:/fault.txt").read())
    