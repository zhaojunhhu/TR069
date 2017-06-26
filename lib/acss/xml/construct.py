#coding:utf-8


# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: construct
#  function: construct soap envelope for  RPC methods' request and  response
#  Author: ATT development group
#  version: V1.0
#  date: 2012.09.04
#  change log:
#  lana     20120904     created
#
# ***************************************************************************

import random
from xml.etree import ElementTree
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring

import TR069.lib.common.logs.log as log 
from TR069.lib.common.rpcstruct import *


CONSTRUCT_SUC = 0
CONSTRUCT_FAIL = -1

# cwmp prefix
CWMP_NS_PREFIX = "cwmp:"

# SOAP_ENV prefix
SOAP_ENV_NS_PREFIX = "SOAP-ENV:" 

# element attrib is string 
STRING_ATTRIB = {'xsi:type':'xsd:string'}


# soap array type
SOAP_ARRAY_TYPR = "SOAP-ENC:arrayType"


# soap header cwmp_id random num
CWMP_ID_RANDOM_NUM_START = 1
CWMP_ID_RANDOM_NUM_END = 1000000

# Baseline RPC message
RPC_GET_RPC_METHODS_TAG = 'GetRPCMethods'
RPC_GET_RPC_METHODS_RES_TAG = 'GetRPCMethodsResponse'

# CPE methods,RPC request name tag
RPC_SET_PARA_VALUES_TAG = 'SetParameterValues'
RPC_GET_PARA_VALUES_TAG = 'GetParameterValues'
RPC_GET_PARA_NAMES_TAG = 'GetParameterNames'
RPC_SET_PARA_ATTRIB_TAG = 'SetParameterAttributes'
RPC_GET_PARA_ATTRIB_TAG = 'GetParameterAttributes'
RPC_ADD_OBJ_TAG = 'AddObject'
RPC_DEL_OBJ_TAG = 'DeleteObject'
RPC_DOWNLOAD_TAG = 'Download'
RPC_REBOOT_TAG = 'Reboot'

# optional CPE methods, RPC request name tag
RPC_GET_QUEUED_TRANSFERS_TAG = 'GetQueuedTransfers'
RPC_SCHEDULE_INFORM_TAG = 'ScheduleInform'
RPC_SET_VOUCHERS_TAG = 'SetVouchers'
RPC_GET_OPTIONS_TAG = 'GetOptions'
RPC_UPLOAD_TAG = 'Upload'
RPC_FACTORY_RESET_TAG = 'FactoryReset'
RPC_GET_ALL_QUEUED_TRANSFERS_TAG = 'GetAllQueuedTransfers'
RPC_SCHEDULE_DOWNLOAD_TAG = 'ScheduleDownload'
RPC_CANCEL_TRANSFER_TAG = 'CancelTransfer'
RPC_CHANGE_DUSTATE_TAG = 'ChangeDUState'

# ACS methods, RPC response name tag
RPC_INFORM_RES_TAG = 'InformResponse'
RPC_TRANSFER_COMPLETE_RES_TAG = 'TransferCompleteResponse'
RPC_AUTONOMOUS_TRANSFER_COMPLETE_RES_TAG = 'AutonomousTransferCompleteResponse'

# optional ACS methods, RPC response name tag
RPC_KICKED_RES_TAG = 'KickedResponse'
RPC_REQUEST_DOWNLOAD_RES_TAG = 'RequestDownloadResponse'
RPC_DUSTATE_CHANGE_COMPLETE_RES_TAG = 'DUStateChangeCompleteResponse'
RPC_AUTONOMOUS_DUSTATE_CHANGE_COMPLETE_RES_TAG = 'AutonomousDUStateChangeCompleteResponse'

# fault message
RPC_FAULT_TAG = 'Fault'




