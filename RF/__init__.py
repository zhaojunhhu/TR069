# -*- coding: utf-8 -*- 

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: TR069
#  function: 提供TR069相关操作的关键字，包括CPE信息查询和修改，RPC方法下发，
#            工单查询与下发，远端服务器地址和端口配置等
#  Author: ATT development group
#  version: V1.0
#  date: 2012.12.22
#  change log:
#  lana     20121222        created
#  nwf      2013-03-21      add worklist
#  nwf      2013-04-13      refactor(unify)
#  wangjun  2013-08-29      通过检查methodagent是否存在来修改DEBUG_UNIT的值引用不同的connectioncache模块
#                           通过检查methodagent是否存在来修改DEBUG_UNIT的值引用不同的LOG模块
#  nwf      2013-11-27      log信息删除 "调用xx关键字成功  的提示信息"，替换为关键字的中文描述
# ***************************************************************************

# sys
import  time
from    time import sleep
import  re
import  sys
import  os
from    cStringIO       import StringIO
import  pickle
import  random


#debug
DEBUG_UNIT          = False

#switch log flag value. #add by wangjun 20130829
tr069_pro_dir=os.path.dirname(os.path.dirname(__file__))
methodagent_pro_path=os.path.join(tr069_pro_dir, 'lib', 'methodagent')

#用来标示是否需要设置log路径. #add by wangjun 20130902
REQUEST_ROM_METHOD_AGENT=False

if os.path.exists(methodagent_pro_path):
    print "MethodAgent module import TR069.RF"
    DEBUG_UNIT = True
    REQUEST_ROM_METHOD_AGENT=True

if DEBUG_UNIT:
    from robot_lib_utils.connectioncache import _NoConnection, ConnectionCache
else:
    from robot.utils.connectioncache import _NoConnection, ConnectionCache

#import log
if (DEBUG_UNIT):
    
    # nwf 2013-07-25; clear sys.path, RF **.pth
    rf_common = r"initapp\common"
    for i in sys.path:
        len1 = len(rf_common)
        if (i[-len1:] == rf_common):
            sys.path.remove(i)
    
    # \branch_v2.2_2\TR069\RF
    g_prj_dir = os.path.dirname(__file__)  
    parent1 = os.path.dirname(g_prj_dir)    # \branch_v2.2_2\TR069
    parent2 = os.path.dirname(parent1)      # \branch_v2.2_2\
    sys.path.insert(0, parent2)             
    
    import  TR069.lib.common.logs.log   as log

    #如果调用来自METHOD AGENT,不修改log默认路径. #add by wangjun 20130902
    if not REQUEST_ROM_METHOD_AGENT:
        log_dir = os.path.join(parent1, "log")
        log.start(name="nwf", directory=log_dir, level="DebugWarn")
        log.set_file_id(testcase_name="tr069")      
    
else:
    import  attlog                      as log

# user
import  TR069.lib.users.user        as user
from    TR069.lib.common.event      import *
from    TR069.lib.common.error      import *
from    TR069.lib.common.function   import *


VERSION = '2.1.1'

