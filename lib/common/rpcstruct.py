# coding:utf-8

class AddObject:
    """
    define the calling arguments for AddObject
    """

    def __init__(self, object_name="", parameter_key=""):
        self.ObjectName = object_name        # type:string(256)
        self.ParameterKey = parameter_key    # type:string(32)

class AddObjectResponse:
    """
    define the arguments for AddObjectResponse
    """

    def __init__(self, instance_num=1, status=0):
        self.InstanceNumber = str(instance_num)     # type:UnsignedInt[1:]
        self.Status = str(status)                   # type:int[0:1]

class AllQueuedTransferStruct:
    """
    define AllQueuedTransferStruct
    """
    
    def __init__(self, command_key="", state=1,
                 is_download=0, file_type="",
                 file_size=0, target_file_name=""):
        self.CommandKey =  command_key              # type:string(32)
        self.State = str(state)                     # type:int[1:3]
        self.IsDownload = str(is_download)          # type:boolean
        self.FileType = file_type                   # type:string(64)
        self.FileSize = str(file_size)              # type:unsignedInt
        self.TargetFileName = target_file_name      # type:string(256)

class ArgStruct:
    """
    define ArgStruct
    """

    def __init__(self, name="", value=""):
        self.Name = name                    # type:string(64)
        self.Value = value                  # type:string(256)

class AutonomousDUStateChangeComplete:
    """
    define the calling arguments for AutonomousDUStateChangeComplete
    """
    
    def __init__(self):
        self.Results = []           # type: AutonOpResultStruct[]

class AutonomousDUStateChangeCompleteResponse:
    """
    define the arguments for AutonomousDUStateChangeCompleteResponse
    """
    
    def __init__(self):
        # this method response have no arguments
        pass

class AutonomousTransferComplete:
    """
    define the calling arguments for AutonomousTransferComplete
    """
    
    def __init__(self, announce_url="", transfer_url="",
                 is_download=0, file_type="",
                 file_size=0, target_file_name="",
                 start_time="0001-01-01T00:00:00",
                 complete_time="0001-01-01T00:00:00"):
        self.AnnounceURL = announce_url         # type:string(1024)
        self.TransferURL = transfer_url         # type:string(1024)
        self.IsDownload = str(is_download)      # type:boolean
        self.FileType = file_type               # type:string(64)
        self.FileSize = str(file_size)          # type:unsignedInt
        self.TargetFileName = target_file_name  # type:string(256)
        self.FaultStruct = []                   # type:FaultStruct
        self.StartTime = start_time             # type:dateTime
        self.CompleteTime = complete_time       # type:dateTime


class AutonomousTransferCompleteResponse:
    """
    define the arguments for AutonomousTransferCompleteResponse
    """
    
    def __init__(self):
        # the AutonomousTransferComplete response have no arguments
        pass

class AutonOpResultStruct:
    """
    define OpResultStruct
    """

    def __init__(self, uuid="", deployment_unit_ref="",
                 version="", current_state="",
                 resolved=0, execution_unitreflist="",
                 start_time="0001-01-01T00:00:00",
                 complete_time="0001-01-01T00:00:00",
                 operation_performed=""):
        self.UUID = uuid                              # type:string(36)
        self.DeploymentUnitRef = deployment_unit_ref  # type:string(256)
        self.Version = version                        # type:strubg(32)
        self.CurrentState = current_state             # type:string
        self.Resolved = str(resolved)                 # type:boolean 
        self.ExecutionUnitRefList = execution_unitreflist  #type:string
        self.StartTime = start_time                   # type:dateTime
        self.CompleteTime = complete_time             # type:dateTime
        self.Fault = []                               # type:FaultStruct
        self.OperationPerformed = operation_performed # type:string

class CancelTransfer:
    """
    define the calling arguments for CancelTransfer
    """
    
    def __init__(self, command_key=""):
        self.CommandKey = command_key           # type: string(32)

class CancelTransferResponse:
    """
    define the arguments for CancelTransferResponse
    """
    
    def __init__(self):
        # this method's response have no arguments
        pass

class ChangeDUState:
    """
    define the calling arguments for ChangeDUState
    """
    
    def __init__(self, command_key=""):
        self.Operations = []                    # type: OperationStruct[]
        self.CommandKey = command_key           # type: string(32)

class ChangeDUStateResponse:
    """
    define the arguments for ChangeDUStateResponse
    """
    
    def __init__(self):
        # this method's response have no arguments
        pass

