#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: xmlparsecontrol
#  function: XMLParseControl
#            
#  Author: ATT development group
#  version: V1.0
#  date: 2013.8.29
#  change log:
#  wangjun  20130829    create
# ***************************************************************************

from xml.etree import ElementTree
from xml.etree.ElementTree import Element
import base64

#user denfine interface
from constantdefinitions import XML_VALUE_DECODE_FALG, OPEN_XML_PROCESS_LOG

#import log
from constantdefinitions import DEBUG_FLAG
if DEBUG_FLAG:
    from outlog import OutLog as log
else:
    import TR069.lib.common.logs.log  as log
    
    

#定义解析XML数据节点
ROOT_NODE_MESSAGE_ID='messageid'
ROOT_NODE_FUNCTION='function'
ROOT_NODE_CPE_ID='cpe'
ROOT_NODE_PARAMETERS='parameters'

CHILD_NODE_PARAMETER='parameter'
CHILD_NODE_VALUE='value'
CHILD_NODE_ITEM='item'
CHILD_NODE_KEY='key'

NODE_ATTRIBUTE_NAME='name'
NODE_ATTRIBUTE_DATA_TYPE='type'

NODE_PARAMETER_DATA_BASICTYPE='basictype'
NODE_PARAMETER_DATA_LIST='list'
NODE_PARAMETER_DATA_DICT='dict'



def parse_process_log(in_value_string):
    if OPEN_XML_PROCESS_LOG:
        log.debug_info(in_value_string)
        
        
