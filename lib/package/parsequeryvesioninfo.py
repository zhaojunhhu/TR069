# -*- coding: utf-8 -*-

# /*************************************************************************
#  Copyright (C), 2013-2014, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: parsequeryvesioninfo
#  function: 解析升级服务器返回查询版本相关信息
#  Author: ATT development group
#  version: V1.0
#  date: 2013.10.17
#  change log:
#
#  wangjun  20131017    created
# 
# ***************************************************************************

import threading
import httplib
import copy

import package.messagehandle  as messagehandle

#定义平台两个GUI包名字标签
PACKAGE_ROBOT_GUI_NAME = 'robot_gui'
PACKAGE_REMOTE_LIB_GUI_NAME = 'remote_lib_gui'

# 定义两个total package 的名字标签
ATTROBOT_PAGKAGE_NAME_HEADER='attrobot'
ATTROBOT_REMOTE_PAGKAGE_NAME_HEADER='attrobot_remote'

    
dict_query_info = {}
dict_query_info_lock = threading.Lock()
    
class ParseQueryVesionInfo(object):

    def __init__(self):
        self.query_result_all_version_dict={}


    def set_query_result_version_data(self,query_result_data):
        global dict_query_info
        global dict_query_info_lock
        
        dict_query_info_lock.acquire()
        
        dict_query_info = query_result_data
        self.query_result_all_version_dict=query_result_data

        dict_query_info_lock.release()
        
        
    def get_query_result_version_data(self):
        return copy.deepcopy(self.query_result_all_version_dict)
    
    
    def load_query_result_version_data(self):
        global dict_query_info
        global dict_query_info_lock
        
        dict_query_info_lock.acquire()
        if self.query_result_all_version_dict != dict_query_info:
            self.query_result_all_version_dict = copy.deepcopy(dict_query_info)
            
        dict_query_info_lock.release()
        
        
        
    def _get_version_Legitimacy_Detection(self, in_base_ver, in_check_ver):
        """
        检查在base版本的基础上，框架库是否有运行权限
        in_base_ver: 是当前框架的版本号数据
        in_check_ver： 是当前库依赖的框架版本号数据
        """
        
        #调试版本不支持
        if (in_base_ver.lower().find(".debug") > 0 and in_base_ver.lower().find(".svn") > 0):    
            #返回不支持标示
            return False
        
        #比较base版本类型和当前版本类型
        if not ((in_base_ver.lower().find(".beta") > 0 and  in_base_ver.lower().find(".svn") > 0) ==
           (in_check_ver.lower().find(".beta") > 0 and  in_check_ver.lower().find(".svn") > 0) ):
            
            #返回不支持标示
            return False
        
        #当前框架的版本号数据小于于当前库依赖的框架版本号数据时，表示前框架的版本不支持当前版本的功能。
        if cmp(in_base_ver.lower(), in_check_ver.lower()) < 0:
            
            #返回不支持标示
            return False
        else:
            
            #返回支持标示
            return True
        

    def get_application_total_package_vers(self, in_base_robot_gui_ver):
        """
        获取服务器上全部版本信息，包括ATTROBOT_TOTAL全部版本信息，ATTROBOT_GUI全部版本信息，基于in_base_robot_gui_ver版本的TESTLIB版本信息
        
        存储数据结构说明:
        ====================================================================================
        [ATTROBOT_TOTAL全部版本信息字典，ATTROBOT全部版本信息字典，基于in_base_robot_gui_ver版本的TESTLIB版本信息字典]
        [{"attrobot":['v1.0','v2.0'],}，{"robot_gui":['v1.0','v2.0'],}, {"Capture":['v1.0','v2.0'],}]
        ====================================================================================
        """
        #加载全局的查询变量数据
        self.load_query_result_version_data()
        
        """
        print "\n+++++++++++++++++++++++++++++++++++++++++++++++++++"
        print self.query_result_all_version_dict
        print "\n+++++++++++++++++++++++++++++++++++++++++++++++++++\n\n"
        """
        
        #保存版本信息变量
        out_attrobot_vers_dict={}
        out_robot_gui_vers_dict={}
        out_base_robot_gui_ver_testlib_vers_dict={}
        out_base_robot_gui_ver_testlib_remote_vers_dict={}
        out_testlib_alias_dict={}
        
        if (in_base_robot_gui_ver.lower().find(".debug") > 0
            and  in_base_robot_gui_ver.lower().find(".svn") > 0):    
            messagehandle.log(u"不支持调试框架版本类型向升级服务器查询版本信息。")
            return out_attrobot_vers_dict, \
                out_robot_gui_vers_dict, \
                out_base_robot_gui_ver_testlib_vers_dict, \
                out_base_robot_gui_ver_testlib_remote_vers_dict, \
                out_testlib_alias_dict

        if not self.query_result_all_version_dict:
            messagehandle.log(u"请先向服务器查询升级相关信息")
            return {}, {}, {}, {}
        
        #复制数据源
        in_testlib_data_dict = copy.deepcopy(self.query_result_all_version_dict)
        
        #数据格式:['v1.1.0','v1.2.0',]
        temp_testlib_node_ver_list = []
        temp_testlib_remote_node_ver_list = []
        
        #{"Capture"：{"v1.1.0":[("TESTLIB_VERSION":"v1.1.0"},{"TESTLIB_VERSION":"v1.1.5"),]}}
        #{"库名"：{"gui版本1":[{"库版本KEY值"："库版本1"}, {"库版本KEY值"："库版本2"}, ]，}}
        for testlib_node in in_testlib_data_dict:
            
            messagehandle.log(u"\n库名：%s" % testlib_node)
            _testlib_alias=""
            
            testlib_base_gui_vers_dict = in_testlib_data_dict.get(testlib_node)
            for testlib_base_gui_ver_node in testlib_base_gui_vers_dict:
                
                #对平台版本的处理
                #对gui版本的处理
                if ( -1 != testlib_node.find(ATTROBOT_PAGKAGE_NAME_HEADER) or
                    -1 != testlib_node.find(ATTROBOT_REMOTE_PAGKAGE_NAME_HEADER) or
                    -1 != testlib_node.find(PACKAGE_ROBOT_GUI_NAME) or
                    -1 != testlib_node.find(PACKAGE_REMOTE_LIB_GUI_NAME) ):
                    
                    messagehandle.log(u"基于ATTROBOT版本号：%s" % testlib_base_gui_ver_node )
                    
                    testlib_base_gui_ver_node_list = testlib_base_gui_vers_dict.get(testlib_base_gui_ver_node)
                    for testlib_version_node in testlib_base_gui_ver_node_list:
                        
                        #将版本信息保存到临时列表中
                        _testlib_ver_value = testlib_version_node.get(messagehandle.Event.TESTLIB_VERSION)

                        #调试版本不支持
                        if (testlib_base_gui_ver_node.lower().find(".debug") > 0 and testlib_base_gui_ver_node.lower().find(".svn") > 0):    
                            continue
                        
                        #比较当前框架版本类型和当前库依赖框架版本版本类型是否为同一类型
                        if not ((in_base_robot_gui_ver.lower().find(".beta") > 0 and  in_base_robot_gui_ver.lower().find(".svn") > 0) ==
                           (testlib_base_gui_ver_node.lower().find(".beta") > 0 and  testlib_base_gui_ver_node.lower().find(".svn") > 0) ):
                            continue
                        
                        messagehandle.log(u"库版本号：%s" % _testlib_ver_value)
                            
                        temp_testlib_node_ver_list.append(_testlib_ver_value)
                    
                        #添加基础测试库别名数据获取 #add by wangjun 20130813 
                        _testlib_alias = testlib_version_node.get(messagehandle.Event.TESTLIB_ALIAS)
                            
                #对基础测试库进行处理
                else:
                    
                    #返回True标示默认gui版本满足加载测试库要求
                    if self._get_version_Legitimacy_Detection(in_base_robot_gui_ver, testlib_base_gui_ver_node):
                        
                        messagehandle.log(u"基于ATTROBOT版本号：%s" % testlib_base_gui_ver_node )
                        
                        testlib_base_gui_ver_node_list = testlib_base_gui_vers_dict.get(testlib_base_gui_ver_node)
                        for testlib_version_node in testlib_base_gui_ver_node_list:
                    
                            #将版本信息保存到列表
                            _testlib_ver_value = testlib_version_node.get(messagehandle.Event.TESTLIB_VERSION)
                            messagehandle.log(u"库版本号：%s" % _testlib_ver_value)
                            
                            temp_testlib_node_ver_list.append(_testlib_ver_value)
                                                        
                            #add by wangjun 20130705
                            _testlib_remote_flag = testlib_version_node.get(messagehandle.Event.TESTLIB_REMOTE_FLAG)
                            if _testlib_remote_flag:
                                #add to remote list
                                temp_testlib_remote_node_ver_list.append(_testlib_ver_value)
                            
                            #添加基础测试库别名数据获取 #add by wangjun 20130813 
                            _testlib_alias = testlib_version_node.get(messagehandle.Event.TESTLIB_ALIAS)
                            
            
            #将基础测试库别名数据保存到字典中 #add by wangjun 20130813
            if _testlib_alias:
                out_testlib_alias_dict[testlib_node]=_testlib_alias
                    
            #将库的版本信息保存到字典中
            #数据项格式：{'库名':['v1.0','v2.0']}
            if temp_testlib_node_ver_list:

                if ( -1 != testlib_node.find(ATTROBOT_PAGKAGE_NAME_HEADER) or
                    -1 != testlib_node.find(ATTROBOT_REMOTE_PAGKAGE_NAME_HEADER)):
                    
                    #对平台版本的处理
                    out_attrobot_vers_dict[testlib_node] = temp_testlib_node_ver_list
                    temp_testlib_node_ver_list = []
                    
                elif ( -1 != testlib_node.find(PACKAGE_ROBOT_GUI_NAME) or
                    -1 != testlib_node.find(PACKAGE_REMOTE_LIB_GUI_NAME)):
                    
                    #对gui版本的处理
                    out_robot_gui_vers_dict[testlib_node] = temp_testlib_node_ver_list
                    temp_testlib_node_ver_list = []
                    
                else:
                    #对基础测试库进行处理
                    out_base_robot_gui_ver_testlib_vers_dict[testlib_node] = temp_testlib_node_ver_list
                    temp_testlib_node_ver_list = []
                    
                    #add by wangjun 20130705
                    if temp_testlib_remote_node_ver_list:#.append(_testlib_ver_value)
                        out_base_robot_gui_ver_testlib_remote_vers_dict[testlib_node] = temp_testlib_remote_node_ver_list
                        temp_testlib_remote_node_ver_list=[]
            
         
        messagehandle.log(u"-------------------------------------------\n")
        messagehandle.log(u"获取ATTROBOT_TOTAL全部版本信息:\n%s\n" % out_attrobot_vers_dict)
        messagehandle.log(u"获取ATTROBOT全部版本信息:\n%s\n" % out_robot_gui_vers_dict)
        messagehandle.log(u"基于%s版本的TESTLIB版本信息:\n%s\n" % (in_base_robot_gui_ver, out_base_robot_gui_ver_testlib_vers_dict) )
        messagehandle.log(u"基于%s版本的远程TESTLIB版本信息:\n%s\n" % (in_base_robot_gui_ver, out_base_robot_gui_ver_testlib_remote_vers_dict) )
        messagehandle.log(u"基础库别名信息:\n%s\n" % (out_testlib_alias_dict))
        messagehandle.log(u"-------------------------------------------\n")
        
        
        return out_attrobot_vers_dict, \
        out_robot_gui_vers_dict, \
        out_base_robot_gui_ver_testlib_vers_dict, \
        out_base_robot_gui_ver_testlib_remote_vers_dict, \
        out_testlib_alias_dict
    
    
    
    def get_base_robot_gui_version_testlib_package_vers(self, in_base_robot_gui_ver):
        """
        获取服务器上基于in_base_robot_gui_ver版本的TESTLIB版本信息
        
        存储数据结构说明:
        ====================================================================================
        [基于in_base_robot_gui_ver版本的TESTLIB版本信息字典]
        [{"Capture":['v1.0','v2.0'],}]
        ====================================================================================
        """
        #加载全局的查询变量数据
        self.load_query_result_version_data()

        #保存版本信息变量
        out_base_robot_gui_ver_testlib_vers_dict = {}
        out_base_robot_gui_ver_testlib_remote_vers_dict = {}

        if (in_base_robot_gui_ver.lower().find(".debug") > 0
            and  in_base_robot_gui_ver.lower().find(".svn") > 0):    
            messagehandle.log(u"不支持调试框架版本类型向升级服务器查询版本信息。")
            return out_base_robot_gui_ver_testlib_vers_dict, \
                out_base_robot_gui_ver_testlib_remote_vers_dict
            
            
        if not self.query_result_all_version_dict:
            messagehandle.log(u"请先向服务器查询升级相关信息")
            return {}, {}
        
        #复制数据源
        in_testlib_data_dict = copy.deepcopy(self.query_result_all_version_dict)
        
        #数据格式:['v1.1.0','v1.2.0',]
        temp_testlib_node_ver_list = []
        temp_testlib_remote_node_ver_list = []
        
        #{"Capture"：{"v1.1.0":[("TESTLIB_VERSION":"v1.1.0"},{"TESTLIB_VERSION":"v1.1.5"),]}}
        #{"库名"：{"gui版本1":[{"库版本KEY值"："库版本1"}, {"库版本KEY值"："库版本2"}, ]，}}
        for testlib_node in in_testlib_data_dict:
            
            messagehandle.log(u"\n库名：%s" % testlib_node)
            
            testlib_base_gui_vers_dict = in_testlib_data_dict.get(testlib_node)
            for testlib_base_gui_ver_node in testlib_base_gui_vers_dict:
                
                #拦截对平台版本的处理
                #拦截对gui版本的处理
                if ( -1 != testlib_node.find(ATTROBOT_PAGKAGE_NAME_HEADER) or
                    -1 != testlib_node.find(ATTROBOT_REMOTE_PAGKAGE_NAME_HEADER) or
                    -1 != testlib_node.find(PACKAGE_ROBOT_GUI_NAME) or
                    -1 != testlib_node.find(PACKAGE_REMOTE_LIB_GUI_NAME) ):
                    continue
                    
                #对基础测试库进行处理
                else:
                    
                    #返回True标示默认gui版本满足加载测试库要求
                    if self._get_version_Legitimacy_Detection(in_base_robot_gui_ver, testlib_base_gui_ver_node):
                        
                        messagehandle.log(u"基于ATTROBOT版本号：%s" % testlib_base_gui_ver_node )
                        
                        testlib_base_gui_ver_node_list = testlib_base_gui_vers_dict.get(testlib_base_gui_ver_node)
                        for testlib_version_node in testlib_base_gui_ver_node_list:
                            
                            #将版本信息保存到列表
                            _testlib_ver_value=testlib_version_node.get(messagehandle.Event.TESTLIB_VERSION)
                            messagehandle.log(u"库版本号：%s" % _testlib_ver_value)
                            
                            temp_testlib_node_ver_list.append(_testlib_ver_value)
                            
                            _testlib_remote_flag = testlib_version_node.get(messagehandle.Event.TESTLIB_REMOTE_FLAG)
                            if _testlib_remote_flag:
                                #add to remote list
                                temp_testlib_remote_node_ver_list.append(_testlib_ver_value)
                            
                            
            #将库的版本信息保存到字典中
            #数据项格式：{'库名':['v1.0','v2.0']}
            if temp_testlib_node_ver_list:
                
                #对基础测试库进行处理
                out_base_robot_gui_ver_testlib_vers_dict[testlib_node] = temp_testlib_node_ver_list
                temp_testlib_node_ver_list=[]

                if temp_testlib_remote_node_ver_list:
                    out_base_robot_gui_ver_testlib_remote_vers_dict[testlib_node]=temp_testlib_remote_node_ver_list
                    temp_testlib_remote_node_ver_list=[]
         
        messagehandle.log(u"-------------------------------------------\n")
        messagehandle.log(u"基于%s版本的TESTLIB版本信息:\n%s\n" % (in_base_robot_gui_ver, out_base_robot_gui_ver_testlib_vers_dict) )
        messagehandle.log(u"基于%s版本的远程TESTLIB版本信息:\n%s\n" % (in_base_robot_gui_ver, out_base_robot_gui_ver_testlib_remote_vers_dict) )
        messagehandle.log(u"-------------------------------------------\n")
        
        return out_base_robot_gui_ver_testlib_vers_dict, out_base_robot_gui_ver_testlib_remote_vers_dict


    def get_auto_selected_testlib_latest_packages(self, in_base_robot_gui_ver):
        """
        获取服务器上基于in_base_robot_gui_ver版本的TESTLIB最新版本信息 组成所有测试库最新版本数据集合
        
        存储数据结构说明:
        ====================================================================================
        [基于robot_gui最新版本的TESTLIB最新版本信息字典]
        [{"testcenter":'v2.0',"Capture":'v2.0'}, [{"ftpclient":'v2.0',"Capture":'v2.0'}]]
        ====================================================================================
        """
        #加载全局的查询变量数据
        self.load_query_result_version_data()
        
        #保存版本信息变量
        out_base_robot_gui_ver_testlib_vers_dict = {}
        out_base_robot_gui_ver_remote_testlib_vers_dict = {}
        
        if (in_base_robot_gui_ver.lower().find(".debug") > 0
            and  in_base_robot_gui_ver.lower().find(".svn") > 0):    
            messagehandle.log(u"不支持调试框架版本类型向升级服务器查询版本信息。")
            return out_base_robot_gui_ver_testlib_vers_dict, \
                out_base_robot_gui_ver_remote_testlib_vers_dict
            
        if not self.query_result_all_version_dict:
            messagehandle.log(u"请先向服务器查询升级相关信息")
            return {}, {}
        
        #复制数据源
        in_testlib_data_dict = copy.deepcopy(self.query_result_all_version_dict)
        
        #{"Capture"：{"v1.1.0":[("TESTLIB_VERSION":"v1.1.0"},{"TESTLIB_VERSION":"v1.1.5"),]}}
        #{"库名"：{"gui版本1":[{"库版本KEY值"："库版本1"}, {"库版本KEY值"："库版本2"}, ]，}}
        for testlib_node in in_testlib_data_dict:
            
            messagehandle.log(u"\n库名：%s" % testlib_node)
            temp_latest_testlib_ver = None
            temp_remote_latest_testlib_ver = None
            
            testlib_base_gui_vers_dict = in_testlib_data_dict.get(testlib_node)
            for testlib_base_gui_ver_node in testlib_base_gui_vers_dict:
                
                #拦截对平台版本的处理
                #拦截对gui版本的处理
                if ( -1 != testlib_node.find(ATTROBOT_PAGKAGE_NAME_HEADER) or
                    -1 != testlib_node.find(ATTROBOT_REMOTE_PAGKAGE_NAME_HEADER) or
                    -1 != testlib_node.find(PACKAGE_ROBOT_GUI_NAME) or
                    -1 != testlib_node.find(PACKAGE_REMOTE_LIB_GUI_NAME) ):
                    continue

                #对基础测试库进行处理
                else:
                    
                    #返回True标示默认gui版本满足加载测试库要求
                    if self._get_version_Legitimacy_Detection(in_base_robot_gui_ver, testlib_base_gui_ver_node):
                        
                        messagehandle.log(u"基于ATTROBOT版本号：%s" % testlib_base_gui_ver_node )
        
                        testlib_base_gui_ver_node_list = testlib_base_gui_vers_dict.get(testlib_base_gui_ver_node)
                        for testlib_version_node in testlib_base_gui_ver_node_list:
         
                            #将版本信息保存到列表
                            _testlib_ver_value = testlib_version_node.get(messagehandle.Event.TESTLIB_VERSION)
                            messagehandle.log(u"库版本号：%s" % _testlib_ver_value)
                            
                            #保存最新gui版本号
                            if not temp_latest_testlib_ver:
                                temp_latest_testlib_ver = _testlib_ver_value
                            else:
                                #返回True标示默认gui版本满足加载测试库要求
                                if self._get_version_Legitimacy_Detection(_testlib_ver_value, temp_latest_testlib_ver):
                                    temp_latest_testlib_ver = _testlib_ver_value
                                    
                            #add by wangjun 20130705
                            #获取库是否支持远端接口
                            _testlib_remote_flag = testlib_version_node.get(messagehandle.Event.TESTLIB_REMOTE_FLAG)
                            if _testlib_remote_flag:
                                #保存远端库最新gui版本号
                                if not temp_remote_latest_testlib_ver:
                                    temp_remote_latest_testlib_ver = _testlib_ver_value
                                    
                                else:
                                    #返回True标示默认gui版本满足加载测试库要求
                                    if self._get_version_Legitimacy_Detection(_testlib_ver_value, temp_remote_latest_testlib_ver):
                                        temp_remote_latest_testlib_ver = _testlib_ver_value
                                    
                                    
                #将库的版本信息保存到字典中
                #数据项格式：{'库名':['v1.0','v2.0']}
                if temp_latest_testlib_ver:
                    #对基础测试库进行处理
                    out_base_robot_gui_ver_testlib_vers_dict[testlib_node] = temp_latest_testlib_ver
                    temp_latest_testlib_ver = None

                #add by wangjun 20130705
                #将库的版本信息保存到远程库数据字典中
                if temp_remote_latest_testlib_ver:
                    #对基础测试库进行处理
                    out_base_robot_gui_ver_remote_testlib_vers_dict[testlib_node] = temp_remote_latest_testlib_ver
                    temp_remote_latest_testlib_ver = None
                    
         
        messagehandle.log(u"-------------------------------------------\n")
        messagehandle.log(u"基于%s版本的TESTLIB最新版本信息:\n%s\n" % (in_base_robot_gui_ver, out_base_robot_gui_ver_testlib_vers_dict) )
        messagehandle.log(u"基于%s版本的远端TESTLIB最新版本信息:\n%s\n" % (in_base_robot_gui_ver, out_base_robot_gui_ver_remote_testlib_vers_dict) )
        
        messagehandle.log(u"-------------------------------------------\n")
        
        return out_base_robot_gui_ver_testlib_vers_dict, out_base_robot_gui_ver_remote_testlib_vers_dict