class TR069(object):
    ROBOT_LIBRARY_SCOPE     = 'GLOBAL'
    ROBOT_LIBRARY_VERSION   = VERSION

    
    def __init__(self):
        """
        """  
        self._cache = ConnectionCache()
        
        
    def switch_cpe(self, sn):
        """
        功能描述：oui-sn不存在则创建CPE(oui-sn)，存在则切换到CPE(oui-sn)  
                  
        参数：sn:  oui-sn 
              
        Example:
        | Switch Cpe | 02018-001CF00865300  |
        
        注意：识别CPE是通过oui-sn来确定全局唯一性的
        """

        self._cache.register(sn, sn)

        desc = "switch cpe(sn=%s) successfully." %(sn)
        log.user_info(desc)
                
        return None        


    def config_remote_server_addr(self, ip, port=50000):
        """
        功能描述：配置远端服务器地址：IP和端口号
        
        参数：ip: 远端服务器ip地址;
            port: 远端服务器端口号，默认为50000
             
        Example:
        | Config Remote Server Addr  | 10.10.10.10 | 50000 |
        
        """
        
        ret_api     = None
        ret_data    = None        

        # 检查IP地址合法性
        if 0 and not check_ipaddr_validity(ip):
            desc = u"关键字执行失败，IP地址为非法地址！"
            raise RuntimeError(desc)

        ret_api, ret_data = user.config_remote_address(ip, port)       
        if ret_api == ERR_SUCCESS:
            log_info = u'配置远端服务器成功。'
            log.user_info(log_info)
            
        else:
            desc = u'配置远端服务器失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)

        return None 
        

    def _get_sn(self):
        """
        if sn is not register, sn = ""(should not be obj(pickle not support) send to agent)
        """
        
        sn = self._cache.current
        if (isinstance(sn, _NoConnection) ): #change _NoConnection import module #changed by wangjumnn 20130829
            sn = ""
            log.user_info("warnning:SN is empty")
        
        return sn


    # ------------------- rpc keywords ---------------------------------------  
    def add_object(self, object_name, parameter_key=''):
        """
        功能描述：给多实例对象创建一个实例
        
        参数：object_name: 表示ObjectName参数，创建实例的路径名，必须以点结尾;
              parameter_key: 表示ParameterKey参数，默认为空。
              
        返回值：执行成功，返回 [新创建的实例号,CPE返回的修改状态status];
                执行失败，raise 错误信息
                
        Example:
        | ${ret_list} | Add Object | InternetGatewayDevice.WANDevice.1.WANConnectionDevice. |          |
        | ${ret_list} | Add Object | InternetGatewayDevice.WANDevice.1.WANConnectionDevice. | some_key |
        """
        
        ret_api     = None
        ret_data    = None
        ret_out     = None    
        
        sn          = self._get_sn()
        user1       = user.UserRpc(sn)        
        list_ret    = []
        
        ret_api, ret_data = user1.add_object(ObjectName=object_name,
                                            ParameterKey=parameter_key)                   
        if ret_api == ERR_SUCCESS:
            desc = u'建立新实例成功。' 
            log.user_info(desc)
            
            if "Status" in ret_data and "InstanceNumber" in ret_data:
                list_ret.append(ret_data["InstanceNumber"])
                list_ret.append(ret_data["Status"])
                
                ret_out = list_ret                    
            else:
                desc = u"建立新实例失败(解析失败)。"
                raise RuntimeError(desc)            
        else:
            desc = u'建立新实例失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)

        return ret_out
        
      
    def delete_object(self, object_name, parameter_key=''):
        """
        功能描述：删除对象的一个特定实例
        
        参数：object_name: 表示ObjectName参数，要删除的实例对象的路径名，必须以点结尾;  
              parameter_key: 表示ParameterKey参数，默认为空。
              
        返回值：执行成功，返回 CPE返回的修改状态status;
                执行失败，raise 错误信息
                
        Example:
        | ${status} | Delete Object | InternetGatewayDevice.WANDevice.1.WANConnectionDevice.3 |
        """
        
        ret_api     = None
        ret_data    = None
        ret_out     = None      
        
        sn          = self._get_sn()
        user1       = user.UserRpc(sn)
          
        ret_api, ret_data = user1.delete_object(ObjectName=object_name,
                                               ParameterKey=parameter_key)               
        if ret_api == ERR_SUCCESS:
            desc = u'删除一个对象的特定实例成功。' 
            log.user_info(desc)
            
            if "Status" in ret_data:
                ret_out = ret_data["Status"]                
            else:
                desc = u"删除一个对象的特定实例失败(解析失败)。"
                raise RuntimeError(desc)            
        else:
            desc = u'删除一个对象的特定实例失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc) 
            
        return ret_out

        
    def cancel_transfer(self, command_key=''):
        """
        功能描述：取消传输
        
        参数：command_key: 表示CommandKey参数，默认为空。
         
        Example:
        | Cancel Transfer  |  |
        | Cancel Transfer  | some_key  |
        """
        
        ret_api     = None
        ret_data    = None
        ret_out     = None       
        
        sn          = self._get_sn()
        user1       = user.UserRpc(sn)
        
        ret_api, ret_data = user1.cancel_transfer(CommandKey=command_key)   
        if ret_api == ERR_SUCCESS:
            desc = u'取消传输成功。' 
            log.user_info(desc)
            
            ret_out = ret_data
        else:
            desc = u'取消传输失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)
            
        return ret_out
        
        
    def change_du_state(self, install_op_struct=[], update_op_struct=[],
                              uninstall_op_struct=[], command_key='AUTO'):
        """
        功能描述：触发Deployment Unit（DU）的Install，Update和Uninstall状态变迁。
                  例如：installing a new DU, updating an existing DU，or uninstalling an existing DU.
                  
        参数：install_op_struct: 表示由InstallOpStruct组成的list，格式为[URL,UUID,Username,Password,ExecutionEnvRef]
                                  或者[[URL,...],[URL,...],...];
              update_op_struct: 表示由UpdateOpStruct组成的list，格式为[UUID,Version,URL,Username,Password]
                                  或者[[UUID,...],[UUID,...],...];
              uninstall_op_struct: 表示由UninstallOpStruct组成的list，格式为[UUID,Version,ExecutionEnvRef]
                                  或者[[UUID,...],[UUID,...],...];
              command_key: 表示CommandKey参数，默认为"AUTO"(由系统自动生成随机字符串)
               
        Example:
        | ${install_list}   | Create List     | url             | uuid              |
        | ...               | username        | password        | ExecutionEnvRef   |
        | ${update_list}    | Create List     | uuid            | version           |
        | ...               | url             | username        | password          |
        | ${uninstall_list} | Create List     | uuid            | version           |
        | ...               | ExecutionEnvRef |                 |                   |
        | Change Du State   | ${install_list} | ${update_list}  | ${uninstall_list} |
        
        """
        
        ret_api     = None
        ret_data    = None
        ret_out     = None        
        
        sn          = self._get_sn()
        user1       = user.UserRpc(sn)

        tmp_install_list    = []
        tmp_update_list     = []
        tmp_uninstall_list  = []
        tmp_operations      = []
        
        # if only one install op struct in install_op_struct,convert install_op_struct to [install_op_struct]
        if install_op_struct == []:
            tmp_install_list = install_op_struct
        elif type(install_op_struct[0]) is not list:
            tmp_install_list.append(install_op_struct)
        else:
            tmp_install_list = install_op_struct
            
        # convert update_op_struct to [update_op_struct], if needed
        if update_op_struct == []:
            tmp_update_list = update_op_struct
        elif type(update_op_struct[0]) is not list:
            tmp_update_list.append(update_op_struct)
        else:
            tmp_update_list = update_op_struct
            
        # convert uninstall_op_struct to [uninstall_op_struct], if needed
        if uninstall_op_struct == []:
            tmp_uninstall_list = uninstall_op_struct
        elif type(uninstall_op_struct[0]) is not list:
            tmp_uninstall_list.append(uninstall_op_struct)
        else:
            tmp_uninstall_list = uninstall_op_struct            

        for item in tmp_install_list:
            if len(item) == 5:
                dict_op_struct = {}
                dict_op_struct["URL"] = item[0]
                dict_op_struct["UUID"] = item[1]
                dict_op_struct["Username"] = item[2]
                dict_op_struct["Password"] = item[3]
                dict_op_struct["ExecutionEnvRef"] = item[4]
                tmp_operations.append({"InstallOpStruct":dict_op_struct})
            else:
                raise RuntimeError(u"输入的参数(install_op_struct)格式有误")
            
        for item in tmp_update_list:
            if len(item) == 5:
                dict_op_struct = {}
                dict_op_struct["UUID"] = item[0]
                dict_op_struct["Version"] = item[1]
                dict_op_struct["URL"] = item[2]
                dict_op_struct["Username"] = item[3]
                dict_op_struct["Password"] = item[4]
                tmp_operations.append({"UpdateOpStruct":dict_op_struct})
            else:
                raise RuntimeError(u"输入的参数(update_op_struct)格式有误")
            
        for item in tmp_uninstall_list:
            if len(item) == 3:    # zsj modified 2013/3/5
                dict_op_struct = {}
                dict_op_struct["UUID"] = item[0]
                dict_op_struct["Version"] = item[1]
                dict_op_struct["ExecutionEnvRef"] = item[2]
                tmp_operations.append({"UninstallOpStruct":dict_op_struct})
            else:
                raise RuntimeError(u"输入的参数(uninstall_op_struct)格式有误")
        
        if (command_key == "AUTO"):
            command_key = self._get_random_command_key()
            
        ret_api, ret_data = user1.change_du_state(Operations=tmp_operations,
                                                CommandKey=command_key)                   
        if ret_api == ERR_SUCCESS:
            desc = u'触发Deployment Unit（DU）的状态变迁成功。' 
            log.user_info(desc)
            
            ret_out = ret_data
        else:
            desc = u'触发Deployment Unit（DU）的状态变迁失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                            
            
        return ret_out

                
    def download(self, file_type, url, user_name='',password='', file_size=0,
                 target_file_name='', delay_seconds=0, success_url='',
                 failure_url='', command_key='AUTO'):
        """
        功能描述：让CPE去某一指定路径下载某一指定文件
        
        参数：file_type: 表示FileType参数，一个整数加一个空格加文件类型描述，目前支持以下几种：
                          "1 Firmware Upgrade Image"
                          "2 Web Content"
                          "3 Vendor Configuration File"
                          "4 Tone File"(new in cwmp-1-2)
                          "5 Ringer File"(new in cwmp-1-2)
                          "X<VENDOR><Vendor-specific-identifier>"
                          "X CU 4 User-Selective Firmware Upgrade Image"(联通)
                          
              url: 表示URL参数，源文件路径;
              
              user_name: 表示Username参数，文件服务器认证的用户名，默认为空;
              
              password: 表示Password参数，文件服务器认证的密码，默认为空;
              
              file_size: 表示FileSize参数，下载文件的大小，默认为0，表示不提供文件长度的信息;
              
              target_file_name: 表示TargetFileName参数，用于目标文件系统的文件名，默认为空;
              
              delay_seconds: 表示DelaySeconds参数，默认为0;
              
              success_url：表示SuccessURL参数，下载成功后，CPE将用户浏览器重定位到该URL，默认为空;
              
              failure_url：表示FailureURL参数，下载失败后，CPE将用户浏览器重定位到该URL，默认为空;
              
              command_key: 表示CommandKey参数，默认为"AUTO"(由系统自动生成随机字符串)
              
        返回值：执行成功，返回 [CPE返回的修改状态status, StartTime,CompleteTime];
                执行失败，raise 错误信息
                
        Example:
        | ${ret_list} | Download  | 3 Vendor Configuration File | http://172.24.35.35/001CF0001CF0865300.CFG |
        | ${ret_list} | Download  | 3 Vendor Configuration File | http://172.24.35.35/001CF0001CF0865300.CFG |
        | ...         | username  | password                    |                                            |
        """               
        ret_api     = None
        ret_data    = None
        ret_out     = None        
        
        sn          = self._get_sn()
        user1       = user.UserRpc(sn) 
        
        tmp_list    = []
        
        if (command_key == "AUTO"):
            command_key = self._get_random_command_key()

        # assistant
        desc = "file_type=%s, url=%s, user_name=%s,password=%s, file_size=%s,  target_file_name=%s, delay_seconds=%s, success_url=%s,  failure_url=%s, command_key=%s" %(file_type, url, user_name,password, file_size,  target_file_name, delay_seconds, success_url,  failure_url, command_key)
        log.user_info(desc)            
            
        ret_api, ret_data = user1.download(CommandKey=command_key,
                                        FileType=file_type,
                                        URL=url,
                                        Username=user_name,
                                        Password=password,
                                        FileSize=file_size,
                                        TargetFileName=target_file_name,
                                        DelaySeconds=delay_seconds,
                                        SuccessURL=success_url,
                                        FailureURL=failure_url)       
        if ret_api == ERR_SUCCESS:
            desc = u'下载成功。' 
            log.user_info(desc)
            
            if ("Status" in ret_data and
                "StartTime" in ret_data and
                "CompleteTime" in ret_data ):
                
                tmp_list.append(ret_data["Status"])
                tmp_list.append(ret_data["StartTime"])
                tmp_list.append(ret_data["CompleteTime"])
                
                ret_out = tmp_list
            else:
                desc = u"下载失败(解析失败)。"
                raise RuntimeError(desc)
        else:
            desc = u'下载失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)           
                        
        return ret_out


    def schedule_download(self, file_type, url, time_window_list,
                          user_name='',password='', file_size=0, 
                          target_file_name='', command_key='AUTO'):
        """
        功能描述：让CPE在一个或两个指定时间窗内到指定路径下载特定文件并应用
        
        参数：file_type: 表示FileType参数，一个整数加一个空格加文件类型描述，目前支持以下几种：
                          "1 Firmware Upgrade Image"
                          "2 Web Content"
                          "3 Vendor Configuration File"
                          "4 Tone File"(new in cwmp-1-2)
                          "5 Ringer File"(new in cwmp-1-2)
                          
                          "X<VENDOR><Vendor-specific-identifier>";
                          
              url: 表示URL参数，源文件路径;
              
              user_name: 表示Username参数，文件服务器认证的用户名，默认为空;
              
              password: 表示Password参数，文件服务器认证的密码，默认为空;
              
              file_size: 表示FileSize参数，下载文件的大小，默认为0，表示不提供文件长度的信息;
              
              target_file_name: 表示TargetFileName参数，用于目标文件系统的文件名，默认为空;
              
              time_window_list: 表示TimeWindowList参数，由一个或两个时间窗的结构体组成的list，两个时间窗不能重叠
                                时间窗的结构体为：
                                WindowStart: 从接受到请求到开始时间窗的偏移时间（in seconds）
                                WindowEnd: 从接受到请求到结束时间窗的偏移时间（in seconds）
                                WindowMode: 表示在时间窗内，CPE如何perform和apply the download,目前定义了以下几种：
                                                        "1 At Any Time"
                                                        "2 Immediately"
                                                        "3 When Idle"
                                                        "4 Confirmation Needed"
                                                        "X <VENDOR> <Vendor specific identifier>"
                                UserMessage: 给CPE用户的消息，通知他关于download请求。当WindowMode是"4 Confirmation Needed"时，CPE可以用它向用户确认。如果不需要，该参数可以为空。
                                MaxRetries: 在确定失败之前，下载和应用尝试的最大次数，为0表示不允许重试，为-1表示由CPE决定重试多少次。
                                time_window_list的参数格式为：
                                如果是一个时间窗结构体：[WindowStart, WindowEnd, WindowMode, UserMessage, MaxRetries]
                                如果是两个时间窗结构体：[[WindowStart,...],[WindowStart,...]]
                                
              command_key: 表示CommandKey参数，默认为"AUTO"(由系统自动生成随机字符串)
                
        Example:
        | ${one_time_window}  | Create List           | 10                      |       100           |
        | ...                 | 1 At Any Time         | ${EMPTY}                |       -1            |
        | ${two_time_window}  | Create List           | 110                     |      200            |
        | ...                 | 4 Confirmation Needed | "Begin to download now" |       -1            |
        | ${time_window_list} | Create List           | ${one_time_window}      | ${two_time_window}  |
        | Schedule Download   | 2 Web Content         | http://register/web/tt  | ${time_window_list} |
        | Schedule Download   | 2 Web Content         | http://register/web/tt  | ${one_time_window}  |
       
        """
        
        ret_api     = None
        ret_data    = None
        ret_out     = None    
        
        sn          = self._get_sn()
        user1       = user.UserRpc(sn)         
        
        tmp_time_window_list    = []
        tmp_list                = []
        
        # if only one time window in time_window_list,convert time_window_list to [parameter_list]
        if type(time_window_list[0]) is not list:
            tmp_list.append(time_window_list)
        else:
            tmp_list = time_window_list
        
        for item in tmp_list:
            if len(item) == 5:
                dict_time_window = {}
                dict_time_window["WindowStart"] = item[0]
                dict_time_window["WindowEnd"] = item[1]
                dict_time_window["WindowMode"] = item[2]
                dict_time_window["UserMessage"] = item[3]
                dict_time_window["MaxRetries"] = item[4]
                tmp_time_window_list.append(dict_time_window)
            else:
                raise RuntimeError(u"输入的参数(time_window_list)格式有误")
        
        if (command_key == "AUTO"):
            command_key = self._get_random_command_key()
            
        ret_api, ret_data = user1.schedule_download(
                                        CommandKey=command_key,
                                        FileType=file_type,
                                        URL=url,
                                        Username=user_name,
                                        Password=password,
                                        FileSize=file_size,
                                        TargetFileName=target_file_name,
                                        TimeWindowList=tmp_time_window_list)                   
        if ret_api == ERR_SUCCESS:
            desc = u'计划下载成功。' 
            log.user_info(desc)
            
            ret_out = ret_data
        else:
            desc = u'计划下载失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                
            
        return ret_out     


    def factory_reset(self):
        """
        功能描述：让CPE恢复出厂默认设置
        
        参数：无
           
        Example:
        | Factory Reset  |       |
        
        """
        
        ret_api     = None
        ret_data    = None
        ret_out     = None  
        
        sn          = self._get_sn()
        user1       = user.UserRpc(sn) 
        
        ret_api, ret_data = user1.factory_reset()                   
        if ret_api == ERR_SUCCESS:
            desc = u'恢复出厂设置成功。' 
            log.user_info(desc)
            
            ret_out = ret_data
        else:
            desc = u'恢复出厂设置失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                
            
        return ret_out


    def get_all_queued_transfers(self):
        """
        功能描述：获取所有上传，下载，包括不是ACS指定的请求的transfer的状态
        
        参数：无
        
        返回值：执行成功，返回 由[CommandKey,State,IsDownload,FileType,FileSize,TargetFileName]组成的列表;
               执行失败，raise 错误信息
               
        Example:
        | ${ret_list} | Get All Queued Transfers  |       |
        
        """
        
        ret_api     = None
        ret_data    = None
        ret_out     = None    
        
        sn          = self._get_sn()
        user1       = user.UserRpc(sn)         
        
        tmp_list    = []
        
        ret_api, ret_data = user1.get_all_queued_transfers()               
        if ret_api == ERR_SUCCESS:
            desc = u'确定前面的下载或上载请求的状态成功。' 
            log.user_info(desc)
            
            if "TransferList" in ret_data:
                for item in ret_data["TransferList"]:
                    tmp_sub_list=[]
                    tmp_sub_list.append(item.get("CommandKey"))
                    tmp_sub_list.append(item.get("State"))
                    tmp_sub_list.append(item.get("IsDownload"))
                    tmp_sub_list.append(item.get("FileType"))
                    tmp_sub_list.append(item.get("FileSize"))
                    tmp_sub_list.append(item.get("TargetFileName"))
                    tmp_list.append(tmp_sub_list)
                    
                ret_out = tmp_list
            else:
                desc = u"确定前面的下载或上传请求的状态失败(解析失败)。"
                raise RuntimeError(desc)
        else:
            desc = u'确定前面的下载或上传请求的状态失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)
            
        return ret_out


    def get_options(self, option_name=''):
        """
        功能描述：获取当前CPE的选项设置。以及它们相应的状态信息
        
        参数：option_name: 表示OptionName参数，该参数表示一个特定option的名字;
                            如果为空，表示需要返回所有CPE支持的Options，默认为空
                            
        返回值：执行成功，返回 由[OptionName,VoucherSN,State,Mode,StartDate,ExpirationDate,IsTransferable]组成的列表;
                执行失败，raise 错误信息
                
        Example:
        | ${ret_list} | Get Options  | some_option_name  |
        
        """
        
        ret_api     = None
        ret_data    = None
        ret_out     = None      
        
        sn          = self._get_sn()
        user1       = user.UserRpc(sn)  
                
        tmp_list    = []
        
        ret_api, ret_data = user1.get_options(OptionName=option_name)       
        if ret_api == ERR_SUCCESS:
            desc = u'获取当前CPE的选项设置成功。' 
            log.user_info(desc)
            
            if "OptionList" in ret_data:
                for item in ret_data["OptionList"]:
                    tmp_sub_list=[]
                    tmp_sub_list.append(item.get("OptionName"))
                    tmp_sub_list.append(item.get("VoucherSN"))
                    tmp_sub_list.append(item.get("State"))
                    tmp_sub_list.append(item.get("Mode"))
                    tmp_sub_list.append(item.get("StartDate"))
                    tmp_sub_list.append(item.get("ExpirationDate"))
                    tmp_sub_list.append(item.get("IsTransferable"))
                    tmp_list.append(tmp_sub_list)
                    
                ret_out = tmp_list                
            else:
                desc = u"获取当前CPE的选项设置失败(解析失败)。"
                raise RuntimeError(desc)
            
        else:
            desc = u'获取当前CPE的选项设置失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                
            
        return ret_out


    def get_rpc_methods(self):    
        """
        功能描述：获取CPE所支持的RPC方法
        
        参数：无
        
        返回值：执行成功，返回 CPE支持的RPC方法列表;
                执行失败，raise 错误信息
                
        Example:
        | ${method_list}  | Get Rpc Methods  |
        """
        
        ret_api     = None
        ret_data    = None
        ret_out     = None     
        
        sn          = self._get_sn()
        user1       = user.UserRpc(sn)  
    
        ret_api, ret_data = user1.get_rpc_methods()       
        if ret_api == ERR_SUCCESS:
            desc = u'获取CPE支持的RPC方法列表成功。' 
            log.user_info(desc)
            
            if "MethodsList" in ret_data:
                ret_data = ret_data.get("MethodsList")
                
                ret_out = ret_data
            else:
                desc = u"获取CPE支持的RPC方法列表失败(解析失败)。"
                raise RuntimeError(desc)        
        else:
            desc = u'取CPE支持的RPC方法列表失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)           
            
        return ret_out
        
       
    def set_parameter_values(self, parameter_list, parameter_key=""):
        """
        功能描述：修改CPE的一个或多个参数值
        
        参数：parameter_list: 表示ParameterList参数，由[name,vlaue]值对作为元素组成的列表，
                              name表示要修改的参数名，value表示要修改的参数值。
                              如果只修改一个参数，参数格式为：[name,value]或者[[name,value]]
                              如果修改多个参数，参数格式为：[[name1,value1],[name2,value2],...]
                              
              parameter_key: 表示ParameterKey参数，默认为空。
              
        返回值：执行成功，返回 CPE返回的修改状态status;
                执行失败，raise 错误信息
                
        Example:
        | ${name}       | Set Variable         | InternetGatewayDevice.DeviceInfo.ManufacturerOUI  |               |
        | ${value}      | Set Variable         | 0F34PT                                            |               |
        | ${para_list}  | Create List          | ${name}                                           | ${value}      |
        | ${status}     | Set Parameter Values | ${para_list}                                      | some_key      |
        | ${one_list}   | Create List          | InternetGatewayDevice.DeviceInfo.ManufacturerOUI  | 0F34PT        |
        | ${two_list}   | Create List          | InternetGatewayDevice.DeviceInfo.ProvisioningCode |  111          |
        | ${para_lists} | Create List          | ${one_list}                                       | ${two_list}   |
        | ${status}     | Set Parameter Values | ${para_lists}                                     | some_key      |

        """
        
        ret_api     = None
        ret_data    = None
        ret_out     = None    
        
        sn          = self._get_sn()
        user1       = user.UserRpc(sn)  
                
        tmp_list            = []
        tmp_parameter_list  = []
        
        # if only one parameter in parameter_list,convert parameter_list to [parameter_list]
        if type(parameter_list[0]) is not list:
            tmp_list.append(parameter_list)
        else:
            tmp_list = parameter_list            

        for item in tmp_list:
        
            len1 = len(item)
            dict_parameters = {}
            
            if (len1 < 2):
                raise RuntimeError(u"输入的参数(parameter_list)格式有误")
            
            if len1 >= 2:                
                dict_parameters["Name"]     = item[0]
                dict_parameters["Value"]    = item[1]
            if (len1 >= 3):
                dict_parameters["Type"]     = item[2]
            
            tmp_parameter_list.append(dict_parameters)
            
        ret_api, ret_data = user1.set_parameter_values(
                                        ParameterList=tmp_parameter_list,
                                        ParameterKey=parameter_key)                   
        if ret_api == ERR_SUCCESS:
            desc = u'修改CPE参数成功。' 
            log.user_info(desc)
            
            if "Status" in ret_data:
                ret_data = ret_data["Status"]
                
                ret_out = ret_data
            else:
                desc = u"修改CPE参数失败(解析失败)。"
                raise RuntimeError(desc)            
        else:
            desc = u'修改CPE参数失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                
            
        return ret_out
        
     
    def get_parameter_values(self, parameter_names=[]):
        """
        功能描述：获取CPE的一个或多个参数值
        
        参数：parameter_names: 表示ParameterNames参数，由参数名组成的列表，
                               如果只获取一个参数值，参数格式为：name 或者[name]
                               如果要获取多个参数值，参数格式为：[name1,name2,...]
                               如果参数名不是完整路径，以点结尾，表示获取该路径下所有的参数值
                               如果参数名为空字符串，表示顶级参数名，默认为空
                               
        返回值：执行成功，返回 由[Name, Value]组成的列表;
                执行失败，raise 错误信息
                
        Example:
        | ${name1}     | Set Variable           | InternetGatewayDevice.DeviceInfo.ManufacturerOUI  |          |
        | ${name2}     | Set Variable           | InternetGatewayDevice.DeviceInfo.ProvisioningCode |          |                                   |
        | ${para_list} | Create List            | ${name1}                                          | ${name2} |
        | ${ret_list}  | Get Parameter Values   | ${para_list}                                      |          |
        | ${ret_list}  | Get Parameter Values   | ${name1}                                          |          |
        """
        
        ret_api     = None
        ret_data    = None
        ret_out     = None  
        
        sn          = self._get_sn()
        user1       = user.UserRpc(sn)  

        tmp_parameter_names = []
        ret_list            = []
        
        # if parameter_names is not list,convert parameter_names to [parameter_names]
        if type(parameter_names) is not list:
            tmp_parameter_names.append(parameter_names)
        else:
            tmp_parameter_names = parameter_names
            
        ret_api, ret_data = user1.get_parameter_values(ParameterNames=tmp_parameter_names)               
        if ret_api == ERR_SUCCESS:
            desc = u'获取CPE参数值成功。' 
            log.user_info(desc)
            
            if "ParameterList" in ret_data:
                tmp_ret_list = ret_data["ParameterList"]
                for item in tmp_ret_list:
                    ret_list.append([item["Name"], item["Value"]])
                    
                ret_out = ret_list                
            else:
                desc = u"获取CPE参数值失败(解析失败)。"
                raise RuntimeError(desc)              
        else:
            desc = u'获取CPE参数值失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)               
            
        return ret_out
        
        
    def get_parameter_names(self, parameter_path='', next_level=False):
        """
        功能描述：获取CPE上可以访问的参数
        
        参数：parameter_path:  表示ParameterPath参数，可以是一个全路径或者部分路径，
                               如果是部分路径必须以点结尾，
                               如果是空字符串表示顶级参数名，默认为空字符串;
                               
              next_level: 表示NextLevel参数，为False表示返回与参数路径完全匹配的节点参数
                          以及该路径下面所有的子节点参数。为True，只返回匹配路径下一级的节点参数
                          默认为False
                          
        返回值：执行成功，返回 由[Name, Writalbe]组成的列表;
                执行失败，raise 错误信息
                
        Example:
        | ${path}      | Set Variable           | InternetGatewayDevice.DeviceInfo.                 |      |
        | ${name}      | Set Variable           | InternetGatewayDevice.DeviceInfo.ManufacturerOUI  |      |
        | ${ret_list}  | Get Parameter Names    | ${path }                                          | True |
        | ${ret_list}  | Get Parameter Names    | ${name}                                           |      |
        | ${ret_list}  | Get Parameter Names    |                                                   |      |
        """
        
        ret_api     = None
        ret_data    = None
        ret_out     = None  
        
        sn          = self._get_sn()
        user1       = user.UserRpc(sn) 
        
        ret_list    = []
        
        ret_api, ret_data = user1.get_parameter_names(ParameterPath=parameter_path,
                                                     NextLevel=next_level)       
        if ret_api == ERR_SUCCESS:
            desc = u'获取CPE上可以访问的参数成功。'
            log.user_info(desc)
            
            if "ParameterList" in ret_data:
                tmp_ret_list = ret_data["ParameterList"]
                for item in tmp_ret_list:
                    ret_list.append([item["Name"], item["Writable"]])
                
                ret_out = ret_list
            else:
                desc = u"获取CPE上可以访问的参数失败(解析失败)。"
                raise RuntimeError(desc)                  
        else:
            desc = u'获取CPE上可以访问的参数失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                   
            
        return ret_out
        
     
    def set_parameter_attributes(self, parameter_list):
        """
        功能描述：修改CPE的一个或多个参数的属性
        
        参数：parameter_list:  表示ParameterList参数，是由
                               [Name,NotificationChang,Notification,AccessListChange,AccessList]
                               组成的列表，
                               如果只修改一个参数，参数格式为：[Name,...]或者[[Name,...]]
                               如果同时修改多个参数，参数格式为：[[Name1,...],[Name2,...]]
                
        Example:
        | ${access_list}           | Create List   | Subscriber                                         |                |
        | ${para_list}             | Create List   | InternetGatewayDevice.DeviceInfo.ManufacturerOUI  | 1              |
        | ...                      |        2      | 1                                                 | ${access_list} |　
        | Set Parameter Attributes | ${para_list}  |                                                   |                |
        | ${two_list}              | Create List   | InternetGatewayDevice.DeviceInfo.ProvisioningCode | 1              |
        | ...                      | 1             | 1                                                 | ${access_list} |
        | ${para_lists}            | Create List   | ${para_list}                                      | ${two_list}    |
        | Set Parameter Attributes | ${para_lists} |                                                   |                |

        """
        
        ret_api     = None
        ret_data    = None
        ret_out     = None  
        
        sn          = self._get_sn()
        user1       = user.UserRpc(sn) 
                
        tmp_list            = []
        tmp_parameter_list  = []
        
        # if only one parameter in parameter_list,convert parameter_list to [parameter_list]
        if type(parameter_list[0]) is not list:
            tmp_list.append(parameter_list)
        else:
            tmp_list = parameter_list
            
        for item in tmp_list:
            if len(item) == 5:
                dict_parameters = {}
                dict_parameters["Name"] = item[0]
                dict_parameters["NotificationChange"] = item[1]
                dict_parameters["Notification"] = item[2]
                dict_parameters["AccessListChange"] = item[3]
                dict_parameters["AccessList"] = item[4]
                tmp_parameter_list.append(dict_parameters)
            else:
                raise RuntimeError(u"输入的参数(parameter_list)格式有误")
            
        ret_api, ret_data = user1.set_parameter_attributes(
                                        ParameterList=tmp_parameter_list)               
        if ret_api == ERR_SUCCESS:
            desc = u'修改CPE的参数的属性成功。' 
            log.user_info(desc)
            
            ret_out = ret_data
        else:
            desc = u'修改CPE的参数的属性失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)   
            
        return ret_out
        
        
    def get_parameter_attributes(self, parameter_names=[]):
        """
        功能描述：获取CPE的一个或多个参数的属性
        
        参数：parameter_names: 表示ParameterNames参数，由参数名组成的列表，
                               如果只获取一个参数的属性，参数格式为：name或者[name]
                               如果要获取多个参数的属性，参数格式为：[name1,name2,...]
                               如果参数名不是完整路径，以点结尾，表示获取该路径下所有的参数的属性
                               如果参数名为空字符串，表示顶级参数名，默认为空
                               
        返回值：执行成功，返回 由[Name, Notification, AccessList]组成的列表;
                执行失败，raise 错误信息
                
        Example:
        | ${name1}     | Set Variable              | InternetGatewayDevice.DeviceInfo.ManufacturerOUI  |          |
        | ${name2}     | Set Variable              | InternetGatewayDevice.DeviceInfo.ProvisioningCode |          |
        | ${para_list} | Create List               | ${name1}                                          | ${name2} | 
        | ${ret_list}  | Get Parameter Attributes  | ${name1}                                          |          |
        | ${ret_list}  | Get Parameter Attributes  | ${para_list}                                      |          |
        
        """
        
        ret_api     = None
        ret_data    = None
        ret_out     = None     
        
        sn          = self._get_sn()
        user1       = user.UserRpc(sn) 
        
        tmp_parameter_names     = []
        ret_list                = []
        
        # if parameter_names is not list,convert parameter_names to [parameter_names]
        if type(parameter_names) is not list:
            tmp_parameter_names.append(parameter_names)
        else:
            tmp_parameter_names = parameter_names
            
        ret_api, ret_data = user1.get_parameter_attributes(ParameterNames=tmp_parameter_names)                   
        if ret_api == ERR_SUCCESS:
            desc = u'获取CPE的参数的属性成功。' 
            log.user_info(desc)
            
            if "ParameterList" in ret_data:
                tmp_ret_list = ret_data["ParameterList"]
                for item in tmp_ret_list:
                    ret_list.append([item["Name"], item["Notification"], item["AccessList"]])
                    
                ret_out = ret_list
            else:
                desc = u"获取CPE的参数的属性失败(解析失败)。"
                raise RuntimeError(desc)               
        else:
            desc = u'获取CPE的参数的属性失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)   
                            
        return ret_out
        
        
    def get_queued_transfers(self):
        """
        功能描述：用于获取之前请求的下载或上传的状态
        
        参数：无
        
        返回值：执行成功，返回 [CommandKey,State]
               执行失败，raise 错误信息
               
        Example:
        | ${ret_list} | Get Queued Transfers  |       |
        
        """
        
        ret_api     = None
        ret_data    = None
        ret_out     = None     
        
        sn          = self._get_sn()
        user1       = user.UserRpc(sn) 
        
        tmp_list    = []
        
        ret_api, ret_data = user1.get_queued_transfers()               
        if ret_api == ERR_SUCCESS:
            desc = u'获取之前请求的下载或上传的状态成功。' 
            log.user_info(desc)
            
            if "TransferList" in ret_data:
                # zsj modified ret_data["TransferList"]的值是列表，应取列表第一项 2013/3/13
                transflist = ret_data["TransferList"]
                if (transflist):
                    transfer_list = transflist[0]                
                    tmp_list.append(transfer_list["CommandKey"])
                    tmp_list.append(transfer_list["State"])
                else:
                    # nwf 2013-06-29;
                    tmp_list = []
                    
                ret_out = tmp_list
            else:
                desc = u"获取之前请求的下载或上传的状态失败(解析失败)。"
                raise RuntimeError(desc)               
        else:
            desc = u'获取之前请求的下载或上传的状态失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                
            
        return ret_out
        
        
    def reboot(self, command_key='AUTO'):
        """
        功能描述：让CPE重启
        
        参数：command_key: 表示CommandKey参数，默认为"AUTO"(由系统自动生成随机字符串)
            
        Example:
        | Reboot  |           |
        | Reboot  | some_key  |
        """
        
        ret_api     = None
        ret_data    = None
        ret_out     = None   
        
        sn          = self._get_sn()
        user1       = user.UserRpc(sn) 
        
        if (command_key == "AUTO"):
            command_key = self._get_random_command_key()
            
        ret_api, ret_data = user1.reboot(CommandKey=command_key)       
        if ret_api == ERR_SUCCESS:
            desc = u'CPE重启成功。'
            log.user_info(desc)
            
            ret_out = ret_data
        else:
            desc = u'CPE重启失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc) 
                
        return ret_out        
        
                
    def schedule_inform(self, delay_seconds, command_key='AUTO'):
        """
        功能描述：该方法给CPE发送一个请求，要求cpe在该方法成功的DelaySeconds之后调用Inform方法。
        
        参数：delay_seconds: 表示DelaySeconds参数，从收到方法到初始inform需要等待的时间，
                             该参数值必须比0大 
              command_key: 表示CommandKey参数，默认为"AUTO"(由系统自动生成随机字符串)
               
        Example:
        | Schedule Inform  |  10  |          |
        | Schedule Inform  |  10  | some_key |
        """
        
        ret_api     = None
        ret_data    = None
        ret_out     = None   
        
        sn          = self._get_sn()
        user1       = user.UserRpc(sn) 
        
        if (command_key == "AUTO"):
            command_key = self._get_random_command_key()
            
        ret_api, ret_data = user1.schedule_inform(
                                DelaySeconds=delay_seconds,
                                CommandKey=command_key)                   
        if ret_api == ERR_SUCCESS:
            desc = u'计划inform成功。'
            log.user_info(desc)
            
            ret_out = ret_data
        else:
            desc = u'计划inform失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)               
            
        return ret_out
        
        
    def set_vouchers(self, voucher_list):
        """
        功能描述：在CPE上设置一个或多个option-vouchers
        
        参数：voucher_list: 表示VoucherList参数，由Voucher组成的list，
                            每个Voucher表现为一个Base64 encoded octet string
                
        Example:
        | ${voucher}      | Set Variable    | some_string |              |
        | ${voucher_list} | Create List     | some_string | other_string |
        | Set Vouchers    | ${voucher}      |             |              |
        | Set Vouchers    | ${voucher_list} |             |              |
        """
        
        ret_api     = None
        ret_data    = None
        ret_out     = None   
        
        sn          = self._get_sn()
        user1       = user.UserRpc(sn) 
        
        ret_api, ret_data = user1.set_vouchers(VoucherList=voucher_list)               
        if ret_api == ERR_SUCCESS:
            desc = u'设置CPE凭据选项成功。'
            log.user_info(desc)
            
            ret_out = ret_data
        else:
            desc = u'设置CPE凭据选项失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                 
            
        return ret_out
        
                        
    def upload(self, file_type, url, user_name='', password='',
                     delay_seconds=0, command_key='AUTO'):
        """
        功能描述：让CPE上传某一特定文件到某一特定路径
        
        参数：file_type: 表示FileType参数，一个整数加一个空格加文件类型描述，目前支持以下几种：
                          "1 Vendor Configuration File"[DEPRECATED]
                          "2 Vendor Log File"[DEPRECATED]
                          "3 Vendor Configuration File <i>"
                          "4 Vendor Log File <i>"
                          "X<VENDOR><Vendor-specific-identifier>"
                          
              url: 表示URL参数，目标文件路径;
              
              user_name: 表示Username参数，文件服务器认证的用户名，默认为空;
              
              password: 表示Password参数，文件服务器认证的密码，默认为空;
              
              delay_seconds: 表示DelaySeconds参数，默认为0;
              
              command_key: 表示CommandKey参数，默认为"AUTO"(由系统自动生成随机字符串)
              
        返回值：执行成功，返回 [CPE返回的修改状态status,StartTime,CompleteTime];
                执行失败，raise 错误信息
                
        Example:
        | ${ret_list} | Upload  | 1 Vendor Configuration File | http://20.20.20.20:9090/web/upload/ |
        | ${ret_list} | Upload  | 1 Vendor Configuration File | http://20.20.20.20:9090/web/upload/ |
        | ...         | user    | password                    | 10                                  | 
        """
        
        ret_api     = None
        ret_data    = None
        ret_out     = None     
        
        sn          = self._get_sn()
        user1       = user.UserRpc(sn) 
        
        tmp_list    = []

        if (command_key == "AUTO"):
            command_key = self._get_random_command_key()
            
        ret_api, ret_data = user1.upload(
                                CommandKey=command_key,
                                FileType=file_type,
                                URL=url,
                                Username=user_name,
                                Password=password,
                                DelaySeconds=delay_seconds)       
        if ret_api == ERR_SUCCESS:
            desc = u'上传成功。'
            log.user_info(desc)
            
            if ("Status" in ret_data and
                "StartTime" in ret_data and
                "CompleteTime" in ret_data ):
                tmp_list.append(ret_data["Status"])
                tmp_list.append(ret_data["StartTime"])
                tmp_list.append(ret_data["CompleteTime"])
                
                ret_out = tmp_list
            else:
                desc = u"上传失败(解析失败)。"
                raise RuntimeError(desc)              
        else:
            desc = u'上传失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)  
            
        return ret_out                                                           
      

    # ------------------- get/set keywords ---------------------------------------          
    def _query_cpe_info(self):
        """
        """
        ret         = ERR_FAIL
        ret_api     = None
        ret_data    = None
        ret_out     = None
        
        sn          = self._get_sn()  

        ret_api, ret_data = user.query_cpe_info(sn)               
        if ret_api == ERR_SUCCESS:
            desc = u'查询CPE信息成功。' 
            #log.user_info(desc)    # no need
            
            ret_out = ret_data      # MsgQueryCPEInfo
            ret = ERR_SUCCESS
        else:
            desc = u'查询CPE信息失败，详细信息为：%s' %ret_data
            
            ret = ERR_FAIL
            ret_out = desc
            
        return ret, ret_out        


    def _update_cpe_info(self, dict_modify_items):
        """
        功能描述：更新CPE相关信息到ACS服务器
        
        参数：dict_modify_items: 需要更新的信息字典，格式为{name:value,...}
        
        返回值：执行成功，返回(TR069_SUCCESS(0)，成功信息);
                执行失败，返回(TR069_FAIL(-1)，错误信息)
        """
        ret         = None
        ret_api     = None
        ret_data    = None  
        ret_out     = None

        sn          = self._get_sn()     
        
        ret_api, ret_data = user.update_cpe_info(sn, dict_modify_items)                   
        if ret_api == ERR_SUCCESS:
            desc = u'更新CPE信息成功。' 
            #log.user_info(desc)
            
            ret = ERR_SUCCESS
            ret_out = ret_data
        else:
            desc = u'更新CPE信息失败，详细信息为：%s' %ret_data
            
            ret = ERR_FAIL
            ret_out = desc
            
        return ret, ret_out    


    def get_acs_auth_info(self):
        """
        功能描述：获取CPE的正向认证信息，包括用户名和密码
        
        参数：无
        
        返回值：执行成功，返回 [username,password];
                执行失败，raise 错误信息
                
        Example:
        | ${ret_list} | Get Acs Auth Info  |
        
        """
        
        ret         = None
        ret_data    = None
        ret_out     = None   

        ret, ret_data = self._query_cpe_info()               
        if ret == ERR_SUCCESS:
            desc = u'获取CPE的正向认证信息成功。' 
            log.user_info(desc)
            
            username = ret_data.cpe2acs_loginname
            password = ret_data.cpe2acs_loginpassword
            ret_out = [username, password]
        else:
            desc = u'获取CPE的正向认证信息失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)
            
        return ret_out


    def set_acs_auth_info(self, username="admin", password="admin"):
        """
        功能描述：修改正向连接认证的用户名和密码
        
        参数： username: acs认证cpe的用户名;
               password: acs认证cpe的密码
                
        Example:
        | Set Acs Auth Info  | username  | password  |
        
        """
        
        ret         = None
        ret_data    = None
        ret_out     = None   
        
        d1 = {}
        d1["acs_auth_cpe_username"] = username
        d1["acs_auth_cpe_password"] = password
        
        ret, ret_data = self._update_cpe_info(d1)        
        if ret == ERR_SUCCESS:
            desc = u'修改正向连接认证的用户名和密码成功。' 
            log.user_info(desc)
            
            ret_out = ret_data
        else:
            desc = u'修改正向连接认证的用户名和密码失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)
           
        return ret_out


    def get_acs_auth_method(self):
        """
        功能描述：获取CPE的正向认证方式
        
        参数：无
        
        返回值：执行成功，返回 认证方式;
                执行失败，raise 错误信息
                
        Example:
        | ${auth_method} | Get Acs Auth Method  |
        
        """
        
        ret         = None
        ret_data    = None
        ret_out     = None   
     
        ret, ret_data = self._query_cpe_info()                   
        if ret == ERR_SUCCESS:
            desc = u'获取CPE的正向认证方式成功。' 
            log.user_info(desc)
            
            ret_out = ret_data.auth_type            
        else:
            desc = u'获取CPE的正向认证方式失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                
            
        return ret_out    


    def set_acs_auth_method(self, method="digest"):
        """
        功能描述：修改正向连接认证方式
        
        参数： method: acs认证cpe的认证方式，eg："digest", "basic", "None"(无认证)
                       默认为"digest"   
               
        Example:
        | Set Acs Auth Method  | baisc  |
        | Set Acs Auth Method  | None  |
        """
        
        ret         = None
        ret_data    = None
        ret_out     = None   
        
        if (method not in ["digest", "basic", "None"]):
            desc = u'参数(method) 不支持'
            RuntimeError(desc)                         
        
        d1 = {}    
        d1["cpe_authtype"] = method
        
        ret, ret_data = self._update_cpe_info(d1)            
        if ret == ERR_SUCCESS:
            desc = u'修改正向连接认证方式成功。' 
            log.user_info(desc)
            
            ret_out = ret_data
        else:
            desc = u'修改正向连接认证方式失败，详细信息为：%s' %ret_data
            RuntimeError(desc) 
           
        return ret_out


    def get_max_session_timeout(self):
        """
        功能描述：获取CPE与ACS的最长会话时长
        
        参数：无
        
        返回值：执行成功，返回 最长会话时长;
                执行失败，raise 错误信息
                
        Example:
        | ${max_session} | Get Max Session Timeout  |
        
        """
        
        ret         = None
        ret_data    = None
        ret_out     = None   

        ret, ret_data = self._query_cpe_info()                   
        if ret == ERR_SUCCESS:
            desc = u'获取CPE与ACS的最长会话时长成功。' 
            log.user_info(desc)
            
            ret_out = ret_data.soap_inform_timeout            
        else:
            desc = u'获取CPE与ACS的最长会话时长失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)            
            
        return ret_out


    def set_max_session_timeout(self, timeout=180):
        """
        功能描述：修改CPE与ACS的最长会话超时
        
        参数： timeout: 超时时间，默认180s 
                
        Example:
        | Set Max Session Timeout  |  180  |
        
        注意:禁止设置大于等于300S.否则当CPE异常时ACS和Agent对此CPE的状态恢复会不同步导致后续测试异常.
            timeout合理值范围 [60, 300]
        """
        
        ret         = None
        ret_data    = None
        ret_out     = None
        
        d1 = {}
        # 对传入的timeout进行入参检查 GCW 20130426
        timeout2 = int(timeout)
        # make sure in [60, 300]; nwf 2013-06-07
        if (timeout2 < 60):
            timeout2 = 60
        elif (timeout2 > 300):
            timeout2 =300
            
        d1["soap_inform_timeout"] = timeout2

        ret, ret_data = self._update_cpe_info(d1)        
        if ret == ERR_SUCCESS:
            desc = u'修改CPE与ACS的最长会话超时成功。' 
            log.user_info(desc)
            
            ret_out = ret_data
        else:
            desc = u'修改CPE与ACS的最长会话超时失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)    
           
        return ret_out

        
    def get_cpe_software_version(self):
        """
        功能描述：获取CPE的软件版本号
        
        参数：无
        
        返回值：执行成功，返回 CPE的软件版本号;
                执行失败，raise 错误信息
                
        Example:
        | ${soft_version_num} | Get Cpe Software Version  |
        
        """
        
        ret         = None
        ret_data    = None
        ret_out     = None        
        
        ret, ret_data = self._query_cpe_info()                   
        if ret == ERR_SUCCESS:
            if (not ret_data.soap_inform):
                desc = u'获取CPE的软件版本号为空'                    
                ret_out = ""
            else:
                desc = u'获取CPE的软件版本号成功。'
                ret_out = ret_data.soap_inform.DeviceId.Softwareversion
                
            log.user_info(desc)
        else:
            desc = u'获取CPE的软件版本号失败，详细信息为：%s' %ret_data                
            raise RuntimeError(desc)
        
        return ret_out
        
        
    def get_cpe_hardware_version(self):
        """
        功能描述：获取CPE的硬件版本号
        
        参数：无
        
        返回值：执行成功，返回 CPE的硬件版本号;
                执行失败，raise 错误信息
                
        Example:
        | ${hard_version_num} | Get Cpe Hardware Version  |
        
        """
        
        ret         = None
        ret_data    = None
        ret_out     = None        
        
        ret, ret_data = self._query_cpe_info()       
        if ret == ERR_SUCCESS:                                
            if (not ret_data.soap_inform):
                desc = u'获取CPE的硬件版本号为空' 
                ret_out = ""
            else:
                desc = u'获取CPE的硬件版本号成功。' 
                ret_out = ret_data.soap_inform.DeviceId.Hardwareversion
            
            log.user_info(desc)
        else:
            desc = u'获取CPE的硬件版本号失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)
            
        return ret_out
        
        
    def get_cpe_connection_request_url(self):
        """
        功能描述：获取CPE的反向连接url
        
        参数：无
        
        返回值：执行成功，返回 CPE的反向连接url;
                执行失败，raise 错误信息
                
        Example:
        | ${url} | Get Cpe Connection Request Url  |
        
        """
        
        ret         = None
        ret_data    = None
        ret_out     = None                
        
        ret, ret_data = self._query_cpe_info()       
        if ret == ERR_SUCCESS:                                                
            # http://172.125.105.26:18015/tr069
            if (not ret_data.soap_inform):
                desc = u'获取CPE的反向连接url为空。' 
                ret_out = ""
            else:
                desc = u'获取CPE的反向连接url成功。' 
                ret_out = ret_data.soap_inform.DeviceId.ConnectionRequestURL
                
            log.user_info(desc)                    
        else:
            desc = u'获取CPE的反向连接url失败，详细信息为：%s' %ret_data                
            raise RuntimeError(desc)
        
        return ret_out
        
        
    def get_cpe_connection_request_ip(self):
        """
        功能描述：获取CPE的反向连接ip
        
        参数：无
        
        返回值：执行成功，返回 CPE的反向连接ip;
                执行失败，raise 错误信息
                
        Example:
        | ${ip} | Get Cpe Connection Request Ip  |
        
        """
        
        ret         = None
        ret_data    = None
        ret_out     = None                  
        
        ret, ret_data = self._query_cpe_info()       
        if ret == ERR_SUCCESS:                                            
            # http://172.125.105.26:18015/tr069 
            if (not ret_data.soap_inform):
                desc = u'获取CPE的反向连接ip为空。' 
                ret_out = ""
            else:
                desc = u'获取CPE的反向连接ip成功。' 
                url = ret_data.soap_inform.DeviceId.ConnectionRequestURL
                            
                ip_start = url.find(':')+3
                ip_end = url.find(':', 6)
                ret_out = url[ip_start:ip_end]

            log.user_info(desc)                
        else:
            desc = u'获取CPE的反向连接url失败，详细信息为：%s' %ret_data                
            raise RuntimeError(desc)

        return ret_out                
        
        
    def get_cpe_auth_info(self):
        """
        功能描述：获取CPE的反向认证信息，包括用户名和密码
        
        参数：无
        
        返回值：执行成功，返回 [username,password];
                执行失败，raise 错误信息
                
        Example:
        | ${ret_list} | Get Cpe Auth Info  |
        
        """
        
        ret         = None
        ret_data    = None
        ret_out     = None   
         
        ret, ret_data = self._query_cpe_info()                   
        if ret == ERR_SUCCESS:
            desc = u'获取CPE的反向认证信息成功。' 
            log.user_info(desc)
            
            username = ret_data.acs2cpe_loginname
            password = ret_data.acs2cpe_loginpassword
            ret_out = [username, password]            
        else:
            desc = u'获取CPE的反向认证信息失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)
            
        return ret_out                
        

    def set_cpe_auth_info(self, username="admin", password="admin"):
        """
        功能描述：修改反向连接认证的用户名和密码
        
        参数： username: cpe认证acs的用户名;
               password: cpe认证acs的密码
                 
        Example:
        | Set Cpe Auth Info  |username1  | password1  |
        """
        
        ret         = None
        ret_data    = None
        ret_out     = None   
           
        d1 = {}
        d1["cpe_auth_acs_username"] = username
        d1["cpe_auth_acs_password"] = password                        

        ret, ret_data = self._update_cpe_info(d1)            
        if ret == ERR_SUCCESS:
            desc = u'修改反向连接认证的用户名和密码成功。' 
            log.user_info(desc)
            
            ret_out = ret_data
        else:
            desc = u'修改反向连接认证的用户名和密码失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                    
           
        return ret_out    

        
    def get_cpe_cwmp_version(self):
        """
        功能描述：获取CPE的TR069版本号
        
        参数：无
        
        返回值：执行成功，返回 TR069版本号;
                执行失败，raise 错误信息
                
        Example:
        | ${cwmp_version} | Get Cpe Cwmp Version  |
        
        """
        
        ret         = None
        ret_data    = None
        ret_out     = None   
          
        ret, ret_data = self._query_cpe_info()                   
        if ret == ERR_SUCCESS:
            desc = u'获取CPE的TR069版本号成功。' 
            log.user_info(desc)
            
            ret_out = ret_data.cwmp_version            
        else:
            desc = u'获取CPE的TR069版本号失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)    
            
        return ret_out                                                                                                
        
        
    def set_cpe_cwmp_version(self, version="cwmp-1-0"):
        """
        功能描述：修改CPE支持的TR069版本号
        
        参数： version: TR069版本号，eg："cwmp-1-0", "cwmp-1-1", "cwmp-1-2", "cwmp-1-3" 等
                       默认为"cwmp-1-0"   
                 
        Example:
        | Set Cpe Cwmp Version  | cwmp-1-3  |
        """
        
        ret         = None
        ret_data    = None
        ret_out     = None   
                
        d1                  = {}                    
        d1["cwmp_version"]  = version
        
        ret, ret_data = self._update_cpe_info(d1)
        if ret == ERR_SUCCESS:
            desc = u'修改CPE支持的TR069版本号成功。' 
            log.user_info(desc)
            
            ret_out = ret_data
        else:
            desc = u'修改CPE支持的TR069版本号失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                    
           
        return ret_out      


    def get_cpe_online_status(self):
        """
        功能描述：获取CPE的在线状态
        
        参数：无
        
        返回值：执行成功，返回 在线状态;
                执行失败，raise 错误信息
                
        Example:
        | ${online_status}  | Get Cpe Online Status |
        
        """
        
        ret_api     = None
        ret_data    = None
        ret_out     = None   

        sn          = self._get_sn()         
        user1       = user.UserRpc(sn)
        
        # 修改函数，通过get_rpc_methods方法获取cpe的实时状态 zsj 2013/2/23
        ret_api, ret_data = user1.get_rpc_methods()               
        if ret_api == ERR_SUCCESS:
            ret_out = "online"
        else:
            ret_out = "offline"  
            log.user_info("%s:%s" %(ret_out, ret_data))
            
        desc = u'当前cpe状态:%s' %ret_out
        log.user_info(desc)
        
        return ret_out                   
                       

    # ------------------- new cpe keywords --------------------------------        
    
    def get_cpe_operator(self):
        """
        功能描述: 获取当前cpe的运营商属性 
        
        参数：空
            
        返回值：执行成功，返回 "CT"表示China Telecom; 返回"CU"表示China Unicom
                失败,抛出异常
        
        Example:
        |  ${cpe_operator}  |  Get Cpe Operator  |
        
        """

        ret         = None
        ret_data    = ""
        ret_out     = "" # RF ret
        desc        = ""

        ret, ret_data = self._query_cpe_info()             
        if ret == ERR_SUCCESS:

            ret_out = ret_data.cpe_operator
            
            desc = u"获取当前cpe的运营商属性成功，结果如下:%s" %ret_out
            log.user_info(desc)                            
        else:
            desc = u"%s" % (ret_data)  # fail, return err
            desc = u"获取当前cpe的运营商属性失败，结果如下:%s" %desc          
            
            raise RuntimeError(desc)                
        
        return ret_out

        
    def set_cpe_operator(self, operator="CT"):
        """
        功能描述：设置cpe 运营商属性
        
        参数:
            operator: "CT"表示China Telecom;
                      "CU"表示China Unicom;
                      "standard"表示标准TR069(不能执行工单).
            
        Example:
        |  Set Cpe Operator  |  CT  |
        
        """

        ret = None
        
        d1                  = dict()        
        d1["cpe_operator"]  = operator
        
        ret, ret_data = self._update_cpe_info(d1)
        if ret == ERR_SUCCESS:
            desc = u'设置cpe 运营商属性成功, 新的operator=%s'  %operator
            log.user_info(desc)        
        else:
            desc = u'设置cpe 运营商属性失败, 原因：%s'  %ret_data
            raise RuntimeError(desc)
        
        return None   


    def get_cpe_rollback(self):
        """
        功能描述: 获取某工单执行失败是否执行回滚操作的标识 
        
        参数：空
            
        返回值：执行成功，返回 "True" 或者 "False" (True表示工单执行失败时要回滚);              
                失败,抛出异常
        
        Example:
        |  ${rollback}  |  Get Cpe Rollback  |
        
        """

        ret         = None
        ret_data    = ""
        ret_out     = "" # RF ret
        desc        = ""

        ret, ret_data = self._query_cpe_info()             
        if ret == ERR_SUCCESS:

            ret_out = ret_data.worklist_rollback
            
            desc = u"获取某工单执行失败是否执行回滚操作的标识成功，结果如下:%s" %ret_out
            log.user_info(desc)                            
        else:
            desc = u"%s" % (ret_data)  # fail, return err
            desc = u"获取某工单执行失败是否执行回滚操作的标识失败，结果如下:%s" %desc          
            
            raise RuntimeError(desc)                
        
        return ret_out

        
    def set_cpe_rollback(self, rollback="False"):
        """
        功能描述：设置cpe执行工单失败时是否回滚的参数
        
        参数:
            rollback: CPE执行工单失败时 是否需要回滚/回退, True表示需要;False表示不需要
            
        Example:
        |  Set Cpe Rollback  |  True  |        
        """

        ret     = None
        
        d1      = dict()        
        rollback = str(rollback)
        if (rollback.lower() == "true"):
            rollback = True
        elif (rollback.lower() == "false"):
            rollback = False
        else:
            desc = u"rollback参数输入错误,请检查"
            raise RuntimeError(desc)
            
        d1["worklist_rollback"] = rollback
        
        ret, ret_data = self._update_cpe_info(d1)
        
        return None   


    def get_cpe_device_type(self):
        """
        功能描述：获取CPE的 设备类型
        
        参数：无
        
        返回值：执行成功，返回 CPE的 设备类型;
                执行失败，raise 错误信息
                
        Example:
        | ${device type} | Get Cpe Device Type  |
        
        """
        
        ret         = None
        ret_data    = None
        ret_out     = None    
          
        ret, ret_data = self._query_cpe_info()                   
        if ret == ERR_SUCCESS:
            
            ret_out = ret_data.worklist_domain
            
            desc = u'获取CPE的 设备类型成功, 结果如下:%s' %ret_out
            log.user_info(desc)
        else:
            desc = u'获取CPE的 设备类型失败，详细信息为：%s'%ret_data
            raise RuntimeError(desc)    
            
        return ret_out   


    def set_cpe_device_type(self, device_type):
        """
        功能描述：设置CPE的设备类型(设备类型模板)
        
        参数:
            device_type: CPE业务类型, 为了便于扩展,目前不做合法性判断,
            但在执行工单时如果没有找到相应的模板目录,则会工单出错.
            所以,建议设置为以下几个参考值,不区分大小写:
            | ADSL_2LAN | ADSL上行,二LAN口  |
            | ADSL_4+1  | ADSL上行,四LAN口,一POST口 |
            | ADSL_4LAN | ADSL上行,四LAN口 |
            | EPON_1+1  | EPON上行,一LAN口,一POST口 |
            | EPON_2+1  | EPON上行,二LAN口,一POST口 |
            | EPON_4+2  | EPON上行,四LAN口,二POST口 |
            | EPON_4LAN | EPON上行,四LAN口 |
            | GPON_1+1  | GPON上行,一LAN口,一POST口 |
            | GPON_2+1  | GPON上行,二LAN口,一POST口 |
            | GPON_4+2  | GPON上行,四LAN口,二POST口 |
            | GPON_4LAN | GPON上行,四LAN口 |
            | LAN_4+1   | LAN上行,四LAN口,一POST口 |
            | LAN_4+2   | LAN上行,四LAN口,二POST口 |
            | LAN_4LAN  | LAN上行,四LAN口 |
            | VDSL_4+1  | VDSL上行,四LAN口,一POST口 |
            | VDSL_4+2  | VDSL上行,四LAN口,二POST口 |
            | VDSL_4LAN | VDSL上行,四LAN口 |
        
        返回值：成功，无返回
                失败,抛出异常
               
        Example:
        |  Set Cpe Device Type  |  ADSL_4LAN  |        
        """
        ret = None 
        
        d1                      = {}
        # GCW 2013-04-05 强制转成大写.工单服务器的文件夹名为大写
        device_type = device_type.upper()
        d1["worklist_domain"]   = device_type
        
        ret, ret_data = self._update_cpe_info(d1)
        desc = u'设置CPE的设备类型(设备类型模板)成功, 新的device_type=%s'  %device_type
        log.user_info(desc)         
        
        return None        


    def get_last_faults(self):
        """
        功能描述：获取当前cpe上一次rpc请求的错误代码和错误信息, 
                如果上一个rpc是正常的，返回值为[];
                如果上一个rpc是错误的，返回错误列表.

        参数: 无

        返回值：成功,返回错误代码和错误信息的列表。
                失败,抛出异常

        Example:
        | ${faultinfolist} | Get Last Faults  |
        """

        ret_api     = ERR_FAIL
        ret_data    = ""
        ret_obj     = None  # event obj
        ret_out     = ""    # RF ret        
 
        sn          = self._get_sn()
         
        ret_api, ret_data = user.query_cpe_last_faults(sn)
        if ret_api == ERR_SUCCESS:
            
            ret_obj = ret_data
            ret_out = eval(ret_obj.dict_ret["str_result"])
            
            desc = u"获取当前CPE上一次rpc请求的错误代码和错误信息成功。"
            log.user_info(desc)                
        else:
            desc = u"获取当前CPE上一次rpc请求的错误代码和错误信息失败, 详细信息为: %s:" %ret_data
            raise RuntimeError(desc)

        return ret_out


    def manual_get_connection_request(self):
        """
        功能描述：手动向CPE发起一个反向连接请求, 
                成功, 通过抓包, CPE会回一个 "6 CONNECTION REQUEST"的inform; 
                失败, CPE无响应.        

        参数: 无

        返回值：无

        Example:
        |  Manual Get Connection Request  |
        """

        ret_api     = ERR_FAIL
        ret_data    = ""      
 
        sn          = self._get_sn()
        user1       = user.UserRpc(sn)
        
        ret_api, ret_data = user1.connection_request()
        if ret_api == ERR_SUCCESS:
            
            desc = u"手动向CPE发起一个反向连接请求成功。" 
            log.user_info(desc)                
        else:
            desc = u"手动向CPE发起一个反向连接请求失败, 详细信息为: %s:" %ret_data
            raise RuntimeError(desc)

        return None


    def set_cpe_interface_version(self, interface_version="AUTO"):
        """
        功能描述：设置CPE支持的 规范版本号
        
        参数:
            interface_version: CPE支持的 规范版本号.
            | v3.0 | 支持的接口规范为 v3.0  |
            | v4.0 | 支持的接口规范为 v4.0  |
            | AUTO | 默认取服务器支持的版本系列中的最小版本 |            
        
        返回值：成功，无返回
                失败,抛出异常
               
        Example:
        |  Set Cpe Interface Version  |  AUTO  |        
        """
        ret_api     = ERR_FAIL
        ret_data    = ""
        ret_obj     = None  # event obj
        ret_out     = "" # RF ret
        desc        = "" 
        
        sn          = self._get_sn()
        user1       = user.UserRpc(sn)         
        
        interface_version = interface_version.lower()
        if (interface_version == "v4.0"):
            # v4= need check       
            para_list = ["InternetGatewayDevice.DeviceInfo.X_CT-COM_InterfaceVersion"]
            ret_api, ret_data = user1.get_parameter_values(ParameterNames=para_list)               
            if (ret_api != ERR_SUCCESS):
                # 9005,invalid para name?
                if (isinstance(ret_data, dict)):
                    if (ret_data.get("FaultCode") == "9005"):            
                        desc = u'设置CPE支持的 规范版本号 失败, 设备不满足4.0规范，请升级固件.'
                        raise RuntimeError(desc)
                else:
                    desc = u'设置CPE支持的 规范版本号 失败, 详细信息为: %s:' %ret_data
                    log.user_info(desc)
                    
        # cfg
        d1                      = {}
        d1["interface_version"] = interface_version
        
        ret, ret_data = self._update_cpe_info(d1)
        if (ret == ERR_SUCCESS):
            desc = u'设置CPE支持的 规范版本号 成功, 新的 interface_version=%s'  %interface_version
            log.user_info(desc)         
        else:
            desc = u'设置cpe 规范版本号 失败, 原因：%s'  %ret_data
            raise RuntimeError(desc)            
            
        return None
    
    
    def get_cpe_interface_version(self):
        """
        功能描述：获取CPE支持的 规范版本号
        
        参数: 无

        返回值：成功，无返回
                失败,抛出异常
               
        Example:
        |  ${interface version}  |  Get Cpe Interface Version  |        
        """
        ret_api     = ERR_FAIL
        ret_data    = ""
        ret_obj     = None  # event obj
        ret_out     = ""    # RF ret        
 
        sn          = self._get_sn()
         
        ret_api, ret_data = user.query_cpe_interface_version(sn)
        if ret_api == ERR_SUCCESS:
            
            ret_obj = ret_data
            ret_out = ret_obj.dict_ret["str_result"]
            
            desc = u"获取CPE支持的 规范版本号 成功。"
            log.user_info(desc)                
        else:
            desc = u"获取CPE支持的 规范版本号 失败, 详细信息为: %s:" %ret_data
            raise RuntimeError(desc)

        return ret_out
    

    # ------------------- worklists keywords------------------------
    def _download_worklist(self):
        """
        功能描述：在工单服务器上查询工单相关的所有信息，返回当前支持的所有工单
        
        参数：无
        
        返回值：成功 返回所有工单服务器上支持的业务脚本集合 

        Example:
        |  Download Worklist  |                 
        """
        
        ret_api     = ERR_FAIL
        ret_data    = ""

        obj = user.UserWorklist()
        ret_api, ret_data = obj.worklistprocess_download()         
        if ret_api == ERR_SUCCESS:
            desc = u"下载工单信息成功。" 
            log.user_info(desc)                
        else:
            desc = u"下载工单信息失败，结果如下%s:" %ret_data
            raise RuntimeError(desc)
            
        return ret_data   
        

    def _get_worklist_record(self, obj_database):
        """
        obj_database = MsgWorklist
        """
        # show
        desc = """
        
id=%s
worklist_name=%s
sn=%s
cpe device type=%s
type=%s
username=%s
userid=%s
status=%s
rollback=%s
dict_data=%s
time_build=%s
time_bind=%s
time_reserve=%s
time_exec_start=%s
time_exec_end=%s

    """ %(obj_database.id_, 
        obj_database.worklist_name, 
        obj_database.sn, 
        obj_database.domain,
        obj_database.type_, 
        obj_database.username, 
        obj_database.userid, 
        obj_database.status, 
        obj_database.rollback, 
        obj_database.dict_data, 
        obj_database.time_build, 
        obj_database.time_bind, 
        obj_database.time_reserve,
        obj_database.time_exec_start, 
        obj_database.time_exec_end)
    
        return desc    


    def get_worklist_name(self, worklist_id):
        """
        功能描述: 获取某工单的名字
        
        参数：
            worklist_id: 需要查询的工单id
        
        返回值：成功,返回工单名字;
                失败,抛出异常
        
        Example:
        |  ${worklist_name}  |  Get Worklist Name  |  ID_1364950237391  |
        
        """
        
        ret_api     = ERR_FAIL
        ret_data    = ""
        ret_obj     = None  # event obj
        ret_out     = ""    # RF ret
        desc        = ""

        obj                 = user.UserWorklist()
        dict_data           = {}
        dict_data["id_"]    = worklist_id         
        
        ret_api, ret_data = obj.worklistprocess_query(**dict_data)           
        if ret_api == ERR_SUCCESS:

            ret_obj = ret_data
            ret_out = ret_obj.worklist_name   # success, return worklist_name
            
            desc = u"获取某工单的名字成功，结果如下:%s" %ret_out
            log.user_info(desc)                            
        else:
            desc = u"%s" % (ret_data)  # fail, return err
            desc = u"获取某工单的名字失败，结果如下:%s" %desc          
            
            raise RuntimeError(desc)                
        
        return ret_out   


    def get_worklist_bind_cpe_sn(self, worklist_id):
        """
        功能描述: 获取某工单绑定的CPE oui-sn
        
        参数：
            worklist_id: 需要查询的工单id

        返回值：成功,返回工单绑定的CPE oui-sn;
                失败,抛出异常
                
        Example:
        |  ${sn}  |  Get Worklist Bind Cpe Sn  |  ID_1364950237391  |
        
        """
        
        ret_api     = ERR_FAIL
        ret_data    = ""
        ret_obj     = None  # event obj
        ret_out     = "" # RF ret
        desc        = ""

        obj                 = user.UserWorklist()
        dict_data           = {}
        dict_data["id_"]    = worklist_id         
        
        ret_api, ret_data = obj.worklistprocess_query(**dict_data)           
        if ret_api == ERR_SUCCESS:

            ret_obj = ret_data
            ret_out = ret_obj.sn   # success, return sn
            
            desc = u"获取某工单绑定的CPE oui-sn成功，结果如下:%s" %ret_out
            log.user_info(desc)                            
        else:
            desc = u"%s" % (ret_data)  # fail, return err
            desc = u"获取某工单绑定的CPE oui-sn失败，结果如下:%s" %desc          
            
            raise RuntimeError(desc)                
        
        return ret_out   

    def get_worklist_bind_cpe_device_type(self, worklist_id):
        """
        功能描述: 获取某工单绑定的CPE Device Type
        
        参数：
            worklist_id: 需要查询的工单id
        
        返回值：成功,返回工单绑定的CPE Device Type;
                失败,抛出异常
                
        Example:
        |  ${cpe_device_type}  |  Get Worklist Bind Cpe Device Type  |  ID_1364950237391  |
        
        """
        
        ret_api     = ERR_FAIL
        ret_data    = ""
        ret_obj     = None  # event obj
        ret_out     = "" # RF ret
        desc        = ""

        obj                 = user.UserWorklist()
        dict_data           = {}
        dict_data["id_"]    = worklist_id         
        
        ret_api, ret_data = obj.worklistprocess_query(**dict_data)           
        if ret_api == ERR_SUCCESS:

            ret_obj = ret_data
            ret_out = ret_obj.domain   # success, return domain
            
            desc = u"获取某工单绑定的CPE Device Type成功，结果如下:%s" %ret_out
            log.user_info(desc)                            
        else:
            desc = u"%s" % (ret_data)  # fail, return err
            desc = u"获取某工单绑定的CPE Device Type失败，结果如下:%s" %desc          
            
            raise RuntimeError(desc)                
        
        return ret_out   


    def get_worklist_type(self, worklist_id):
        """
        功能描述: 获取某工单的类型
        
        参数：
            worklist_id: 需要查询的工单id
            
        返回值：成功,返回工单的类型;
                失败,抛出异常
                
        Example:
        |  ${worklist_type}  |  Get Worklist Type  |  ID_1364950237391  |
        
        """
        
        ret_api     = ERR_FAIL
        ret_data    = ""
        ret_obj     = None  # event obj
        ret_out     = "" # RF ret
        desc        = ""

        obj                 = user.UserWorklist()
        dict_data           = {}
        dict_data["id_"]    = worklist_id         
        
        ret_api, ret_data = obj.worklistprocess_query(**dict_data)           
        if ret_api == ERR_SUCCESS:

            ret_obj = ret_data
            ret_out = ret_obj.type_   # success, return type_
            
            desc = u"获取某工单的类型成功，结果如下:%s" %ret_out
            log.user_info(desc)                            
        else:
            desc = u"%s" % (ret_data)  # fail, return err
            desc = u"获取某工单的类型失败，结果如下:%s" %desc          
            
            raise RuntimeError(desc)                
        
        return ret_out   


    def get_worklist_userinfo(self, worklist_id):
        """
        功能描述: 获取某工单的用户信息        
        
        参数：
            worklist_id: 需要查询的工单id
            
        返回值：执行成功，返回(username, userid);
                失败,抛出异常
        
        Example:
        |  ${username}  |  ${userid}  |  Get Worklist Userinfo  |  ID_1364950237391  |
        
        注意：这里的username和id,是指执行逻辑工单时的username和id。
        
        """
        
        ret_api     = ERR_FAIL
        ret_data    = ""
        ret_obj     = None  # event obj
        ret_out     = "" # RF ret
        desc        = ""

        obj = user.UserWorklist()
        dict_data           = {}
        dict_data["id_"]    = worklist_id         
        
        ret_api, ret_data = obj.worklistprocess_query(**dict_data)           
        if ret_api == ERR_SUCCESS:

            ret_obj = ret_data
            ret_out = (ret_obj.username, ret_obj.userid)   # success, return (,)
            
            desc = u"获取某工单的用户信息成功，结果如下:%s" %str(ret_out)
            log.user_info(desc)                            
        else:
            desc = u"%s" % (ret_data)  # fail, return err
            desc = u"获取某工单的用户信息失败，结果如下:%s" %desc          
            
            raise RuntimeError(desc)                
        
        return ret_out   


    def get_worklist_status(self, worklist_id):
        """
        功能描述: 查询某工单的状态
        
        参数：
            worklist_id: 需要查询的工单id
            
        返回值：成功，返回工单的状态;
                失败,抛出异常
        
        Example:
        |  ${status}  |  Get Worklist Status  |  ID_1364950237391  |
        
        """
        
        ret_api     = ERR_FAIL
        ret_data    = ""
        ret_obj     = None  # event obj
        ret_out     = "" # RF ret
        desc        = ""

        obj = user.UserWorklist()
        
        dict_data           = {}
        dict_data["id_"]    = worklist_id         
        
        ret_api, ret_data = obj.worklistprocess_query(**dict_data)           
        if ret_api == ERR_SUCCESS:

            ret_obj = ret_data
            ret_out = ret_obj.status   # success, return 
            
            desc = u"查询某工单的状态成功，结果如下:%s" %ret_out
            log.user_info(desc)                            
        else:
            desc = u"%s" % (ret_data)  # fail, return err
            desc = u"查询某工单的状态失败，结果如下:%s" %desc          
            
            raise RuntimeError(desc)                
        
        return ret_out
    
    
    def get_worklist_args(self, worklist_id):
        """
        功能描述: 获取某工单的配置参数
        
        参数：
            worklist_id: 需要查询的工单id
            
        返回值：执行成功，返回工单的配置参数(字符串类型);
                失败,抛出异常
        
        Example:
        |  ${args}  |  Get Worklist Args  |  ID_1364950237391  |
        
        """
        
        ret_api     = ERR_FAIL
        ret_data    = ""
        ret_obj     = None  # event obj
        ret_out     = "" # RF ret
        desc        = ""

        obj = user.UserWorklist()
        
        dict_data           = {}
        dict_data["id_"]    = worklist_id         
        
        ret_api, ret_data = obj.worklistprocess_query(**dict_data)           
        if ret_api == ERR_SUCCESS:

            ret_obj = ret_data
            ret_out = str(ret_obj.dict_data) 
            
            desc = u"获取某工单的配置参数成功，结果如下:%s" %ret_out
            log.user_info(desc)                            
        else:
            desc = u"%s" % (ret_data)  # fail, return err
            desc = u"获取某工单的配置参数失败，结果如下:%s" %desc          
            
            raise RuntimeError(desc)                
        
        return ret_out       


    def get_worklist_times(self, worklist_id):
        """
        功能描述: 获取某工单的时间记录信息
        
        参数：
            worklist_id: 需要查询的工单id
            
        返回值：执行成功，返回(build的时间, bind的时间, 工单执行开始的时间, 执行结束的时间);
                失败,抛出异常
        
        Example:
        |  ${build_time}  |  ${bind_time}  |  ${start_exec_time}  |  ${end_exec_time}  |  Get Worklist Times  |  ID_1364950237391  |
        
        """
        
        ret_api     = ERR_FAIL
        ret_data    = ""
        ret_obj     = None  # event obj
        ret_out     = "" # RF ret
        desc        = ""

        obj = user.UserWorklist()
        
        dict_data           = {}
        dict_data["id_"]    = worklist_id         
        
        ret_api, ret_data = obj.worklistprocess_query(**dict_data)           
        if ret_api == ERR_SUCCESS:

            ret_obj = ret_data
            ret_out = (ret_obj.time_build, ret_obj.time_bind, ret_obj.time_exec_start, ret_obj.time_exec_end)   # success, return 
            
            desc = u"获取某工单的时间记录信息成功，结果如下:%s" %str(ret_out)
            log.user_info(desc)                            
        else:
            desc = u"%s" % (ret_data)  # fail, return err
            desc = u"获取某工单的时间记录信息失败，结果如下:%s" %desc          
            
            raise RuntimeError(desc)                
        
        return ret_out      


    def get_worklist_logs(self, worklist_id):
        """
        功能描述: 获取某工单执行过程日志.
        
        参数：
            worklist_id: 需要查询的工单id
            
        返回值：执行成功，返回工单的过程日志;
                失败,抛出异常
        
        Example:
        |  ${dict_data}  |  Get Worklist Logs  |  ID_1364950237391  |
        
        """
        
        ret_api     = ERR_FAIL
        ret_data    = ""
        ret_obj     = None  # event obj
        ret_out     = "" # RF ret
        desc        = ""

        obj = user.UserWorklist()
        
        dict_data           = {}
        dict_data["id_"]    = worklist_id         
        
        ret_api, ret_data = obj.worklistprocess_query(**dict_data)
        if ret_api == ERR_SUCCESS:

            ret_obj = ret_data
            
            ret_status = ret_obj.status
            if ret_status not in ["fail", "success"]:
                desc = u"工单的当前状态(%s)为非结束状态,不支持对其查询测试结果日志" % ret_status
                log.user_info(desc)
                return
            
            ret_out = ret_obj.dict_ret   # success, return 
            
            ret_out = ret_out["str_result"]            
            desc = u"获取某工单执行过程日志成功，结果如下:%s" %ret_out
            log.user_info(desc)                            
        else:
            desc = u"%s" % (ret_data)  # fail, return err
            desc = u"获取某工单执行过程日志失败，结果如下:%s" %desc          
            
            raise RuntimeError(desc)                
        
        return ret_out

    
    def get_telecom_account_password(self):
        """
        功能描述: 获取维护帐号密码
        
        参数:无
        
        返回值：成功，返回维护密码(WEB页面登录密码);
                失败,抛出异常
                
        Example:
        |  ${password}  |  Get Telecom Account Password  |
        
        """
        
        ret_api     = ERR_FAIL
        dict_args   = {}
        ret_out     = "" # RF ret    
        
        sn          = self._get_sn()                
        id_ = self._init_worklist("Auto_GetTelecomAccountPassword", 
                                str(dict_args), 
                                "SYS")
        self.bind_physic_worklist(id_, sn)
        self.execute_worklist(id_)
        
        ret_out = self.get_worklist_logs(id_)
        
        return ret_out


    def _init_worklist(self, worklist_name, str_dict_args, group="SYS"):
        """
        功能描述：初始化需要执行的工单参数
        
        参数:
            worklist_name: 初始化需要执行的工单名字;
            str_dict_args: 初始化需要执行的工单参数
            group       :   "USER" or "SYS"
        
        返回值：成功，返回工单ID号
                失败,抛出异常
               
        Example:
        |  ${id}  |  Init Worklist  |  WLAN_ADD  |  {"Num":("4", "1")}  |
        
        注意:此关键字是为以后扩展用户自定义工单用,暂时不建议用户使用.
        """
        
        ret_api     = ERR_FAIL
        ret_data    = ""
        ret_obj     = None  # event obj
        ret_out     = "" # RF ret
        desc        = ""

        obj = user.UserWorklist()
        
        dict_data                   = {}
        dict_data["worklist_name"]  = worklist_name
        dict_data["dict_data"]      = eval(str_dict_args)
        dict_data["group"]          = group        
        
        ret_api, ret_data = obj.worklistprocess_build(**dict_data)          
        if ret_api == ERR_SUCCESS:

            ret_obj = ret_data
            ret_out = ret_obj.id_   # success, return id
            desc = u"%s" % (ret_out)
            desc = u"初始化工单(%s)成功，返回工单序号:%s" % (worklist_name, desc)
            log.user_info(desc)     
        else:
            desc = u"%s" % (ret_data) # fail, return err
            desc = u"初始化工单(%s)失败，结果如下:%s" % (worklist_name, desc)
            
            raise RuntimeError(desc)                
        
        return ret_out 


    def init_worklist(self, worklist_name, *args):
        """
        功能描述：初始化需要执行的工单参数
        
        参数:
            worklist_name: 初始化需要执行的工单名字;
            args:          表示可选参数，传入的格式为"varname=value",具体参数描述如下;
        
        *注：当用户不输入时使用模板中的默认参数，args支持单个输入单个参数，但必须要按参数顺序输入，建议使用"varname=value"格式；
        
        返回值：成功，返回工单ID号
                失败,抛出异常
               
        Example:
        
        |  ${id}  |  Init Worklist  |  QoS_IP  |
        |  ${id}  |  Init Worklist  |  QoS_IP  | Min=222.66.65.57 | DSCPMarkValue=2 | M802_1_P_Value=2 |ClassQueue=1 |
        |  ${id}  |  Init Worklist  |  QoS_IP  | 222.66.65.57 | DSCPMarkValue=2 | M802_1_P_Value=2 |ClassQueue=1 |
        |  ${id}  |  Init Worklist  |  QoS_IP  | 222.66.65.57 |  | ClassQueue=1 | 2 |

        """
        
        ret_api     = ERR_FAIL
        ret_data    = ""
        ret_obj     = None  # event obj
        ret_out     = "" # RF ret
        desc        = ""

        obj = user.UserWorklist()
        
        dict_data                   = {}
        dict_data["worklist_name"]  = worklist_name
        
        if len(args) == 1:
            try:
                temp_data = eval(args[0])
                if isinstance(temp_data, dict):
                    dict_data["dict_data"] = temp_data
                else:
                    dict_data["dict_data"] = self._convert_worklist_args(args)
                
            except Exception:
                dict_data["dict_data"] = self._convert_worklist_args(args)
        else:  
            dict_data["dict_data"]      = self._convert_worklist_args(args)
        
        ret_api, ret_data = obj.worklistprocess_build(**dict_data)          
        if ret_api == ERR_SUCCESS:

            ret_obj = ret_data
            ret_out = ret_obj.id_   # success, return id
            desc = u"%s" % (ret_out)
            desc = u"初始化工单(%s)成功，返回工单序号:%s" % (worklist_name, desc)
            log.user_info(desc)     
        else:
            desc = u"%s" % (ret_data) # fail, return err
            desc = u"初始化工单(%s)失败，结果如下:%s" % (worklist_name, desc)
            
            raise RuntimeError(desc)                
        
        return ret_out 


    def bind_physic_worklist(self, worklist_id, sn=""):
        """
        功能描述：绑定物理工单 
        
        参数:
            worklist_id: 需要绑定的工单id;
            sn: cpe的oui-sn，为空表示当前cpe
        
        返回值：成功，无返回;
                失败,抛出异常
               
        Example:
        |  Bind Physic Worklist  |  ID_1364950237391  |  00904C-2013012901  |
        
        """

        ret_api         = ERR_FAIL
        ret_data        = ""
        desc            = ""

        if (sn == ""):
           sn = self._get_sn()          

        obj = user.UserWorklist()
        
        dict_data           = {}
        dict_data["id_"]    = worklist_id
        dict_data["sn"]     = sn
        
        ret_api, ret_data = obj.worklistprocess_bind_physical(**dict_data)           
        if ret_api == ERR_SUCCESS:

            desc = u"绑定物理工单成功。"  # success, only desc 
            log.user_info(desc)
        else:
            desc = u"绑定物理工单失败，结果如下:%s" %ret_data            
            raise RuntimeError(desc)                
        
        return None 


    def bind_logic_worklist(self, worklist_id, username, userid):
        """
        功能描述：绑定逻辑工单 
        
        参数:
            worklist_id:        需要绑定的工单id;
            username:   逻辑工单的username;
            userid:     逻辑工单的userid
        
        返回值：成功，无返回;
                失败,抛出异常
               
        Example:
        |  Bind Logic Worklist  |  ID_1364950237391  |  username  |  userid  |
        
        """
        
        ret_api     = ERR_FAIL
        ret_data    = ""
        desc        = ""


        obj         = user.UserWorklist()
        
        dict_data               = {}
        dict_data["id_"]        = worklist_id
        dict_data["username"]   = username
        dict_data["userid"]     = userid            
        
        ret_api, ret_data = obj.worklistprocess_bind_logical(**dict_data)         
        if ret_api == ERR_SUCCESS:
                             
            desc = u"绑定逻辑工单成功。" # success, only desc   
            log.user_info(desc)
        else:
            desc = u"绑定逻辑工单失败，结果如下:%s" %ret_data            
            raise RuntimeError(desc)                
        
        return None 

        
    def _get_worklist_exec_info(self, worklist_id):
        """
        """
        ret_api     = ERR_FAIL
        ret_data    = ""
        ret_obj     = None  # event obj
        ret_out     = "" # RF ret
        desc        = ""

        # query worklist
        obj = user.UserWorklist()
        
        dict_data           = {}
        dict_data["id_"]    = worklist_id         
        
        ret_api, ret_data = obj.worklistprocess_query(**dict_data)          
        if ret_api != ERR_SUCCESS:
            desc = u"%s" % (ret_data)  # fail, return err
            desc = u"查询某工单的详细信息失败，结果如下:%s" %desc            
            raise RuntimeError(desc)
        
        ret_obj = ret_data
        
        # query cpe
        ret_api, ret_data = user.query_cpe_info(ret_obj.sn)
        if ret_api != ERR_SUCCESS:
            desc = u'查询CPE信息失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)
        
        ret_obj = ret_data
        # show cpe info
        desc = u""" 执行工单前的CPE信息:
operator运营商=%s,
interface version接口规范=%s,
cpe device type设备类型=%s
""" %(ret_obj.cpe_operator, ret_obj.interface_version, ret_obj.worklist_domain)
        
        return desc
    
        
    def execute_worklist(self, worklist_id):
        """
        功能描述：执行工单 
        
        参数:
            worklist_id:需要执行的工单id
        
        返回值：成功，无返回;
                失败,抛出异常
               
        Example:
        |  Execute Worklist  |  ID_1364950237391  |
        
        """
        
        ret_api     = ERR_FAIL
        ret_data    = ""
        ret_obj     = None  # event obj
        ret_out     = "" # RF ret
        desc        = ""

        # show info
        #desc = self._get_worklist_exec_info(worklist_id)
        #log.user_info(desc)

        obj = user.UserWorklist()
        
        dict_data           = {}
        dict_data["id_"]    = worklist_id         
        
        ret_api, ret_data = obj.worklistprocess_execute(**dict_data)
        if ret_api == ERR_SUCCESS:
            ret_obj = ret_data
            ret_out = ret_obj.dict_ret.get("str_result")
        
            desc = u"执行工单成功，结果如下:%s" %ret_out
            log.user_info(desc)
        else:
            # agent error?
            if (isinstance(ret_data, Exception) or
                (isinstance(ret_data, basestring))):
                desc = ret_data
            else:
                # worklist error
                ret_obj = ret_data
                ret_out = ret_obj.dict_ret.get("str_result")
                desc = ret_out
            
            desc = u"执行工单失败，结果如下:%s" %desc
            
            raise RuntimeError(desc)                
        
        return None 
    
    
    def query_worklist(self, worklist_id):
        """
        功能描述: 查询某工单的详细信息
        
        参数：
            worklist_id: 需要查询的工单id
        
        返回值：成功，无返回;
                失败,抛出异常
               
        Example:
        |  Query Worklist  |  ID_1364950237391  |
        
        """
        
        ret_api     = ERR_FAIL
        ret_data    = ""
        ret_obj     = None  # event obj
        desc        = ""

        obj = user.UserWorklist()
        
        dict_data           = {}
        dict_data["id_"]    = worklist_id         
        
        ret_api, ret_data = obj.worklistprocess_query(**dict_data)          
        if ret_api == ERR_SUCCESS:

            ret_obj = ret_data
            desc = self._get_worklist_record(ret_obj)  # success, show log                    
            desc = u"查询某工单的详细信息成功，结果如下:%s" %desc
            log.user_info(desc)
        else:
            desc = u"%s" % (ret_data)  # fail, return err
            desc = u"查询某工单的详细信息失败，结果如下:%s" %desc
            
            raise RuntimeError(desc)                
        
        return desc          
    
    # -------------------wait inform keywords ---------------------------------------  
    def wait_next_inform(self, timeout=120):
        """
        功能描述：发送命令，等待CPE的下一个inform(任何eventcode值)
        
        参数：
        | timeout | 超时时间，单位秒 |
        
        Example:
        | Wait Next Inform | 120 |
        
        """
        ret_api         = None
        ret_data        = None
           
        sn = self._get_sn()  
        
        timeout2 = int(timeout)
        ret_api, ret_data = user.wait_next_inform(sn, timeout2)
        if ret_api == ERR_SUCCESS:
            desc = u'等待CPE的下一个inform成功。' 
            log.user_info(desc)
            
        else:
            desc = u'等待CPE的下一个inform失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                    
           
        return None 
    
    
    def init_wait_eventcode(self, include_eventcodes, exclude_eventcodes=[]):
        """
        功能描述：初始化生成一个 wait_eventcode 的任务
        
        参数：
        | include_eventcodes | 同一个 inform 里面包含的 eventcode 列表 |
        | exclude_eventcodes | 同一个 inform 里面不能被包含的 eventcode 列表 |
        
        返回值：
        | 执行成功 | 返回本次 wait_eventcode 任务ID |        

        Example:
        | ${id} | Init Wait EventCode | 8 DIAGNOSTICS COMPLETE |
        | ${id} | Init Wait EventCode | 8 DIAGNOSTICS COMPLETE | 6 CONNECTION REQUEST  |
        
        | ${include_eventcodes} | Create List  | 1 BOOT |  2 PERIODIC  |  |
        | ${exclude_eventcodes} | Create List  | 6 CONNECTION REQUEST |  8 DIAGNOSTICS COMPLETE | X CT-COM ALARM |
        | ${id} | Init Wait EventCode | ${include_eventcodes} | ${exclude_eventcodes}  |        
        
        """            
        
        ret_api         = None
        ret_data        = None
        ret_obj         = None  # event obj
        ret_out         = ""    # RF ret        
           
        sn = self._get_sn()  

        # convert
        include_eventcodes2 = include_eventcodes
        exclude_eventcodes2 = exclude_eventcodes
        if (not isinstance(include_eventcodes, list)):
            include_eventcodes2 = []
            include_eventcodes2.append(include_eventcodes)
            
        if (not isinstance(exclude_eventcodes, list)):
            exclude_eventcodes2 = []
            exclude_eventcodes2.append(exclude_eventcodes)

        ret_api, ret_data = user.init_wait_eventcode(sn, include_eventcodes2, exclude_eventcodes2)                   
        if ret_api == ERR_SUCCESS:
            ret_obj = ret_data
            ret_out = ret_obj.id_
            
            desc = u'初始化生成一个 wait_eventcode 的任务成功。' 
            log.user_info(desc)
            
        else:
            desc = u'初始化生成一个 wait_eventcode 的任务失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                    
           
        return ret_out         
    
    
    def start_wait_eventcode(self, wait_eventcode_id):
        """
        功能描述：开始 wait_eventcode 任务
        
        参数：
        | wait_eventcode_id | init_wait_eventcode 返回的id |
        
        Example:               
        | start_wait_eventcode | ID_wait_eventcode_2013-08-06_10:33:42.241000_12345678 |
        
        """
        ret_api         = None
        ret_data        = None
           
        sn = self._get_sn()  

        ret_api, ret_data = user.start_wait_eventcode(sn, wait_eventcode_id)                   
        if ret_api == ERR_SUCCESS:
            desc = u'开始 wait_eventcode 任务成功。' 
            log.user_info(desc)
            
        else:
            desc = u'开始 wait_eventcode 任务失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                    
           
        return None         
    
    
    def check_result_and_stop_wait_eventcode(self, wait_eventcode_id, timeout=120):
        """
        功能描述：在timeout时间内，每隔一段时间(3s) 向服务器查询，是否满足 init_wait_eventcode 的配置要求。
                满足要求则立刻返回成功; 不满足要求，则延时等候最长timeout时间。
                该关键字返回前, 会自动结束掉 init_wait_eventcode 创建的任务。
        
        参数：
        | wait_eventcode_id | init_wait_eventcode 返回的id |
        | timeout | 向服务器查询持续的最长时间, 单位秒 |
        
        返回值：
        | 执行成功 | 说明满足 init_wait_eventcode 任务的配置要求 |
        | 执行失败 | 说明不满足 init_wait_eventcode 任务的配置要求 |
        
        Example:               
        | Check Result and Stop Wait EventCode | ID_wait_eventcode_2013-08-06_10:33:42.241000_12345678 |
        | Check Result and Stop Wait EventCode | ID_wait_eventcode_2013-08-06_10:33:42.241000_12345678 | 300 |
        
        """
        ret_api         = None
        ret_data        = None
           
        sn = self._get_sn()
        
        timeout2 = int(timeout)

        ret_api, ret_data = user.check_result_and_stop_wait_eventcode(sn, wait_eventcode_id, timeout2)                   
        if ret_api == ERR_SUCCESS:
            desc = u'检查wait_eventcode任务成功。' 
            log.user_info(desc)
            
        else:
            desc = u'检查wait_eventcode任务失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                    
           
        return None      


    # -------------------alarm/monitor keywords ---------------------------------------
    def init_alarm(self, parameterlist, limit_min, limit_max, timelist=1, mode=1):
        """
        功能描述：初始化一个告警流程
        
        注意: 联通的CPE，告警规则固定，只需要init_alram动作，参数任意配置
        
        参数：
        | parameterlist | 需要监控的关键参数（TR069参数模型全路径），例如：InternetGatewayDevice.WANDevice.{i}.X_CT-COM_EponInterfaceConfig.Stats. BytesSent  |
        | limit_min     | 需要监控的关键参数的最小范围 |
        | limit_max     | 需要监控的关键参数的最大范围 |        
        | timelist      | 告警周期，单位为：分钟  |
        | mode          | 告警取值方式，1：累加值，2：平均值，3：瞬间值 |
        
        返回值：
        | 执行成功 | 返回本次告警流程ID |
        
        Example:
        | ${id} | Init Alarm | InternetGatewayDevice.WANDevice.1.WANConnectionDevice.7.WANIPConnection.1.Stats.EthernetBytesReceived | 2000 | 3000 | 1 | 1 |
        
        """
        ret_api         = None
        ret_data        = None
        ret_obj         = None  # event obj
        ret_out         = ""    # RF ret
           
        sn = self._get_sn()  
        
        ret_api, ret_data = user.init_alarm(sn, parameterlist, limit_max, limit_min, timelist, mode)                   
        if ret_api == ERR_SUCCESS:
            desc = u'初始化一个告警流程成功。' 
            log.user_info(desc)
            
            ret_obj = ret_data
            ret_out = ret_obj.id_
        else:
            desc = u'初始化一个告警流程失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                    
           
        return ret_out
    
    
    def start_alarm(self, alarm_id):
        """
        功能描述：开始告警流程
        
        参数：
        | alarm_id | Init Alarm 返回的ID |
        
        返回值：
        | 执行成功 | 返回None |
        | 执行失败 | 异常 |
        
        Example:
        | Start Alarm | ID_alarm_2013-05-30_10:33:42.241000  |
        
        """
        ret_api         = None
        ret_data        = None
           
        sn = self._get_sn()  
        
        ret_api, ret_data = user.start_alarm(sn, alarm_id)                   
        if ret_api == ERR_SUCCESS:
            desc = u'开始告警流程成功。' 
            log.user_info(desc)
            
        else:
            desc = u'开始告警流程失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                    
           
        return None  


    def stop_alarm(self, alarm_id):
        """
        功能描述：停止告警流程
        
        参数：
        | ${alarm_id} | Init Alarm 返回的ID |
        
        Example:
        | Stop Alarm |  ID_alarm_2013-05-30_10:33:42.241000 |
        
        """
        ret_api         = None
        ret_data        = None
           
        sn = self._get_sn()  
        
        ret_api, ret_data = user.stop_alarm(sn, alarm_id)                   
        if ret_api == ERR_SUCCESS:
            desc = u'停止告警流程成功。' 
            log.user_info(desc)
            
        else:
            desc = u'停止告警流程失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                    
           
        return None  


    def get_alarm_values(self, alarm_id):
        """
        功能描述：告警流程开始后，从满足告警条件的inform中获得监控节点值
        
        参数：
        | ${alarm_id} | Start Alarm返回的ID |
        
        返回值: [(time1, value1), (time2, value2), ...]
        
        注意：联通的CPE，返回值[(time1, inform1), (time2, inform2), ...]
        
        Example:
        | ${values}  | Get Alarm Values |  ID_alarm_2013-05-30_10:33:42.241000 |
        
        """
        ret_api         = None
        ret_data        = None
        ret_obj         = None
        ret_out         = None       
        ret_out_4log    = None
        ret_out_4ret    = None
        values          = ""
                   
        sn = self._get_sn()  

        ret_api, ret_data = user.get_alarm_values(sn, alarm_id)                   
        if ret_api == ERR_SUCCESS:
            desc = u'获取告警值成功。返回值如下:'
            log.user_info(desc)

            ret_obj = ret_data
            ret_out = ret_obj.parameter_values

            # nwf 2013-07-08; datetime obj->datetime str
            ret_out_4log = []
            ret_out_4ret = []
            for time1,value1 in ret_out:
                # for show
                time1.strftime('%Y-%m-%d %H:%M:%S %f')
                ret_out_4log.append((str(time1), value1))

                # for return
                seconds = (time1-datetime(1970,1,1)).total_seconds()
                seconds = int(round(seconds))
                ret_out_4ret.append((seconds, value1))   

                # for cu
                values = values + value1 + "\r\n"
            
            log.user_info(str(ret_out_4log))  # show datetime str
            
            # for cu 
            desc = u'显示值如下:'
            log.user_info(desc)
            log.user_info(values)
            
            ret_out = ret_out_4ret                  
            
        else:
            desc = u'获取告警值失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                    
           
        return ret_out  


    def init_monitor(self, parameterlist, timelist=1):
        """
        功能描述：初始化一个监控流程
        
        参数：
        | parameterlist | 需要监控的关键参数（TR069参数模型全路径），例如：InternetGatewayDevice.WAN¬Device.{i}.X_CT-COM_EponInterfaceConfig.Stats.BytesSent |
        | timelist      | 采样周期，单位为：分钟  |
        
        返回值：
        | 执行成功 | 返回本次监控流程ID |
        
        Example:
        | ${id} | Init Monitor | InternetGatewayDevice.WANDevice.1.WANConnectionDevice.7.WANIPConnection.1.Stats.EthernetBytesReceived | 1 |
        
        """
        ret_api         = None
        ret_data        = None
        ret_obj         = None  # event obj
        ret_out         = ""    # RF ret        
           
        sn = self._get_sn()  
        
        ret_api, ret_data = user.init_monitor(sn, parameterlist, timelist)                   
        if ret_api == ERR_SUCCESS:
            desc = u'初始化一个监控流程成功。' 
            log.user_info(desc)
            
            ret_obj = ret_data
            ret_out = ret_obj.id_
        else:
            desc = u'初始化一个监控流程失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                    
           
        return ret_out  


    def start_monitor(self, monitor_id):
        """
        功能描述：开始监控流程
        
        参数：
        | ${monitor_id} | Init Monitor 返回的ID |
        
        返回值：
        | 执行成功 | 返回 None |
        | 执行失败 | 异常 |
        
        Example:
        | Start Monitor | ID_monitor_2013-05-30_10:33:42.241000 |
        
        """
        ret_api         = None
        ret_data        = None
           
        sn = self._get_sn()  
        
        ret_api, ret_data = user.start_monitor(sn, monitor_id)                   
        if ret_api == ERR_SUCCESS:
            desc = u'开始监控流程成功。' 
            log.user_info(desc)
            
        else:
            desc = u'开始监控流程失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                    
           
        return None  


    def stop_monitor(self, monitor_id):
        """
        功能描述：停止监控流程
        
        参数：
        | ${monitor_id} | Init Monitor 返回的ID |
        
        Example:
        | Stop Monitor |  ID_monitor_2013-05-30_10:33:42.241000 |
        
        """
        ret_api         = None
        ret_data        = None
           
        sn = self._get_sn()  
        
        ret_api, ret_data = user.stop_monitor(sn, monitor_id)                   
        if ret_api == ERR_SUCCESS:
            desc = u'停止监控流程成功。' 
            log.user_info(desc)
            
        else:
            desc = u'停止监控流程失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                    
           
        return None  


    def get_monitor_values(self, monitor_id):
        """
        功能描述：监控流程开始后，从满足监控条件的inform中获得监控节点的值
        
        参数：
        | monitor_id | Start Monitor 返回的ID |
        
        返回值: [(time1, value1), (time2, value2), ...]        
        
        Example:    
        | ${values}  | Get Monitor Values |  ID_monitor_2013-05-30_10:33:42.241000 |
        
        """
        ret_api         = None
        ret_data        = None
        ret_obj         = None
        ret_out         = None
        ret_out_4log    = None
        ret_out_4ret    = None        
           
        sn = self._get_sn()  

        ret_api, ret_data = user.get_monitor_values(sn, monitor_id)                   
        if ret_api == ERR_SUCCESS:
            desc = u'获取监控值成功。返回值如下:' 
            log.user_info(desc)
            
            ret_obj = ret_data
            ret_out = ret_obj.parameter_values
            
            # nwf 2013-07-08; datetime obj->datetime str
            ret_out_4log = []
            ret_out_4ret = []
            for time1,value1 in ret_out:
                time1.strftime('%Y-%m-%d %H:%M:%S %f')
                ret_out_4log.append((str(time1), value1))
            
                # for return
                seconds = (time1-datetime(1970,1,1)).total_seconds()
                seconds = int(round(seconds))
                ret_out_4ret.append((seconds, value1))                
            
            log.user_info(str(ret_out_4log))  # show datetime str      
            
            ret_out = ret_out_4ret         
            
        else:
            desc = u'获取监控值失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                    
           
        return ret_out  



    def get_last_session_soap(self):
        """
        功能描述：得到上一次ACS与CPE交互的RPC的SOAP包
        
        参数：空
        
        返回值：
        | 执行成功 | 以字符串形式返回soap包 |
        | 执行失败 | 异常 |        
        
        Example:
        | ${soap} |  Get Last Session Soap  |
        
        """
        ret_api         = None
        ret_data        = None
        ret_obj         = None  # event obj
        ret_out         = ""    # RF ret        
           
        sn = self._get_sn()  
        
        ret_api, ret_data = user.query_last_session_soap(sn)                   
        if ret_api == ERR_SUCCESS:
            desc = u'得到上一次ACS与CPE交互的RPC的SOAP包成功。' 
            log.user_info(desc)
            
            ret_obj = ret_data
            ret_out = ret_obj.dict_ret["str_result"]
        else:
            desc = u'得到上一次ACS与CPE交互的RPC的SOAP包失败，详细信息为：%s' %ret_data
            raise RuntimeError(desc)                    
           
        return ret_out  

    def _get_random_command_key(self):
        """
        string(32)
        eg = 2013-11-22_15:02:49.845000_8819
        """
        dt1     = datetime.now()
        random1 = random.randrange(1000, 10000)
        command_key = "%s_%s_%s" %(dt1.date(), dt1.time(), random1)
        
        desc = "auto command_key = %s" %command_key
        log.user_info(desc)
        
        return command_key
    
    def _convert_worklist_args(self, list_args):
        """
        函数功能：对用户输入的list类型的工单参数做转换，转为dict
        参数：
            list_args： list型的工单参数，list中的参数可能是单个字符串，可能是由"key=value"组成的字符串
        返回值：
            dict_data： 对list_args转换后的字典数据
        """
        dict_data = {}
        
        i = 1
        for key_value in list_args:
            index = "%s" % i
            list_data = key_value.split('=', 1)
            if len(list_data) <= 1:
                key = index
                value = list_data[0]
            elif list_data[0].rstrip()=="":
                key = index
                value = key_value
            else:
                key = list_data[0]
                value = list_data[1]

            dict_data.update({key:(value,index)})

            i += 1
        
        return dict_data

   