class Construct:
    """
    construct soap envelope of xml structure
    """
    
    def __init__(self):
        """
        do some initial
        """
        
        # create an empty tree
        self.soap = ElementTree()
        
        # this variable used to save created soap envelpoe's xml content
        self.str_xml = ""
        
    def create_soap_envelope(self, rpc_name, cwmp_version="cwmp-1-0", rpc_args="", cwmp_id=""):
        """
        create soap envelope, and convert the structure to xml
        rpc_name: RPC name need to create
        cwmp_version: CPE supported cwmp version, default is cwmp-1-0
        rpc_args: RPC arguments, default is ""
        """
        
        log.debug_info("create_soap_envelope")
        
        try:
            dict_envelope_attrib = {'xmlns:SOAP-ENV':'http://schemas.xmlsoap.org/soap/envelope/',
                   'xmlns:SOAP-ENC':'http://schemas.xmlsoap.org/soap/encoding/',
                   'xmlns:xsd':'http://www.w3.org/2001/XMLSchema',
                   'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance'}
            
            dict_envelope_attrib['xmlns:cwmp'] = '' + 'urn:dslforum-org:'+ cwmp_version
            
            # create an element
            self.soap_envelope = Element('SOAP-ENV:Envelope', dict_envelope_attrib)
        
            # set root of tree
            self.soap._setroot(self.soap_envelope)
        
            # create sub elemnts of soap_envelop
            self.soap_header = Element('SOAP-ENV:Header')
            self.soap_body = Element('SOAP-ENV:Body')
        
            # add soap_header and soap_body to soap_envelope
            self.soap_envelope.append(self.soap_header)
            self.soap_envelope.append(self.soap_body)
        
            # create sub elements of soap header  
            self.create_soap_header(cwmp_id)
        
            # create sub elements of soap body
            self.create_soap_body(rpc_name, rpc_args)
        
            # convert structure to xml
            self.str_xml = tostring(self.soap_envelope)
            
        except Exception, e:
            
            log.debug_err(e)
            return CONSTRUCT_FAIL, e
        
        return CONSTRUCT_SUC, ""
    
    def create_soap_header(self, header_cwmp_id):
        """
        create soap header
        """
        log.debug_info("create_soap_header")
        
        # create sub element of soap header
        cwmp_id = Element('cwmp:ID', {'SOAP-ENV:mustUnderstand':'1'})
        cwmp_hold_requests = Element('cwmp:HoldRequests', {'SOAP-ENV:mustUnderstand':'1'})
        
        # set sub element's text
        # for cwmp:ID,create random num
        int_rand_num = random.randint(CWMP_ID_RANDOM_NUM_START, CWMP_ID_RANDOM_NUM_END)
        # element cwmp:ID's text need string type
        if header_cwmp_id:
            cwmp_id.text = header_cwmp_id
        else:
            cwmp_id.text = str(int_rand_num)
        
        
        # set cwmp:HoldRequests's text as 0 for default.maybe need to change later.
        cwmp_hold_requests.text = str(0)
        
        # add sub elments to soap_header
        self.soap_header.append(cwmp_id)
        self.soap_header.append(cwmp_hold_requests)
        
        return CONSTRUCT_SUC
    
    def create_soap_body(self, rpc_name, rpc_args):
        """
        create soap body
        """
        log.debug_info("create_soap_body")
        
        
        # create different RPC method structure
        if (rpc_name == RPC_GET_RPC_METHODS_TAG or
            rpc_name == RPC_FACTORY_RESET_TAG or
            rpc_name == RPC_GET_QUEUED_TRANSFERS_TAG or
            rpc_name == RPC_GET_ALL_QUEUED_TRANSFERS_TAG or
            rpc_name == RPC_TRANSFER_COMPLETE_RES_TAG or
            rpc_name == RPC_AUTONOMOUS_TRANSFER_COMPLETE_RES_TAG or
            rpc_name == RPC_REQUEST_DOWNLOAD_RES_TAG or
            rpc_name == RPC_DUSTATE_CHANGE_COMPLETE_RES_TAG or
            rpc_name == RPC_AUTONOMOUS_DUSTATE_CHANGE_COMPLETE_RES_TAG):
            
            self.create_no_parameter_struct(rpc_name)
            
        elif rpc_name == RPC_GET_RPC_METHODS_RES_TAG:
            self.create_get_rpc_methods_res_struct(rpc_args)
            
        elif rpc_name == RPC_SET_PARA_VALUES_TAG:
            self.create_set_parameter_values_struct(rpc_args)
            
        elif rpc_name == RPC_GET_PARA_VALUES_TAG:
            self.create_get_parameter_values_struct(rpc_args)
        
        elif rpc_name == RPC_GET_PARA_NAMES_TAG:
            self.create_get_parameter_names_struct(rpc_args)
            
        elif rpc_name == RPC_SET_PARA_ATTRIB_TAG:
            self.create_set_parameter_attrib_struct(rpc_args)
            
        elif rpc_name == RPC_GET_PARA_ATTRIB_TAG:
            self.create_get_parameter_attrib_struct(rpc_args)
            
        elif rpc_name == RPC_ADD_OBJ_TAG:
            self.create_add_object_struct(rpc_args)
            
        elif rpc_name == RPC_DEL_OBJ_TAG:
            self.create_del_object_struct(rpc_args)
            
        elif rpc_name == RPC_DOWNLOAD_TAG:
            self.create_download_struct(rpc_args)
            
        elif rpc_name == RPC_REBOOT_TAG:
            self.create_reboot_struct(rpc_args)
            
        
        elif rpc_name == RPC_GET_QUEUED_TRANSFERS_TAG:
            self.create_get_queued_transfers_struct(rpc_args)
            
        elif rpc_name == RPC_SCHEDULE_INFORM_TAG:
            self.create_schedule_inform_struct(rpc_args)
            
        elif rpc_name == RPC_SET_VOUCHERS_TAG:
            self.create_set_vouchers_struct(rpc_args)
            
        elif rpc_name == RPC_GET_OPTIONS_TAG:
            self.create_get_options_struct(rpc_args)
            
        elif rpc_name == RPC_UPLOAD_TAG:
            self.create_upload_struct(rpc_args)
            
        elif rpc_name == RPC_GET_ALL_QUEUED_TRANSFERS_TAG:
            self.create_get_all_queued_transfers_struct(rpc_args)
            
        elif rpc_name == RPC_SCHEDULE_DOWNLOAD_TAG:
            self.create_schedule_download_struct(rpc_args)
            
        elif rpc_name == RPC_CANCEL_TRANSFER_TAG:
            self.create_cancel_transfer_struct(rpc_args)
            
        elif rpc_name == RPC_CHANGE_DUSTATE_TAG:
            self.create_change_du_state_struct(rpc_args)
            
        
        elif rpc_name == RPC_INFORM_RES_TAG:
            self.create_inform_res_struct(rpc_args)
            
        
        elif rpc_name == RPC_KICKED_RES_TAG:
            self.create_kicked_res_struct(rpc_args)
            
            
        elif rpc_name == RPC_FAULT_TAG:
            self.create_fault_struct(rpc_args)
            
        else:
            log.debug_err("Now do not support RPC method:" + rpc_name)
            
        return CONSTRUCT_SUC
    
    def create_no_parameter_struct(self, rpc_name):
        """
        create no parameter rpc method struct
        """
        
        # add "cwmp:" before RPC name
        cwmp_rpc_name = CWMP_NS_PREFIX + rpc_name
        
        # create RPC method element
        rpc_name_element = Element(cwmp_rpc_name)
        
        # add RPC method element to soap_body
        self.soap_body.append(rpc_name_element)
        
        return CONSTRUCT_SUC
        
    def create_get_rpc_methods_res_struct(self, rpc_args):
        """
        create GetRPCMethdsResponse struct
        """
        
        # create RPC method element
        rpc_name_element = Element(CWMP_NS_PREFIX+RPC_GET_RPC_METHODS_RES_TAG)
        
        # add RPC method element to soap_body
        self.soap_body.append(rpc_name_element)
        
        # create MethodList element
        method_list_len = len(rpc_args.MethodList)
        method_list_attrib_value = "xsd:string[" + str(method_list_len) + "]"
        method_list_element = Element('MethodList',
                                      {SOAP_ARRAY_TYPR:method_list_attrib_value})
        
        # add MethodList element to rpc_name_element
        rpc_name_element.append(method_list_element)
        
        # add MethodList's sub element
        for i in range(method_list_len):
            SubElement(method_list_element, 'string').text = rpc_args.MethodList[i]
        
        return CONSTRUCT_SUC
    
    def create_set_parameter_values_struct(self, rpc_args):
        """
        create SetParameterValues struct
        """
        
        # create RPC method element
        rpc_name_element = Element(CWMP_NS_PREFIX + RPC_SET_PARA_VALUES_TAG)
        
        # add RPC method element to soap_body
        self.soap_body.append(rpc_name_element)
        
        # create RPC method parameters element
        # first ParameterList element
        parameter_list_len = len(rpc_args.ParameterList)
        parameter_list_attrib_value = "cwmp:ParameterValueStruct[" + str(parameter_list_len) + "]"
        parameter_list_element = Element('ParameterList',
                                         {SOAP_ARRAY_TYPR:parameter_list_attrib_value})
        # create and add ParameterValueStruct element
        for i in range(parameter_list_len):
            paravalue_struct_element = Element("ParameterValueStruct")
            parameter_list_element.append(paravalue_struct_element)
            
            name = rpc_args.ParameterList[i].Name
            name_attrib = STRING_ATTRIB
            
            value = rpc_args.ParameterList[i].Value
            value_type = rpc_args.ParameterList[i].Value_type
            # add  prefix "xsd:"
            value_type = "xsd:" + value_type
            value_attrib = {'xsi:type':value_type}
            
            SubElement(paravalue_struct_element, "Name", name_attrib).text = name
            SubElement(paravalue_struct_element, "Value", value_attrib).text = str(value)
        
        # second ParameterKey element
        parameter_key_element = Element('ParameterKey', STRING_ATTRIB)
        parameter_key_element.text = rpc_args.ParameterKey
        
        # add RPC method parameters element
        rpc_name_element.append(parameter_list_element)
        rpc_name_element.append(parameter_key_element)
        
        return CONSTRUCT_SUC
    
    def create_get_parameter_values_struct(self, rpc_args):
        """
        create GetParameterValues struct
        """
        
        # create RPC method element
        rpc_name_element = Element(CWMP_NS_PREFIX + RPC_GET_PARA_VALUES_TAG)
        
        # add RPC method element to soap_body
        self.soap_body.append(rpc_name_element)
        
        # create ParameterNames element
        parameter_names_len = len(rpc_args.ParameterNames)
        parameter_names_attrib_value = "xsd:string[" + str(parameter_names_len) + "]"
        parameter_names_element = Element('ParameterNames',
                                         {SOAP_ARRAY_TYPR:parameter_names_attrib_value})
        
        # add ParameterNames element to rpc_name_element
        rpc_name_element.append(parameter_names_element)
        
        # add ParameterNames's sub element
        for i in range(parameter_names_len):
            SubElement(parameter_names_element, 'string').text = rpc_args.ParameterNames[i]
        
        
        return CONSTRUCT_SUC
    
    def create_get_parameter_names_struct(self, rpc_args):
        """
        create GetParameterNames struct
        """
        
        # create RPC method element
        rpc_name_element = Element(CWMP_NS_PREFIX + RPC_GET_PARA_NAMES_TAG)
        
        # add RPC method element to soap_body
        self.soap_body.append(rpc_name_element)
        
        # create RPC method parameters element
        SubElement(rpc_name_element, 'ParameterPath').text = rpc_args.ParameterPath
        SubElement(rpc_name_element, 'NextLevel').text = str(rpc_args.NextLevel)
        
        return CONSTRUCT_SUC
    
    def create_set_parameter_attrib_struct(self, rpc_args):
        """
        create SetParameterAttributes struct
        """
        
        # create RPC method element
        rpc_name_element = Element(CWMP_NS_PREFIX + RPC_SET_PARA_ATTRIB_TAG)
        
        # add RPC method element to soap_body
        self.soap_body.append(rpc_name_element)
        
        # create and add RPC method parameters element
        parameter_list_len = len(rpc_args.ParameterList)
        parameter_list_attrib_value = "cwmp:SetParameterAttributesStruct[" + str(parameter_list_len) + "]"
        parameter_list_element = Element('ParameterList',
                                         {SOAP_ARRAY_TYPR:parameter_list_attrib_value})
        
        rpc_name_element.append(parameter_list_element)
        # create and add ParameterValueStruct element
        for i in range(parameter_list_len):
            setpara_attrib_struct_element = Element("SetParameterAttributesStruct")
            parameter_list_element.append(setpara_attrib_struct_element)
            
            name = rpc_args.ParameterList[i].Name
            notification_change = rpc_args.ParameterList[i].NotificationChange
            notifiacation = rpc_args.ParameterList[i].Notification
            accesslist_change = rpc_args.ParameterList[i].AccessListChange
            access_list = rpc_args.ParameterList[i].AccessList
            
            SubElement(setpara_attrib_struct_element, "Name").text = name
            SubElement(setpara_attrib_struct_element, "NotificationChange").text = str(notification_change)
            SubElement(setpara_attrib_struct_element, "Notification").text = str(notifiacation)
            SubElement(setpara_attrib_struct_element, "AccessListChange").text = str(accesslist_change)
            if len(access_list) == 0:
                SubElement(setpara_attrib_struct_element, "AccessList", {'xsi:nil':'true'})
            else:
                access_list_element = Element("AccessList")
                setpara_attrib_struct_element.append(access_list_element)
                for j in range(len(access_list)):
                    SubElement(access_list_element, 'string').text = access_list[j]
            
        return CONSTRUCT_SUC
    
    def create_get_parameter_attrib_struct(self, rpc_args):
        """
        create GetParameterAttributes struct
        """
        
        # create RPC method element
        rpc_name_element = Element(CWMP_NS_PREFIX + RPC_GET_PARA_ATTRIB_TAG)
        
        # add RPC method element to soap_body
        self.soap_body.append(rpc_name_element)
        
        # create ParameterNames element
        parameter_names_len = len(rpc_args.ParameterNames)
        parameter_names_attrib_value = "xsd:string[" + str(parameter_names_len) + "]"
        parameter_names_element = Element('ParameterNames',
                                         {SOAP_ARRAY_TYPR:parameter_names_attrib_value})
        
        # add ParameterNames element to rpc_name_element
        rpc_name_element.append(parameter_names_element)
        
        # add ParameterNames's sub element
        for i in range(parameter_names_len):
            SubElement(parameter_names_element, 'string').text = rpc_args.ParameterNames[i]
        
        
        return CONSTRUCT_SUC
    
    def create_add_object_struct(self, rpc_args):
        """
        create AddObject struct
        """
        
        # create RPC method element
        rpc_name_element = Element(CWMP_NS_PREFIX + RPC_ADD_OBJ_TAG)
        
        # add RPC method element to soap_body
        self.soap_body.append(rpc_name_element)
        
        # create RPC method parameters element
        SubElement(rpc_name_element, 'ObjectName').text = rpc_args.ObjectName
        if rpc_args.ParameterKey != "":
            SubElement(rpc_name_element, 'ParameterKey').text = rpc_args.ParameterKey
        else:
            SubElement(rpc_name_element, 'ParameterKey', {'xsi:nil':'true'})
        
        return CONSTRUCT_SUC
    
    def create_del_object_struct(self, rpc_args):
        """
        create DeleteObject struct
        """
        
        # create RPC method element
        rpc_name_element = Element(CWMP_NS_PREFIX + RPC_DEL_OBJ_TAG)
        
        # add RPC method element to soap_body
        self.soap_body.append(rpc_name_element)
        
        # create RPC method parameters element
        SubElement(rpc_name_element, 'ObjectName').text = rpc_args.ObjectName
        if rpc_args.ParameterKey != "":
            SubElement(rpc_name_element, 'ParameterKey').text = rpc_args.ParameterKey
        else:
            SubElement(rpc_name_element, 'ParameterKey', {'xsi:nil':'true'})
        
        return CONSTRUCT_SUC
    
    def create_download_struct(self, rpc_args):
        """
        create Download struct
        """
        
        # create RPC method element
        rpc_name_element = Element(CWMP_NS_PREFIX + RPC_DOWNLOAD_TAG)
        
        # add RPC method element to soap_body
        self.soap_body.append(rpc_name_element)
        
        # create RPC method parameters element
        if rpc_args.CommandKey != "":
            SubElement(rpc_name_element, 'CommandKey').text = rpc_args.CommandKey
        else:
            SubElement(rpc_name_element, 'CommandKey', {'xsi:nil':'true'})
        SubElement(rpc_name_element, 'FileType').text = rpc_args.FileType
        SubElement(rpc_name_element, 'URL').text = rpc_args.URL
        if rpc_args.Username != "":
            SubElement(rpc_name_element, 'Username').text = rpc_args.Username
        else:
            SubElement(rpc_name_element, 'Username', {'xsi:nil':'true'})
        if rpc_args.Password != "":
            SubElement(rpc_name_element, 'Password').text = rpc_args.Password
        else:
            SubElement(rpc_name_element, 'Password', {'xsi:nil':'true'})
        SubElement(rpc_name_element, 'FileSize').text = str(rpc_args.FileSize)
        SubElement(rpc_name_element, 'TargetFileName').text = rpc_args.TargetFileName
        SubElement(rpc_name_element, 'DelaySeconds').text = str(rpc_args.DelaySeconds)
        if rpc_args.SuccessURL != "":
            SubElement(rpc_name_element, 'SuccessURL').text = rpc_args.SuccessURL
        else:
            SubElement(rpc_name_element, 'SuccessURL', {'xsi:nil':'true'})
        if rpc_args.FailureURL != "":
            SubElement(rpc_name_element, 'FailureURL').text = rpc_args.FailureURL
        else:
            SubElement(rpc_name_element, 'FailureURL', {'xsi:nil':'true'})
        
        return CONSTRUCT_SUC
    
    def create_reboot_struct(self, rpc_args):
        """
        create Reboot struct
        """
        
        # create RPC method element
        rpc_name_element = Element(CWMP_NS_PREFIX + RPC_REBOOT_TAG)
        
        # add RPC method element to soap_body
        self.soap_body.append(rpc_name_element)
        
        # create RPC method parameters element
        if rpc_args.CommandKey != "":
            SubElement(rpc_name_element, 'CommandKey').text = rpc_args.CommandKey
        else:
            SubElement(rpc_name_element, 'CommandKey', {'xsi:nil':'true'})
        
        
        return CONSTRUCT_SUC

    
    def create_schedule_inform_struct(self, rpc_args):
        """
        create ScheduleInform struct
        """
        
        # create RPC method element
        rpc_name_element = Element(CWMP_NS_PREFIX + RPC_SCHEDULE_INFORM_TAG)
        
        # add RPC method element to soap_body
        self.soap_body.append(rpc_name_element)
        
        # create RPC method parameters element
        SubElement(rpc_name_element, 'DelaySeconds').text = str(rpc_args.DelaySeconds)
        
        if rpc_args.CommandKey != "":
            SubElement(rpc_name_element, 'CommandKey').text = rpc_args.CommandKey
        else:
            SubElement(rpc_name_element, 'CommandKey', {'xsi:nil':'true'})
            
        return CONSTRUCT_SUC
    
    def create_set_vouchers_struct(self, rpc_args):
        """
        create SetVouchers struct
        """
        
        # create RPC method element
        rpc_name_element = Element(CWMP_NS_PREFIX + RPC_SET_VOUCHERS_TAG)
        
        # add RPC method element to soap_body
        self.soap_body.append(rpc_name_element)
        
        # create RPC method parameters element
        voucher_list_len = len(rpc_args.VoucherList)
        
        #TODO: need check the struct base64 whether correct or not
        voucher_list_attrib_value = "xsd:base64[" + str(voucher_list_len) + "]"
        voucher_list_element = Element('VoucherList',
                                      {SOAP_ARRAY_TYPR:voucher_list_attrib_value})
        
        # add MethodList element to rpc_name_element
        rpc_name_element.append(voucher_list_element)
        
        # add MethodList's sub element
        for i in range(voucher_list_len):
            SubElement(voucher_list_element, 'base64').text = rpc_args.VoucherList[i]
        
        return CONSTRUCT_SUC
    
    def create_get_options_struct(self, rpc_args):
        """
        create GetOptions struct
        """
        
        # create RPC method element
        rpc_name_element = Element(CWMP_NS_PREFIX + RPC_GET_OPTIONS_TAG)
        
        # add RPC method element to soap_body
        self.soap_body.append(rpc_name_element)
        
        # create RPC method parameters element
        if rpc_args.OptionName != "":
            SubElement(rpc_name_element, 'OptionName').text = rpc_args.OptionName
        else:
            SubElement(rpc_name_element, 'OptionName', {'xsi:nil':'true'})
        
        return CONSTRUCT_SUC
    
    def create_upload_struct(self, rpc_args):
        """
        create Upload struct
        """
        
        # create RPC method element
        rpc_name_element = Element(CWMP_NS_PREFIX + RPC_UPLOAD_TAG)
        
        # add RPC method element to soap_body
        self.soap_body.append(rpc_name_element)
        
        # create RPC method parameters element
        if rpc_args.CommandKey != "":
            SubElement(rpc_name_element, 'CommandKey').text = rpc_args.CommandKey
        else:
            SubElement(rpc_name_element, 'CommandKey', {'xsi:nil':'true'})
        SubElement(rpc_name_element, 'FileType').text = rpc_args.FileType
        SubElement(rpc_name_element, 'URL').text = rpc_args.URL
        if rpc_args.Username != "":
            SubElement(rpc_name_element, 'Username').text = rpc_args.Username
        else:
            SubElement(rpc_name_element, 'Username', {'xsi:nil':'true'})
        if rpc_args.Password != "":
            SubElement(rpc_name_element, 'Password').text = rpc_args.Password
        else:
            SubElement(rpc_name_element, 'Password', {'xsi:nil':'true'})
            
        SubElement(rpc_name_element, 'DelaySeconds').text = str(rpc_args.DelaySeconds)
        
        return CONSTRUCT_SUC
    
    def create_schedule_download_struct(self, rpc_args):
        """
        create ScheduleDownload struct
        """
        
        # create RPC method element
        rpc_name_element = Element(CWMP_NS_PREFIX + RPC_SCHEDULE_DOWNLOAD_TAG)
        
        # add RPC method element to soap_body
        self.soap_body.append(rpc_name_element)
        
        # create RPC method parameters element
        if rpc_args.CommandKey != "":
            SubElement(rpc_name_element, 'CommandKey').text = rpc_args.CommandKey
        else:
            SubElement(rpc_name_element, 'CommandKey', {'xsi:nil':'true'})
        SubElement(rpc_name_element, 'FileType').text = rpc_args.FileType
        SubElement(rpc_name_element, 'URL').text = rpc_args.URL
        if rpc_args.Username != "":
            SubElement(rpc_name_element, 'Username').text = rpc_args.Username
        else:
            SubElement(rpc_name_element, 'Username', {'xsi:nil':'true'})
        if rpc_args.Password != "":
            SubElement(rpc_name_element, 'Password').text = rpc_args.Password
        else:
            SubElement(rpc_name_element, 'Password', {'xsi:nil':'true'})
        SubElement(rpc_name_element, 'FileSize').text = str(rpc_args.FileSize)
        SubElement(rpc_name_element, 'TargetFileName').text = rpc_args.TargetFileName
        
        # create and add TimeWindowList element
        time_window_list_len = len(rpc_args.TimeWindowList)
        time_window_list_attrib_value = "cwmp:TimeWindowStruct[" + str(time_window_list_len) + "]"
        time_window_list_element = Element('TimeWindowList',
                                         {SOAP_ARRAY_TYPR:time_window_list_attrib_value})
        rpc_name_element.append(time_window_list_element)
        
        for i in range(time_window_list_len):
            # create and add TimeWindowStruct
            time_window_struct_element = Element("TimeWindowStruct")
            time_window_list_element.append(time_window_struct_element)
            
            # create and add sub element of TimeWindowStruct
            SubElement(time_window_struct_element, "WindowStart").text = \
                str(rpc_args.TimeWindowList[i].WindowStart)
            SubElement(time_window_struct_element, "WindowEnd").text = \
                str(rpc_args.TimeWindowList[i].WindowEnd)
            SubElement(time_window_struct_element, "WindowMode").text = \
                str(rpc_args.TimeWindowList[i].WindowMode)
            if rpc_args.TimeWindowList[i].UserMessage == "":
                SubElement(time_window_struct_element, "UserMessage")
            else:
                SubElement(time_window_struct_element, "UserMessage").text = \
                    rpc_args.TimeWindowList[i].UserMessage
            SubElement(time_window_struct_element, "MaxRetries").text = \
                str(rpc_args.TimeWindowList[i].MaxRetries)
        
        return CONSTRUCT_SUC
    
    def create_cancel_transfer_struct(self, rpc_args):
        """
        create CancelTransfer struct
        """
        
        # create RPC method element
        rpc_name_element = Element(CWMP_NS_PREFIX + RPC_CANCEL_TRANSFER_TAG)
        
        # add RPC method element to soap_body
        self.soap_body.append(rpc_name_element)
        
        # create RPC method parameters element
        if rpc_args.CommandKey != "":
            SubElement(rpc_name_element, 'CommandKey').text = rpc_args.CommandKey
        else:
            SubElement(rpc_name_element, 'CommandKey', {'xsi:nil':'true'})
        
        return CONSTRUCT_SUC
    
    def create_change_du_state_struct(self, rpc_args):
        """
        create ChangeDUState struct
        """
        
        # create RPC method element
        rpc_name_element = Element(CWMP_NS_PREFIX + RPC_CHANGE_DUSTATE_TAG)
        
        # add RPC method element to soap_body
        self.soap_body.append(rpc_name_element)
        
        # create RPC method parameters element
        operations_len = len(rpc_args.Operations)
        operations_attrib_value = "cwmp:OperationsStruct[" + str(operations_len) + "]"
        operations_element = Element('Operations',
                                         {SOAP_ARRAY_TYPR:operations_attrib_value})
        rpc_name_element.append(operations_element)
        
        # create and add OperationsStruct
        for i in range(operations_len):
            if rpc_args.Operations[i].Name == "InstallOpStruct":
                install_op_struct_element = Element("InstallOpStruct")
                operations_element.append(install_op_struct_element)
                
                # create and add InstallOpStruct sub element
                SubElement(install_op_struct_element, 'URL').text = \
                    rpc_args.Operations[i].URL
                SubElement(install_op_struct_element, 'UUID').text = \
                    rpc_args.Operations[i].UUID
                SubElement(install_op_struct_element, 'Username').text = \
                    rpc_args.Operations[i].Username
                SubElement(install_op_struct_element, 'Password').text = \
                    rpc_args.Operations[i].Password
                SubElement(install_op_struct_element, 'ExecutionEnvRef').text = \
                    rpc_args.Operations[i].ExecutionEnvRef
                
            elif rpc_args.Operations[i].Name == "UninstallOpStruct":
                uninstall_op_struct_element = Element("UninstallOpStruct")
                operations_element.append(uninstall_op_struct_element)
                
                #create and add UninstallOpStruct sub element
                SubElement(uninstall_op_struct_element, 'UUID').text = \
                    rpc_args.Operations[i].UUID
                SubElement(uninstall_op_struct_element, 'Version').text = \
                    rpc_args.Operations[i].Version
                SubElement(uninstall_op_struct_element, 'ExecutionEnvRef').text = \
                    rpc_args.Operations[i].ExecutionEnvRef
                
            elif rpc_args.Operations[i].Name == "UpdateOpStruct":
                update_op_struct_element = Element("UpdateOpStruct")
                operations_element.append(update_op_struct_element)
                
                # create and add UpdateOpStruct sub element
                SubElement(update_op_struct_element, 'UUID').text = \
                    rpc_args.Operations[i].UUID
                SubElement(update_op_struct_element, 'Version').text = \
                    rpc_args.Operations[i].Version
                SubElement(update_op_struct_element, 'URL').text = \
                    rpc_args.Operations[i].URL
                SubElement(update_op_struct_element, 'Username').text = \
                    rpc_args.Operations[i].Username
                SubElement(update_op_struct_element, 'Password').text = \
                    rpc_args.Operations[i].Password
                
            else:
                log.debug_err("Error Operations struct type:", rpc_args.Operations[i].Name)
                return CONSTRUCT_FAIL
        
        if rpc_args.CommandKey != "":
            SubElement(rpc_name_element, 'CommandKey').text = rpc_args.CommandKey
        else:
            SubElement(rpc_name_element, 'CommandKey', {'xsi:nil':'true'})
            
        return CONSTRUCT_SUC

    
    def create_inform_res_struct(self, rpc_args):
        """
        create InformResponse struct
        """
        
        # create RPC method element
        rpc_name_element = Element(CWMP_NS_PREFIX + RPC_INFORM_RES_TAG)
        
        # add RPC method element to soap_body
        self.soap_body.append(rpc_name_element)
        
        # create RPC method parameters element
        SubElement(rpc_name_element, 'MaxEnvelopes').text = str(rpc_args.MaxEnvelopes)
        
        return CONSTRUCT_SUC

    
    def create_kicked_res_struct(self, rpc_args):
        """
        create KickedResponse struct
        """
        
        # create RPC method element
        rpc_name_element = Element(CWMP_NS_PREFIX + RPC_KICKED_RES_TAG)
        
        # add RPC method element to soap_body
        self.soap_body.append(rpc_name_element)
        
        # create RPC method parameters element
        SubElement(rpc_name_element, 'NextURL').text = rpc_args.NextURL
        
        return CONSTRUCT_SUC

    def create_fault_struct(self, rpc_args):
        """
        create Fault struct
        """
        # create RPC method element
        rpc_name_element = Element(SOAP_ENV_NS_PREFIX + RPC_FAULT_TAG)
        
        # add RPC method element to soap_body
        self.soap_body.append(rpc_name_element)
        
        # create RPC method parameters element
        SubElement(rpc_name_element, 'faultcode').text = str(rpc_args.faultcode)
        SubElement(rpc_name_element, 'faultstring').text = rpc_args.faultstring
        
        # create and add detail element
        detail_element = Element('detail')
        rpc_name_element.append(detail_element)
        
        # create and add sub element of detail
        cwmp_fault_element = Element(CWMP_NS_PREFIX + RPC_FAULT_TAG)
        detail_element.append(cwmp_fault_element)
        
        # create and add sub element of cwmp fault element
        SubElement(cwmp_fault_element, 'FaultCode').text = str(rpc_args.detail.FaultCode)
        SubElement(cwmp_fault_element, 'FaultString').text = rpc_args.detail.FaultString
        
        return CONSTRUCT_SUC



