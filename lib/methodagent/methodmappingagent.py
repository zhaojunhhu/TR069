#coding:utf-8

#user denfine interface
from outputcontrol import ClientResponseHandle
from dataprocess import ConstructResponseData
from constantdefinitions import TR069_SWITCH_CPE_METHOD_NAME

#import log
from constantdefinitions import DEBUG_FLAG
if DEBUG_FLAG:
    from outlog import OutLog as log
else:
    import TR069.lib.common.logs.log  as log


class MethodMappingAgent():
    """
    完成函数功能映射的模块调用
    """

    @staticmethod
    def mapping_method(in_methon_from_module_handle,
                        in_conn,
                        in_sequence_id,
                        in_method_name,
                        in_cpe_id=None,
                        in_method_parameters_list=[]):
        
        #执行method方法
        log.debug_info("Run mapping_method START" )
        
        #检测cpe id是否有效，如果是有效数据则需要预先调用'switch_cpe'接口
        rc_status_flag,\
        rc_result_data=MethodMappingAgent._run_swicth_cpe_method(in_methon_from_module_handle,in_cpe_id)

        #检查请求不是switch_cpe操作，并且上一个步骤，switch_cpe操作成功
        if (TR069_SWITCH_CPE_METHOD_NAME != in_method_name and True == rc_status_flag):
            
            #调用in_method_name对应接口
            rc_status_flag,rc_result_data=MethodMappingAgent._run_method(in_methon_from_module_handle,
                                                                        in_method_name,
                                                                        in_method_parameters_list)
        
        log.debug_info("Run mapping_method END" )
        
        #给客户端回method执行响应
        MethodMappingAgent._send_run_method_response_data_to_client(in_conn,
                                                                    in_sequence_id,
                                                                    rc_status_flag,
                                                                    rc_result_data)
            
            
    @staticmethod
    def _send_run_method_response_data_to_client(in_conn,
                                                 in_sequence_id,
                                                 rc_status_flag,
                                                 in_result_data):
        """
        给客户端回method执行响应
        """
        if rc_status_flag:
            
            #构建返回XML数据 #RUN MENTHOD SUC
            out_data=ConstructResponseData.construct_response_data(in_sequence_id,
                                                                   ClientResponseHandle.RESPONSE_STATUS_SUC,
                                                                   in_result_data)
            
            ClientResponseHandle.send_response_data_to_client(in_conn,out_data)

        else:
            
            #构建返回XML数据 #RUN MENTHOD EXCEPT
            out_data=ConstructResponseData.construct_response_data(in_sequence_id,
                                                                   ClientResponseHandle.RESPONSE_STATUS_FAILE,
                                                                   in_result_data)
            
            ClientResponseHandle.send_response_data_to_client(in_conn,out_data) 

        
    @staticmethod
    def _run_swicth_cpe_method(in_methon_from_module_handle,
                               in_cpe_id):
        """
        检测cpe id是否有效，如果是有效数据则需要预先调用'switch_cpe'接口
        """
        
        if not in_cpe_id:
            return True, None
        
        #调用switch_cpe接口来切换cpe数据
        in_switch_cpe_method_name="switch_cpe"
                        
        in_switch_cpe_parameters_list=[]
        in_switch_cpe_parameters_list.append(in_cpe_id)

        rc_status_flag,rc_result_data=MethodMappingAgent._run_method(in_methon_from_module_handle,
                                                                    in_switch_cpe_method_name,
                                                                    in_switch_cpe_parameters_list)
        
        return rc_status_flag,rc_result_data
           
            
    @staticmethod
    def _run_method(in_methon_from_module_handle,
                   in_method_name,
                   in_method_parameters_list=[]):
        
        if not in_methon_from_module_handle:
            error_info="Input method from module handle is None."
            return False, error_info
        
        if not in_method_name:
            error_info="Input method name is None."
            return False, error_info

        method_name=in_method_name
        tcldataagent_object=in_methon_from_module_handle
    
        attr_isexist_flag=hasattr(tcldataagent_object, method_name)
        log.debug_info(attr_isexist_flag )
        
        if hasattr(tcldataagent_object, method_name):
            
            try:
                log.debug_info("Call method:%s" % method_name )
    
                method_args=in_method_parameters_list
                
                if not method_args:
                    result = getattr(tcldataagent_object, method_name)()
                else:
                    result = getattr(tcldataagent_object, method_name)(*method_args)
    
            except Exception, e:
                error_info="%s" % str(e)
                log.debug_info(error_info)
                return False, error_info
            
            log.debug_info(result)
            return True,result
    
        else:
            
            error_info="Not found insterface."
            log.debug_info(error_info)
            return False, error_info