def test_rpc():

    if (1):
        x = obj.set_cpe_interface_version("Auto")
        print x

    if (0):
        x2=obj.get_last_faults()
        print x2

    if (0):
        x=obj.get_rpc_methods()
        print x
        
    if (0):
        x2=obj.get_last_faults()
        print x2        
        
    if (0):
        x=obj.add_object("InternetGatewayDevice.WANDevice.11.WANConnectionDevice.")
        print x
    

    
    
    
def test_cpe_query_update():
    
    x=obj.get_telecom_account_password()
    print x
  
    
    
    x=obj.get_acs_auth_info()
    print x
    x=obj.set_acs_auth_info("admin", "admin")
    print x
    
    x=obj.get_acs_auth_method()
    print x
    x=obj.set_acs_auth_method("digest")
    print x    
    
    x=obj.get_max_session_timeout()
    print x
    x=obj.set_max_session_timeout(240)
    print x
    
    x=obj.get_cpe_software_version()
    print x

    x=obj.get_cpe_hardware_version()
    print x
    
    x=obj.get_cpe_connection_request_url()
    print x
    x=obj.get_cpe_connection_request_ip()
    print x
    
    x=obj.get_cpe_auth_info()
    print x
    x=obj.set_cpe_auth_info("admin", "admin")
    print x
    
    x=obj.get_cpe_cwmp_version()
    print x
    x=obj.set_cpe_cwmp_version()
    print x
    
    x=obj.get_cpe_online_status()
    print x
    

    x=obj.set_cpe_rollback("True")
    print x
    x=obj.get_cpe_rollback()
    print x    

    x=obj.set_cpe_device_type("ADSL")
    print x
    x=obj.get_cpe_device_type()
    print x
    