def test(rpc_name):
    
    try:
        g_construct
    except NameError:
        g_construct = Construct()
        create_soap_envelope = g_construct.create_soap_envelope
        create_get_rpc_methods_res_struct = g_construct.create_get_rpc_methods_res_struct

    
    if rpc_name == "GetRPCMethods":
        ret = create_soap_envelope(rpc_name)
        print g_construct.str_xml
        
    else:
    
        if rpc_name == "GetRPCMethodsResponse":
            test_object = GetRPCMethodsResponse()
            test_object.MethodList = ['GetRPCMethods', 'Inform', 'TransferComplete',
                                      'AutonomousTransferComplete', 'Kicked', 
                                      'RequestDownload', 'DUStateChangeComplete',
                                      'AutonomousDUStateChangeComplete']
        
        elif rpc_name == "SetParameterValues":
            test_object = SetParameterValues()
            para_value_struct_object = ParameterValueStruct()
            para_value_struct_object.Name = "InternetGatewayDevice.DeviceInfo.X_CT-COM_UPNP.Enable"
            para_value_struct_object.Value = "1"
            para_value_struct_object.Value_type = "string"
            para_value_struct_object2 = ParameterValueStruct()
            para_value_struct_object2.Name = "InternetGatewayDevice.DeviceInfo.X_CT-COM_UPNP.Enable2"
            para_value_struct_object2.Value = "2"
            para_value_struct_object2.Value_type = "string"
            test_object.ParameterList.append(para_value_struct_object)
            test_object.ParameterList.append(para_value_struct_object2)
            test_object.ParameterKey = "test"
        elif rpc_name == "GetParameterValues":
            test_object = GetParameterValues()
            test_object.ParameterNames = ['InternetGatewayDevice.DeviceInfo.X_CT-COM_UPNP.Enable']
        elif rpc_name == "GetParameterNames":
            test_object = GetParameterNames()
            test_object.ParameterPath = 'InternetGatewayDevice.LANDevice.1.LANEthernetInterfaceConfig.'
            test_object.NextLevel = '0'
        elif rpc_name == "SetParameterAttributes":
            test_object = SetParameterAttributes()
            setpara_attrib_struct_object = SetParameterAttributesStruct()
            setpara_attrib_struct_object.Name = 'InternetGatewayDevice.LANDevice.1.WLANConfiguration.1.SSID' 
            setpara_attrib_struct_object.NotificationChange = '1'
            setpara_attrib_struct_object.Notification = '2'
            setpara_attrib_struct_object.AccessListChange = '1'
            setpara_attrib_struct_object.AccessList = ['Subscriber', 'admin']
            test_object.ParameterList.append(setpara_attrib_struct_object)
        elif rpc_name == "GetParameterAttributes":
            test_object = GetParameterAttributes()
            test_object.ParameterNames = ['InternetGatewayDevice.DeviceInfo.X_CT-COM_UPNP.Enable']
        elif rpc_name == "AddObject":
            test_object = AddObject()
            test_object.ObjectName = 'InternetGatewayDevice.WANDevice.1.WANConnectionDevice.'
            test_object.ParameterKey = "123456"
        elif rpc_name == "DeleteObject":
            test_object = DeleteObject()
            test_object.ObjectName = 'InternetGatewayDevice.WANDevice.1.WANConnectionDevice.'
            test_object.ParameterKey = "123456"
        elif rpc_name == "Download":
            test_object = Download()
            test_object.CommandKey = "111111"
            test_object.FileType = "3 Vendor Configuration File"
            test_object.URL = "http://172.24.35.35/001CF0001CF0865300.CFG"
            test_object.Username = ""
            test_object.Password = ""
            test_object.FileSize = "14966" 
            test_object.TargetFileName = "001CF0001CF0865300.CFG"
            test_object.DelaySeconds = '2'
            test_object.SuccessURL = "success.html"
            test_object.FailureURL = "fail.html"
        elif rpc_name == "Reboot":
            test_object = Reboot("111111")
        elif rpc_name == "InformResponse":
            test_object = InformResponse('1')
        elif rpc_name == "KickedResponse":
            test_object = KickedResponse("http://10.10.10.10")
        elif rpc_name == "ScheduleInform":
            test_object = ScheduleInform('10', 'commandkey_test')
        elif rpc_name == "SetVouchers":
            test_object = SetVouchers(['1','2','3'])
        elif rpc_name == "GetOptions":
            test_object = GetOptions("test")
        elif rpc_name == "Upload":
            test_object = Upload()
            test_object.CommandKey = 'Upload3651'
            test_object.FileType = '1 Vendor Configuration File'
            test_object.URL = 'http://20.20.20.20:9090/web/upload/cfg?deviceId=001CF0001CF0865300'
            test_object.DelaySeconds = '0'
        elif rpc_name == "ScheduleDownload":
            test_object = ScheduleDownload()
            test_object.CommandKey = "111111"
            test_object.FileType = "3 Vendor Configuration File"
            test_object.URL = "http://172.24.35.35/001CF0001CF0865300.CFG"
            test_object.Username = ""
            test_object.Password = ""
            test_object.FileSize = "14966" 
            test_object.TargetFileName = "001CF0001CF0865300.CFG"
            
            time_window_object = TimeWindowStruct()
            time_window_object.WindowStart = "1"
            time_window_object.WindowEnd = "2"
            time_window_object.WindowMode = "test"
            time_window_object.UserMessage = "hello"
            time_window_object.MaxRetries = "2"
            test_object.TimeWindowList.append(time_window_object)
            
        elif rpc_name == "ChangeDUState":
            install_object = InstallOpStruct()
            install_object.URL = "http://192.168.201.1:80/DeploymentUnit_60865e05/"
            install_object.UUID = 'b1fbaaa4-44f0-11e0-94cb-001cc09333fb'
            
            uninstall_object = UninstallOpStruct()
            uninstall_object.UUID = 'b1fbaaa4-44f0-11e0-94cb-001cc09333fb'
            
            update_object = UpdateOpStruct()
            update_object.URL = "http://192.168.201.1:80/DeploymentUnit_60865e05/"
            update_object.UUID = 'b1fbaaa4-44f0-11e0-94cb-001cc09333fb'
            
            test_object = ChangeDUState()
            test_object.Operations = [install_object, uninstall_object, update_object]
            test_object.CommandKey = "changesustate-111"
            
        elif rpc_name == "Fault":
            test_object = Fault()
            test_object.faultcode = "Server"
            test_object.faultstring = "CWMP fault"
            
            test_object.detail = CWMPFaultStruct()
            
            test_object.detail.FaultCode = "8003"
            test_object.detail.FaultString = "Invalid arguments"   
            
            
        else:
            print "now don't support:", rpc_name
        
        ret = create_soap_envelope(rpc_name, rpc_args=test_object)
        print ret
        print g_construct.str_xml


if __name__ == '__main__':
    
    test("Fault")