class XMLParseControl():
    
    @staticmethod
    def parse_xml_stream_data(in_stream_data):

        out_message_id=None
        out_methond_name=None
        out_cpe_id=None
        out_parameters_list=[]
        
        #取得元素的根节点
        root = ElementTree.fromstring(in_stream_data) 
          
        #获取消息id
        eitor = root.find(ROOT_NODE_MESSAGE_ID)
        if None == eitor:
            return False, []
        
        out_message_id=XMLParseControl.node_value_text_format('string',eitor.text)
        parse_process_log("%s:%s" % (ROOT_NODE_MESSAGE_ID,out_message_id))
        #parse_process_log("=====================================\n")
        
        
        #获取method名字
        eitor = root.find(ROOT_NODE_FUNCTION)
        if None == eitor:
            return False, []
        
        out_methond_name=XMLParseControl.node_value_text_format('string',eitor.text)
        parse_process_log("%s:%s" % (ROOT_NODE_FUNCTION,out_methond_name))
        #parse_process_log("=====================================\n\n")

        #获取cpe id
        eitor = root.find(ROOT_NODE_CPE_ID)
        if None == eitor:
            return False, []
        
        out_cpe_id=XMLParseControl.node_value_text_format('string',eitor.text)
        parse_process_log("%s:%s" % (ROOT_NODE_CPE_ID,out_cpe_id))
        #parse_process_log("=====================================\n\n")

        
        #获取parameters列表
        eitor = root.find(ROOT_NODE_PARAMETERS)
        if None != eitor:
      
            #获取parameter数据项
            for parameter_node in eitor.findall(CHILD_NODE_PARAMETER):

                #获取parameter的属性数据
                attrib_dict=parameter_node.attrib
                if attrib_dict:
                    
                    #获取parameter数据项的名称和类型
                    parameter_name=attrib_dict.get(NODE_ATTRIBUTE_NAME)
                    parameter_type=attrib_dict.get(NODE_ATTRIBUTE_DATA_TYPE)
                    #parse_process_log("parameter name=%s, parameter type=%s" % (parameter_name, parameter_type))
                    
                    if parameter_type==NODE_PARAMETER_DATA_BASICTYPE:

                        #解析basictype类型的数据节点
                        rc_item_vlue=XMLParseControl.parse_parameter_type_is_basetype_element(parameter_type,parameter_node)
                        out_parameters_list.append(rc_item_vlue)
                        
                        parse_process_log("parameter name=%s, parameter type=%s, parameter value=%s" % \
                                       (parameter_name, parameter_type, rc_item_vlue))
                        
                    elif parameter_type==NODE_PARAMETER_DATA_LIST:
                    
                        #解析list类型的数据节点
                        rc_item_vlue=XMLParseControl.parse_parameter_type_is_list_element(parameter_type,parameter_node)
                        out_parameters_list.append(rc_item_vlue)
                        
                        parse_process_log("parameter name=%s, parameter type=%s, parameter value=%s" % \
                                       (parameter_name, parameter_type, rc_item_vlue))
                        
                    elif parameter_type==NODE_PARAMETER_DATA_DICT:

                        #解析dict类型的数据节点
                        rc_item_vlue=XMLParseControl.parse_parameter_type_is_dict_element(parameter_type,parameter_node)
                        out_parameters_list.append(rc_item_vlue)
                        
                        parse_process_log("parameter name=%s, parameter type=%s, parameter value=%s" % \
                                       (parameter_name, parameter_type, rc_item_vlue))
                        
                    else:
                        pass

                    #parse_process_log("-------------------------------------")
        
        #打印全部的参数数据  
        parse_process_log("\nparameters value=%s" % out_parameters_list)
        #parse_process_log("=====================================")

        #打印接口全部的数据
        out_parse_xml_stream_data_list=[out_message_id,out_methond_name,out_cpe_id,out_parameters_list]
        parse_process_log("\nparse request total value=%s" % out_parse_xml_stream_data_list)
        #parse_process_log("=====================================")
        
        return True,out_parse_xml_stream_data_list
    
    
    @staticmethod
    def parse_parameter_type_is_basetype_element(in_parameter_type,in_parameter_node):

        out_item_value=None
        if in_parameter_type==NODE_PARAMETER_DATA_BASICTYPE:

            for parameter_item_node in in_parameter_node.findall(CHILD_NODE_VALUE):
                
                #item_value=parameter_item_node.text
                itme_attrib_dict=parameter_item_node.attrib
                item_value_type=itme_attrib_dict.get(NODE_ATTRIBUTE_DATA_TYPE)
                
                #基础数据类型int,sting,bool数据格式转换
                item_value=XMLParseControl.node_value_text_format(item_value_type, parameter_item_node.text)
                
                #parse_process_log("item value=%s, item value type=%s" % (item_value, item_value_type))
                
                #保存基础数据类型int,bool,string的值
                out_item_value=item_value
                break
            
        #parse_process_log("-------------------------:%s" % out_item_value)
        
        #返回单个数据项的值
        return out_item_value
    
    
    @staticmethod
    def parse_parameter_type_is_list_element(in_parameter_type,in_parameter_node):

        out_item_value_list=[]
        if in_parameter_type==NODE_PARAMETER_DATA_LIST:
            
            #遍历value节点
            for parameter_item_node in in_parameter_node.findall(CHILD_NODE_VALUE):
                
                item_value=parameter_item_node.text
                itme_attrib_dict=parameter_item_node.attrib
                item_value_type=itme_attrib_dict.get(NODE_ATTRIBUTE_DATA_TYPE)

                #parse_process_log("item value=%s, item value type=%s" % (item_value, item_value_type))

                if item_value_type==NODE_PARAMETER_DATA_LIST:

                    #递归解析list类型的数据节点
                    rc_item_vlue=XMLParseControl.parse_parameter_type_is_list_element(item_value_type,parameter_item_node)
                    out_item_value_list.append(rc_item_vlue)
                    
                elif item_value_type==NODE_PARAMETER_DATA_DICT:

                    #递归解析dict类型的数据节点
                    rc_item_vlue=XMLParseControl.parse_parameter_type_is_dict_element(item_value_type,parameter_item_node)
                    out_item_value_list.append(rc_item_vlue)

                else:
                    #基础数据类型int,sting,bool数据格式转换
                    out_item_vlue=XMLParseControl.node_value_text_format(item_value_type, parameter_item_node.text)

                    #保存基础数据类型int,bool,string的值
                    out_item_value_list.append(out_item_vlue)
                
        return out_item_value_list
        
        
    @staticmethod
    def parse_parameter_type_is_dict_element(in_parameter_type,in_parameter_node):
        
        out_item_value_dict={}
        
        if in_parameter_type==NODE_PARAMETER_DATA_DICT:
            
            #遍历item节点
            for parameter_dict_item_node in in_parameter_node.findall(CHILD_NODE_ITEM):

                #获取item的key,value节点数据
                #for dict_item_node in parameter_dict_item_node.findall(CHILD_NODE_ITEM):
                    
                    dict_item_key_node=parameter_dict_item_node.find(CHILD_NODE_KEY)
                    if None == dict_item_key_node:
                        parse_process_log("Not find dict tag key.")
                        continue
                    
                    dict_item_value_node=parameter_dict_item_node.find(CHILD_NODE_VALUE)
                    if None == dict_item_value_node:
                        parse_process_log("Not find dict tag value.")
                        continue
                    
                    dict_item_key_value=dict_item_key_node.text
                    dict_item_value_value=dict_item_value_node.text
                    dict_item_value_value_attrib_dict=dict_item_value_node.attrib
                    dict_item_value_value_type=dict_item_value_value_attrib_dict.get(NODE_ATTRIBUTE_DATA_TYPE)
                    
                    #parse_process_log("item key=%s, item value=%s, item value type=%s" % (dict_item_key_value,dict_item_value_value,dict_item_value_value_type) )

                    out_item_value_dict[dict_item_key_value]=None
                    
                    if dict_item_value_value_type ==NODE_PARAMETER_DATA_LIST:

                        #递归解析list类型的数据节点
                        rc_item_vlue=XMLParseControl.parse_parameter_type_is_list_element(dict_item_value_value_type,dict_item_value_node)
                        out_item_value_dict[dict_item_key_value]=rc_item_vlue
                        
                    elif dict_item_value_value_type ==NODE_PARAMETER_DATA_DICT:
                        
                        #递归解析dict类型的数据节点
                        rc_item_vlue=XMLParseControl.parse_parameter_type_is_dict_element(dict_item_value_value_type,dict_item_value_node)
                        out_item_value_dict[dict_item_key_value]=rc_item_vlue
                    
                    else:
                        #基础数据类型int,sting,bool数据格式转换
                        dict_item_value_value=XMLParseControl.node_value_text_format(dict_item_value_value_type, dict_item_value_node.text)
                        
                        #保存基础数据类型int,bool,string的值
                        out_item_value_dict[dict_item_key_value]=dict_item_value_value
                        
        return out_item_value_dict


    @staticmethod
    def node_value_text_format(in_item_value_type,in_item_value):
        """
        解码参数数据并将数据类型转换为xml文件中定义的类型
        """
        out_value=None
        if 'string' == in_item_value_type:
            out_value=''
            
        if not in_item_value:
            return out_value
        
        decode_value=XMLParseControl.node_value_b64decode(in_item_value)
        print "^^^^^^^^^^^^^^^^^^^^^^tpye:%s data:%s" % (in_item_value_type,decode_value)
        
        if ('False'==decode_value ):
                out_value=bool(False)
                
        elif('True' == decode_value):
                out_value=bool(True)
                
        elif 'string'==in_item_value_type:
            out_value=decode_value
                
        elif 'int' == in_item_value_type:
            out_value=int(decode_value)
            
        elif 'float' == in_item_value_type:
            out_value=float(decode_value)
                
        elif 'long' == in_item_value_type:
            out_value=long(decode_value)
            
        else:
            out_value=decode_value
                
        return out_value
        
        
    @staticmethod
    def node_value_b64decode(in_value_node_data):
        """
        对数据进行64位解码码,只针对<value/>和<key/> text值
        """
        if XML_VALUE_DECODE_FALG:
            if isinstance(in_value_node_data, str):
                return base64.b64decode(in_value_node_data)
            
            else:
                return in_value_node_data
        else:
            return in_value_node_data
    
    