class DeleteObject:
    """
    define the calling arguments for DeleteObject
    """
    
    def __init__(self, object_name="", parameter_key=""):
        self.ObjectName = object_name        # type:string(256)
        self.ParameterKey = parameter_key    # type:string(32)

class DeleteObjectResponse:
    """
    define the arguments for DeleteObjectResponse
    """
    
    def __init__(self, status=0):
        self.Status = str(status)            # type:int[0:1]

class DeviceIdStruct:
    """
    define DeviceIdStruct
    """
    
    def __init__(self, manufacturer="", oui="",
                 product_class="", serial_number=""):
        self.Manufacturer = manufacturer           # type:string(64)
        self.OUI = oui                             # type:string(6)
        self.ProductClass = product_class          # type:string(64)
        self.SerialNumber = serial_number          # type:string(64)
        
        self.ConnectionRequestURL = ""             # added for parse inform struct
        self.Hardwareversion = ""                  # added for parse inform struct
        self.Softwareversion = ""                  # added for parse inform struct

class Download:
    """
    define the calling arguments for Download
    """
    
    def __init__(self, command_key="",     file_type="",
                       url="",             username="",
                       password="",        file_size=0,
                       target_filename="", delay_seconds=0,
                       success_url= "",    failure_url=""):
        self.CommandKey = command_key              # type:string(32)
        self.FileType = file_type                  # type:string(64)
        self.URL = url                             # type:string(256)
        self.Username = username                   # type:string(256)
        self.Password = password                   # type:string(256)
        self.FileSize = str(file_size)             # type:unsignedInt
        self.TargetFileName = target_filename      # type:string(256)
        self.DelaySeconds = str(delay_seconds)     # type:unsignedInt
        self.SuccessURL = success_url              # type:string(256)
        self.FailureURL = failure_url              # type:string(256)

class DownloadResponse:
    """
    define the arguments for DownloadResponse
    """
    
    def __init__(self, status=0, start_time="0001-01-01T00:00:00",
                 complete_time="0001-01-01T00:00:00"):
        self.Status = str(status)               # type:int[0:1]
        self.StartTime = start_time             # type:dateTime
        self.CompleteTime = complete_time       # type:dateTime

class DUStateChangeComplete:
    """
    define the calling arguments for DUStateChangeComplete
    """
    
    def __init__(self, command_key=""):
        self.Results = []                # type: OpResultStruct
        self.CommandKey = command_key    # type: string(32)

class DUStateChangeCompleteResponse:
    """
    define the arguments for DUStateChangeCompleteResponse
    """
    
    def __init__(self):
        # this method response have no arguments
        pass

class EventStruct:
    """
    define EventStruct
    """
    
    def __init__(self, event_code="", command_key=""):
        self.EventCode = event_code           # type:string(64)
        self.CommandKey = command_key         # type:string(32)

class FactoryReset:
    """
    define the calling arguments for FactoryReset
    """
    
    def __init__(self):
        # this method has no calling arguments
        pass

class FactoryResetResponse:
    """
    define the arguments for FactoryResetResponse
    """
    
    def __init__(self):
        # the FactoryReset response have no arguments
        pass

class FaultStruct:
    """
    define FaultStruct
    """
    
    def __init__(self, fault_code=8000, fault_string=""):
        self.FaultCode = str(fault_code)           # type:unsignedInt
        self.FaultString = fault_string            # type:string(256)

class GetAllQueuedTransfers:
    """
    define the calling arguments for GetAllQueuedTransfers
    """
    
    def __init__(self):
        # this method has no calling arguments
        pass

class GetAllQueuedTransfersResponse:
    """
    define the calling arguments for GetAllQueuedTransfersResponse
    """
    
    def __init__(self):
        self.TransferList = []    # type: AllQueuedTransferStruct[16]

class GetOptions:
    """
    define the calling arguments for GetOptions
    """
    
    def __init__(self, option_name=""):
        self.OptionName = option_name    # type: string(64)

class GetOptionsResponse:
    """
    define the arguments for GetOptionsResponse
    """
    
    
    def __init__(self):
        self.OptionList = []   # type: OptionStruct[]

class GetParameterAttributes:
    """
    define the calling arguments for GetParameterAttributes
    """
    
    def __init__(self):
        # the element of ParameterNames is string(256)
        self.ParameterNames = []