#-------------------------------------------------------------------------------------


if __name__ == '__main__':

    test_data2={
        'Capture':\
            {'v1.3.0': [{'TESTLIB_REMOTE_FLAG': True, 'TESTLIB_ALIAS': None, 'TESTLIB_VERSION': 'v1.0.0'}],\
            'v.beta131016.svn1600': [{'TESTLIB_REMOTE_FLAG': True, 'TESTLIB_ALIAS': None, 'TESTLIB_VERSION': 'v.beta131016.svn1680'}]},\
        'remote_lib_gui': \
                {'v1.3.3r': [{'TESTLIB_REMOTE_FLAG': False, 'TESTLIB_ALIAS': None, 'TESTLIB_VERSION': 'v1.3.3r'}], \
                'v1.3.2r': [{'TESTLIB_REMOTE_FLAG': False, 'TESTLIB_ALIAS': None, 'TESTLIB_VERSION': 'v1.3.2r'}], \
                'v1.3.6': [{'TESTLIB_REMOTE_FLAG': False, 'TESTLIB_ALIAS': None, 'TESTLIB_VERSION': 'v1.3.6'}], \
                'v1.3.4r': [{'TESTLIB_REMOTE_FLAG': False, 'TESTLIB_ALIAS': None, 'TESTLIB_VERSION': 'v1.3.4r'}], \
                'v1.3.5': [{'TESTLIB_REMOTE_FLAG': False, 'TESTLIB_ALIAS': None, 'TESTLIB_VERSION': 'v1.3.5'}],
                'v.beta131016.svn1600': [{'TESTLIB_REMOTE_FLAG': True, 'TESTLIB_ALIAS': None, 'TESTLIB_VERSION': 'v.beta131016.svn1600'}]}
        }
    
    
    #解析相关版本信息
    query_obj=ParseQueryVesionInfo()
    query_obj.set_query_result_version_data(test_data2)
    
    #保存需要下载的文件列表
    query_obj.get_application_total_package_vers("v.beta131016.svn1600")
    query_obj.get_base_robot_gui_version_testlib_package_vers("v.beta131016.svn1600")
    query_obj.get_auto_selected_testlib_latest_packages("v.beta131016.svn1600")

    nExit = raw_input("Press any key to end...")
#-------------------------------------------------------------------------------------