#测试 
def test():

    xml_stream_string="""<?xml version='1.0' encoding='UTF-8'?>
    <root>
    <messageid>0123456</messageid>
    <function>test_method</function>
    <cpe>021018-021018000074</cpe>
    <parameters>
        <parameter name="install_op_struct" type="list">
        </parameter>
        <parameter name="update_op_struct" type="list">
        </parameter>
        <parameter name="uninstall_op_struct" type="list">
        </parameter>
        <parameter name="command_key" type="basictype">
            <value type="string">123</value>
        </parameter>  
    </parameters>
    </root>
    """
    
    test_str_1="""<root>
    <messageid>MTM3NzY3NzExNS0wMDE5QzYtMDEwMDAwMDAwMDAxMDExMDAwMDAxOUM2OUU3QkI3</messageid>
    <cpe>MDAxOUM2LTAxMDAwMDAwMDAwMTAxMTAwMDAwMTlDNjlFN0JCNw==</cpe>
    <function>ZG93bmxvYWQ=</function>
    <parameters><parameter name="file_type" type="basictype"><value type="string">ZmlsZXR5cGU=</value></parameter><parameter name="url" type="basictype"><value type="string">dXJs</value></parameter><parameter name="user_name" type="basictype"><value type="string"></value></parameter><parameter name="password" type="basictype"><value type="string"></value></parameter><parameter name="file_size" type="basictype"><value type="int">MTAw</value></parameter><parameter name="target_file_name" type="basictype"><value type="string"></value></parameter><parameter name="delay_seconds" type="basictype"><value type="int">MA==</value></parameter><parameter name="success_url" type="basictype"><value type="string"></value></parameter><parameter name="failure_url" type="basictype"><value type="string"></value></parameter><parameter name="command_key" type="basictype"><value type="string"></value></parameter></parameters></root>"""
     
    try:
        rc_flag,rc_data_list=XMLParseControl.parse_xml_stream_data(test_str_1)
        parse_process_log('\n\n%s' % rc_data_list )
        
    except Exception, e:
        parse_process_log('\n\nXMLParseControl parse_xml_stream_data error: %s' % e )
        


if __name__ == '__main__':
    test()