class GetParameterAttributesResponse:
    """
    define the arguments for GetParameterAttributesResponse
    """
    
    def __init__(self):
        # the element of ParameterList is ParameterAttributeStruct
        self.ParameterList = []

class GetParameterNames:
    """
    define the calling arguments for GetParameterNames
    """
    
    def __init__(self, path="", next_level=0):
        self.ParameterPath = path            # type:string(256)
        self.NextLevel = str(next_level)     # type:boolean

class GetParameterNamesResponse:
    """
    define the arguments for GetParameterNamesResponse
    """
    
    def __init__(self):
        # the element of ParameterList is ParameterInfoStruct
        self.ParameterList = []

class GetParameterValues:
    """
    define the calling arguments for GetParameterValues
    """
    
    
    def __init__(self):
        # the element of ParameterNames is string
        self.ParameterNames = []

class GetParameterValuesResponse:
    """
    define the arguments for GetGarameterValuesResponse
    """
    
    def __init__(self):
        # the element of ParameterList is ParameteValueStruct
        self.ParameterList = []

class GetQueuedTransfers:
    """
    define the calling arguments for GetQueuedTransfers
    """
    
    def __init__(self):
        # the GetQueuedTransfers have no calling arguments
        pass


class GetQueuedTransfersResponse:
    """
    define the arguments for GetQueuedTransfersResponse
    """
    
    def __init__(self):
        # type QueuedTransferStruct[16]
        self.TransferList = []

class GetRPCMethods:
    """
    define the calling arguments for GetRPCMethods
    """
    
    def __init__(self):
        # this method has no calling arguments
        pass

class GetRPCMethodsResponse:
    """
    define the arguments for GetRPCMethodsResponse
    """
    
    def __init__(self):
        # the element of MethodList is string
        self.MethodList = []

class Inform:
    """
    define the calling arguments for Inform
    """

    def __init__(self):
        self.DeviceId = []                            # type:DeviceIdStruct
        self.Event = []                               # type:EventStruct[64]
        self.MaxEnvelopes = "1"                       # type:unsignedInt
        self.CurrentTime = "0001-01-01T00:00:00"      # type:dateTime
        self.RetryCount = "0"                         # type:unsignedInt
        self.ParameterList = []                       # type:ParameterValueStruct[]

class InformResponse:
    """
    define the arguments for InformResponse
    """

    def __init__(self, max_envelopes=1):
        self.MaxEnvelopes = str(max_envelopes)    # type:unsignedInt

class InstallOpStruct:
    """
    define InstallOpStruct
    """
    
    def __init__(self, url="", uuid="",
                 username="", password="",
                 execution_envref=""):
        self.URL = url                          # type:string(1024)
        self.UUID = uuid                        # type:string(36)
        self.Username = username                # type:string(256)
        self.Password = password                # type:string(256)
        self.ExecutionEnvRef = execution_envref # type:string(256)
        self.Name = "InstallOpStruct"           # this can not be changed
  
class Kicked:
    """
    define the calling arguments for Kicked
    """
    
    def __init__(self, command="", referer="",
                 arg="", next=""):
        self.Command = command           # type: string(32)
        self.Referer = referer           # type: string(64)
        self.Arg = arg                   # type: string(256)
        self.Next = next                 # type: string(1024)

class KickedResponse:
    """
    define the arguments for KickedResponse
    """
    
    
    def __init__(self, next_url=""):
        self.NextURL = next_url        # type: string(1024)


class OpResultStruct:
    """
    define OpResultStruct
    """
    
    def __init__(self, uuid="", deployment_unit_ref="",
                 version="", current_state="",
                 resolved=0, execution_unitreflist="",
                 start_time="0001-01-01T00:00:00",
                 complete_time="0001-01-01T00:00:00"):
        self.UUID = uuid                              # type:string(36)
        self.DeploymentUnitRef = deployment_unit_ref  # type:string(256)
        self.Version = version                        # type:strubg(32)
        self.CurrentState = current_state             # type:string
        self.Resolved = str(resolved)                      # type:boolean 
        self.ExecutionUnitRefList = execution_unitreflist  #type:string
        self.StartTime = start_time                   # type:dateTime
        self.CompleteTime = complete_time             # type:dateTime
        self.Fault = []                              # type:FaultStruct