def test_worklist():

    x = obj.set_cpe_device_type("ADSL")
    x = obj.set_cpe_rollback("True")
    
    if (1):
        dict_data = {"key1":"value1", "key2":"value2"}
        str_dict_data = str(dict_data)
        id1 =  obj.init_worklist("test", str_dict_data)
        
        
        x,y = obj.get_worklist_userinfo(id1)
        
        
        obj.query_worklist(id1)
        
        x1 = obj.bind_physic_worklist(id1)
        obj.query_worklist(id1)
    
        x2 = obj.execute_worklist(id1)
        obj.query_worklist(id1)
    
        # rpc
        x=obj.get_telecom_account_password()
        print x
    
    
    print "hold"


def test_monitor_inform():
    pass
    
    """
    x=obj.wait_next_inform(120)
    print x
    """
    

    x=obj.init_alarm("InternetGatewayDevice.WANDevice.1.WANConnectionDevice.4.WANIPConnection.1.Stats.EthernetPacketsReceived", 3000, 2000)
    print x

    x=obj.start_alarm(x)
    print x

def test():    
    pass 

    #test_monitor_inform()

    test_rpc()
    
    #test_cpe_query_update()
    
    #test_worklist()
    
    print "test end"
    

if __name__ == '__main__':  
    
    sn = "00904C-2013012901"

    
    obj = TR069()
    obj.config_remote_server_addr("172.123.117.13", port=50000)
    obj.switch_cpe(sn)
    
    
    

    test()
        
    obj.switch_cpe(sn)
    
    #test()
    
    
    
    print "\n test end \n"
    