class TR069UserClientCfg():
    
    @staticmethod
    def create_tr069_user_client_object():
        """
        生成TR069 user client对象
        """

        #[1]
        #加载TR069库
        try:
            from TR069.RF import TR069
            
        except Exception, e:
            try:
                if cmp(e,"No module named TR069.RF"):
                    
                    #加载TR069库
                    TR069UserClientCfg._load_tr069_user_client_lib_path()
                    log.debug_info('Load TR069 user client lib path')
                    
                    from TR069.RF import TR069

            except Exception, e:
                if cmp(e,"No module named TR069.RF"):
                    print "^^^^^^^^^^^^^^^ No module named TR069.RF"
                    return None
                
                error_info="%s" % str(e)
                log.debug_info(error_info)
                return None
         
        #[2]
        #配置TR069库数据编码为UTF-8
        TR069UserClientCfg._set_sys_encoding_type_to_utf8()
        
        #[3]
        #生成TR069对象句柄
        try:
            tr069_user_client=TR069()
            
        except Exception, e:
            error_info="%s" % str(e)
            log.debug_info(error_info)
            return None
        
        return tr069_user_client
        
        
    @staticmethod
    def _load_tr069_user_client_lib_path():
        """
        加载TR069库
        """
        import os
        import sys
    
        g_prj_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        #log.debug_info(g_prj_dir)
        
        sys.path.insert(0, g_prj_dir)


    @staticmethod
    def _set_sys_encoding_type_to_utf8():
        """
        配置TR069库数据编码为UTF-8
        """
        import sys
        
        reload(sys)
        sys.setdefaultencoding('utf-8')
        #log.debug_info(sys.getdefaultencoding())




def test_method_run_tr069_interface():
    """
    测试
    """
    try:
        tr069userclient_object=TR069UserClientCfg.create_tr069_user_client_object()
            
        test_method_name="switch_cpe"
        test_xml_data_list=[]
        test_xml_data_list.append('021018-021018000074')
    
        rc_info=MethodMappingAgent._run_method(tr069userclient_object,
                                               test_method_name,
                                               test_xml_data_list)
        
        
        test_method_name="config_remote_server_addr"
        test_xml_data_list=[]
        test_xml_data_list.append('172.16.28.59')
    
        rc_info=MethodMappingAgent._run_method(tr069userclient_object,
                                               test_method_name,
                                               test_xml_data_list)
        
        
        test_method_name="init_worklist_wlan_add"
        test_xml_data_list=[]

    
        rc_status_flag,rc_result_data=MethodMappingAgent._run_method(tr069userclient_object,
                                               test_method_name,
                                               test_xml_data_list)
        
        log.debug_info("%s: result data=%s" % (test_method_name, rc_result_data))
        
        if not rc_status_flag:
            return
        
    
        
        temp_wl_id=rc_result_data
        
        test_method_name="bind_physic_worklist"
        test_xml_data_list=[]
        test_xml_data_list.append(temp_wl_id)
        test_xml_data_list.append('021018-021018000074')
        
        rc_status_flag,rc_result_data=MethodMappingAgent._run_method(tr069userclient_object,
                                                test_method_name,
                                                test_xml_data_list)
        
        log.debug_info("%s: result data=%s" % (test_method_name, rc_result_data))
        
        if not rc_status_flag:
            return

        test_method_name="execute_worklist"
        test_xml_data_list=[]
        test_xml_data_list.append(temp_wl_id)

        rc_status_flag,rc_result_data=MethodMappingAgent._run_method(tr069userclient_object,
                                                test_method_name,
                                                test_xml_data_list)
        
        log.debug_info("%s: result data=%s" % (test_method_name, rc_result_data))

    except Exception, e:
        error_info="%s" % str(e)
        log.debug_info(error_info)
        return False, error_info




def test_tr069_object_methond():
    #[1]
    try:
        tr069_plugin_client=TR069UserClientCfg.create_tr069_user_client_object()
        #tr069_plugin_client=TR069()
        
        tr069_plugin_client.config_remote_server_addr('172.16.28.59')
        tr069_plugin_client.switch_cpe('021018-021018000074')
        temp_wl_id=tr069_plugin_client.init_worklist_wlan_add()
        tr069_plugin_client.bind_physic_worklist(temp_wl_id,'021018-021018000074')
        tr069_plugin_client.execute_worklist(temp_wl_id)
    
    except Exception, e:
        error_info="%s" % str(e)
        log.debug_info(error_info)
        return False, error_info
            


if __name__ == '__main__':
    #test_tr069_object_methond()
    test_method_run_tr069_interface()
    