class OptionStruct:
    """
    define OptionStruct
    """
    
    def __init__(self, option_name="", voucher_sn=0,
                 state=1, mode=0,
                 start_date="0001-01-01T00:00:00",
                 expiration_date="0001-01-01T00:00:00",
                 is_transferable=0):
        self.OptionName =  option_name              # type:string(64)
        self.VoucherSN = str(voucher_sn)            # type:unsignedInt
        self.State = str(state)                     # type:unsignedInt
        self.Mode = str(mode)                       # type:int[0:2]
        self.StartDate = start_date                 # type:dateTime
        self.ExpirationDate = expiration_date       # type:dateTime
        self.IsTransferable = str(is_transferable)  # type:boolean

class ParameterAttributeStruct:
    """
    define ParameterAttributeStruct
    """
    
    def __init__(self, name="", notification=0):
        self.Name = name                                    # type:string(256)
        self.Notification = str(notification)               # type:int[0:2]
        self.AccessList = []                                # the element of AccessList is string(64)

class ParameterInfoStruct:
    """
    define ParameterInfoStruct
    """
    
    def __init__(self, name="", writable=0):
        self.Name = name                  # type:string(256)
        self.Writable = str(writable)     # type:boolean

class ParameterValueStruct:
    """
    define ParameterValueStruct
    """
    
    def __init__(self, name="", value="", value_type=""):
        self.Name = name              # type:string(256)
        self.Value = value            # type:anySimpleType
        self.Value_type = value_type  # type:string

class QueuedTransferStruct:
    """
    define QueuedTransferStruct
    """
    
    def __init__(self, command_key="", state=1):
        self.CommandKey =  command_key           # type:string(32)
        self.State = str(state)                  # type:int[1:3]

class Reboot:
    """
    define the calling arguments for Reboot
    """
    
    def __init__(self, command_key=""):
        self.CommandKey = command_key         # type:string(32)

class RebootResponse:
    """
    define the arguments for RebootResponse
    """
    
    def __init__(self):
        # the reboot response have no argument
        pass

class RequestDownload:
    """
    define the calling arguments for RequestDownload
    """
    
    def __init__(self, file_type=""):
        self.FileType = file_type           # type: string(64)
        self.FileTypeArg = []               # type: ArgStruct[16]

class RequestDownloadResponse:
    """
    define the arguments for RequestDownloadResponse
    """
    
    def __init__(self):
        # this method response have no arguments
        pass

class ScheduleDownload:
    """
    define the calling arguments for ScheduleDownload
    """
    
    def __init__(self, command_key="", file_type="",
                 url="", username="", password="",
                 file_size=0, target_file_name=""):
        self.CommandKey = command_key           # type: string(32)
        self.FileType = file_type               # type: string(64)
        self.URL = url                          # type: string(256)
        self.Username = username                # type: string(256)
        self.Password = password                # type: string(256)
        self.FileSize = str(file_size)          # type: unsignedInt
        self.TargetFileName = target_file_name  # type: string(256)
        self.TimeWindowList = []                # type: TimeWindowStruct[1:2]

class ScheduleDownloadResponse:
    """
    define the arguments for ScheduleDownloadResponse
    """
    
    def __init__(self):
        # this method's response have no arguments
        pass

class ScheduleInform:
    """
    define the calling arguments for ScheduleInform
    """
    
    def __init__(self, delay_seconds=0, command_key=""):
        self.DelaySeconds = str(delay_seconds)    # type: unsignedInt
        self.CommandKey = command_key             # type: string(32)

class ScheduleInformResponse:
    """
    define the arguments for ScheduleInformResponse
    """
    
    def __init__(self):
        # the ScheduleInform response have no arguments
        pass

class SetParameterAttributes:
    """
    define the calling arguments for SetParameterAttributes
    """
    
    def __init__(self):
        # the element of ParameterList is SetParameterAttributesStruct
        self.ParameterList = []

class SetParameterAttributesResponse:
    """
    define the arguments for SetParameterAttributesResponse
    """
    
    def __init__(self):
        # this response have no arguments
        pass

class SetParameterAttributesStruct:
    """
    define SetParameterAttributesStruct
    """
    
    def __init__(self, name="", notification_change=0, 
                 notification=0, access_list_change=0):
        self.Name = name                                    # type:string(256)
        self.NotificationChange = str(notification_change)  # type:boolean
        self.Notification = str(notification)               # type:int[0:2]
        self.AccessListChange = str(access_list_change)     # type:boolen
        self.AccessList = []                                # the element of AccessList is string

class SetParameterValues:
    """
    define the calling arguments for SetParameterValues
    """
    
    def __init__(self, parameter_key=''):
        # the element of ParameterList is ParameterValueStruct
        self.ParameterList = []
        self.ParameterKey = parameter_key       # type: string(32)

class SetParameterValuesResponse:
    """
    define the arguments for SetParameterValuesResponse
    """
    
    def __init__(self, status=0):
        self.Status = str(status)   # type:int[0:1]

class SetVouchers:
    """
    define the calling arguments for SetVouchers
    """
    
    def __init__(self):
        self.VoucherList = []    # type: base64[]

class SetVouchersResponse:
    """
    define the arguments for SetVouchersResponse
    """
    
    def __init__(self):
        # the SetVouchers response have no arguments
        pass

class TimeWindowStruct:
    """
    define TimeWindowStruct
    """
    
    def __init__(self, window_start=0, window_end=0,
                 window_mode="", user_msg="",
                 max_retries=0):
        self.WindowStart = str(window_start)         # type:unsignedInt
        self.WindowEnd = str(window_end)             # type:unsignedInt
        self.WindowMode = window_mode                # type:string(64)
        self.UserMessage = user_msg                  # type:string(256)
        self.MaxRetries = str(max_retries)           # type:int

class TransferComplete:
    """
    define the calling arguments for TransferComplete
    """
    
    def __init__(self, command_key="", 
                 start_time="0001-01-01T00:00:00",
                 complete_time="0001-01-01T00:00:00"):
        self.CommandKey = command_key         # type:string(32)
        self.FaultStruct = []                 # type:FaultStruct
        self.StartTime = start_time           # type:dateTime
        self.CompleteTime = complete_time     # type:dateTime

class TransferCompleteResponse:
    """
    define the arguments for TransferCompleteResponse
    """
    
    def __init__(self):
        # the TransferComplete response have no arguments
        pass

class UninstallOpStruct:
    """
    define UninstallOpStruct
    """
    
    def __init__(self, uuid="", version="",
                 execution_envref=""):
        self.UUID = uuid                         # type:string(36)
        self.Version = version                   # type:string(32)
        self.ExecutionEnvRef = execution_envref  # type:string(256)
        self.Name = "UninstallOpStruct"          # this can not be changed

class UpdateOpStruct:
    """
    define UpdateOpStruct
    """
    
    def __init__(self, uuid="", version="",
                 url="", username="", password=""):
        self.UUID = uuid                        # type:string(36)
        self.Version = version                  # type:string(32)
        self.URL = url                          # type:string(1024)
        self.Username = username                # type:string(256)
        self.Password = password                # type:string(256)
        self.Name = "UpdateOpStruct"            # this can not be change

class Upload:
    """
    define the calling arguments for Upload
    """
    
    def __init__(self, command_key="", file_type="",
                 url="", username="", password="",
                 delay_seconds=0):
        self.CommandKey = command_key           # type: string(32)
        self.FileType = file_type               # type: string(64)
        self.URL = url                          # type: string(256)
        self.Username = username                # type: string(256)
        self.Password = password                # type: string(256)
        self.DelaySeconds = str(delay_seconds)  # type: unsignedInt

class UploadResponse:
    """
    define the arguments for UploadResponse
    """

    def __init__(self, status=0, start_time="0001-01-01T00:00:00",
                 complete_time="0001-01-01T00:00:00"):
        self.Status = str(status)               # type:int[0:1]
        self.StartTime = start_time             # type:dateTime
        self.CompleteTime = complete_time       # type:dateTime

class Fault:
    """
    define the arguments for Fault message
    """
    
    def __init__(self, fault_code="", fault_string=""):
        
        self.faultcode = fault_code        # type: string
        self.faultstring = fault_string    # type: string
        self.detail = []                   # type: CWMPFaultStruct
    
class CWMPFaultStruct:
    """
    define the struct of cwmp:Fault
    """
    
    def __init__(self, fault_code="", fault_string=""):
        
        self.FaultCode = fault_code            # type: string
        self.FaultString = fault_string        # type: string
        self.SetParameterValuesFaultList = []  # type: SetParameterValuesFaultStruct
    
class SetParameterValuesFaultStruct:
    """
    define the struct of SetParameterValuesFault
    """
    
    def __init__(self):
        
        self.ParameterName = ""      # type:string
        self.FaultCode = ""          # type:string
        self.FaultString = ""        # type:string
    
    