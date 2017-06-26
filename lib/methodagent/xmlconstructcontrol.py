#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: xmlconstructcontrol
#  function: XMLConstructControl
#            
#  Author: ATT development group
#  version: V1.0
#  date: 2013.8.29
#  change log:
#  wangjun  20130829    create
#  wangjun  20130830    对数据源添加对datetime.datetime数据类型支持
#  wangjun  20130902    对数据源添加对unicode数据类型支持
#                       对数据源添加对tuple数据类型的支持
# ***************************************************************************

from xml.etree import ElementTree
from xml.etree.ElementTree import Element
import base64
import datetime

#user denfine interface
from constantdefinitions import XML_VALUE_DECODE_FALG, OPEN_XML_PROCESS_LOG

#import log
from constantdefinitions import DEBUG_FLAG
if DEBUG_FLAG:
    from outlog import OutLog as log
else:
    import TR069.lib.common.logs.log  as log
    
    
#定义构造XML数据节点
ROOT_NODE='root'
ROOT_NODE_MESSAGE_ID='messageid'
ROOT_NODE_STATUS='status'
ROOT_NODE_RESULTS='results'
CHILD_NODE_RESULT='value'#'result'
CHILD_NODE_VALUE='value'

NODE_ATTRIBUTE_DATA_TYPE='type'

NODE_PARAMETER_DATA_BASICTYPE='basictype'
NODE_PARAMETER_DATA_LIST='list'
NODE_PARAMETER_DATA_DICT='dict'



def parse_process_log(in_value_string):
    if OPEN_XML_PROCESS_LOG:
        log.debug_info( in_value_string)


class XMLConstructControl():

    @staticmethod
    def construct_xml_stream_data(in_message_id,in_status,in_response_data):
        """
        构造XML数据流
        """
        #设置编码格式
        import sys
        def_encode=sys.getdefaultencoding()
        if 'utf8' != def_encode:
            reload(sys)
            sys.setdefaultencoding('utf8')
        
        parse_process_log(sys.getdefaultencoding())
        
        out_stream_data_string=None
        
        #将返回值数据类型从元组转换为列表
        if isinstance(in_response_data, tuple):
            in_response_data=list(in_response_data)
        
        #设置根节点
        root = Element(ROOT_NODE)
        tree = ElementTree.ElementTree(root)
            
        #设置message_id节点
        node_message_id = Element(ROOT_NODE_MESSAGE_ID)
        node_message_id.text=XMLConstructControl.node_value_b64encode(str(in_message_id))
        root.append(node_message_id)
            
        #设置status节点
        node_status = Element(ROOT_NODE_STATUS)
        node_status.text=XMLConstructControl.node_value_b64encode(str(in_status))
        root.append(node_status)
    
        #设置results节点
        node_results = Element(ROOT_NODE_RESULTS)
        root.append(node_results)
        
        #保存XML基本节点数据流
        out_stream_data_string=ElementTree.tostring(root,'UTF-8',method='xml')

        try:
                    
            if in_response_data:
        
                #构造results节点的内容
                XMLConstructControl.construct_results_node(node_results,in_response_data)
                
            else:
                pass
            
        except Exception, e:
            error_info="Construct result data occurs expection:%s" % e
            parse_process_log('\n\n%s' % error_info)

            #构造results错误节点数据内容
            node_status.text=XMLConstructControl.node_value_b64encode(str(-1))
            root.remove(node_results)
            node_results = Element(ROOT_NODE_RESULTS)
            root.append(node_results)
            XMLConstructControl.construct_error_responde_node(node_results,error_inf)
        
        #保存XML基本节点数据流
        out_stream_data_string=ElementTree.tostring(root,'UTF-8',method='xml')
            
        #打印构造数据结果
        parse_process_log("out_stream_data_string:%s" % out_stream_data_string)
            
        return out_stream_data_string
             
             
    @staticmethod
    def construct_error_responde_node(in_results_element,error_info):
        """
        构造解析参数输入到XML流中异常
        """
        #创建result节点，并将改节点插入到results子节点中
        node_result = Element(CHILD_NODE_RESULT, {NODE_ATTRIBUTE_DATA_TYPE: NODE_PARAMETER_DATA_BASICTYPE} )
        in_results_element.append(node_result)
        parse_process_log("ROOT-DATA, Create result node, type=%s" % NODE_PARAMETER_DATA_BASICTYPE)
            
        #添加value节点
        XMLConstructControl.construct_value_node(node_result,error_info)
    
    
    @staticmethod
    def construct_value_node(in_result_element,in_value_node_data):
        """
        生成基本数据类型<value/>节点
        """
        #添加result/value节点
        node_result_value = Element(CHILD_NODE_VALUE)
        node_result_value.text=XMLConstructControl.node_value_b64encode(in_value_node_data)
        in_result_element.append(node_result_value)
        parse_process_log("Create value node, value node data=%s" % in_value_node_data)

    @staticmethod
    def node_value_b64encode(in_value_node_data):
        """
        对数据进行64位编码,只针对<value/> text值
        """
        if XML_VALUE_DECODE_FALG:
            if isinstance(in_value_node_data, str):
                return base64.b64encode(in_value_node_data)
            
            else:
                return in_value_node_data
        else:
            return in_value_node_data

    @staticmethod
    def check_node_value_type_is_identified(in_value_node_data,in_check_key_flag=False):
        """
        检查参数数据类型是否为常用类型
        """
        parse_process_log("Data type=%s" % type(in_value_node_data))
        
        if in_check_key_flag:
            if isinstance(in_value_node_data, (int,float,long,str,bool,)):
                return True
        else:
            #添加对datetime.datetime数据类型支持 #add by wangjun 02130830
            #添加对unicode数据类型的支持 #add by wangjun 20130902
            #添加对tuple数据类型的支持 #add by wangjun 20130902
            if isinstance(in_value_node_data, (int,float,long,str,list,dict,datetime.datetime,unicode,tuple,)):
                return True
        
        parse_process_log("Not found data type=%s" % type(in_value_node_data))
        return False
    
    
    @staticmethod
    def construct_results_node(in_results_element,in_results_data):
        """
        构造<results/>数据节点
        """
        
        #拦截非常用数据类型处理
        if not XMLConstructControl.check_node_value_type_is_identified(in_results_data):
            return
        
        #type:int,float,log
        if isinstance(in_results_data, (int,float,long)):
            
            #转str类型并通过递归调用数据处理节点
            item_value_string=str(in_results_data)
            XMLConstructControl.construct_results_node(in_results_element,item_value_string)
        
        #type:datetime.datetime #add by wangjun 20130830
        elif isinstance(in_results_data, datetime.datetime):
            
            #格式化时间对象为字符串
            item_value_string=in_results_data.strftime("%Y-%m-%d %H:%M:%S")
            XMLConstructControl.construct_results_node(in_results_element,item_value_string)

        #type:unicode #add by wangjun 20130902
        elif isinstance(in_results_data, unicode):
            
            #将unicode类型转换为str类型
            item_value_string=in_results_data.encode('utf8')
            XMLConstructControl.construct_results_node(in_results_element,item_value_string)

        #type:str    
        elif isinstance(in_results_data, str):
            
            #创建result节点，并将改节点插入到results子节点中
            node_result = Element(CHILD_NODE_RESULT, {NODE_ATTRIBUTE_DATA_TYPE: NODE_PARAMETER_DATA_BASICTYPE} )
            in_results_element.append(node_result)
            parse_process_log("ROOT-DATA, Create result node, type=%s" % NODE_PARAMETER_DATA_BASICTYPE)
            
            #添加value节点
            XMLConstructControl.construct_value_node(node_result,in_results_data)
        
        #type:list
        elif isinstance(in_results_data, (list,tuple,)):

            #处理列表单个数据节点的数据
            for child_data_node in in_results_data:
                
                #拦截非常用数据类型处理
                if not XMLConstructControl.check_node_value_type_is_identified(child_data_node):
                    continue
                
                #设置节点的类型
                if isinstance(child_data_node, (list,tuple,)):
                    value_node_type=NODE_PARAMETER_DATA_LIST
                    
                elif isinstance(child_data_node, dict):
                    value_node_type=NODE_PARAMETER_DATA_DICT
                    
                else:
                    value_node_type=NODE_PARAMETER_DATA_BASICTYPE

                #创建result节点，并将改节点插入到results子节点中
                node_result = Element(CHILD_NODE_RESULT, {NODE_ATTRIBUTE_DATA_TYPE: value_node_type} )
                in_results_element.append(node_result)
                parse_process_log("ROOT-DATA, Create result node, type=%s" % value_node_type)
                
                #处理value节点
                XMLConstructControl.construct_result_node(node_result,child_data_node)
                
        #type:dict
        elif isinstance(in_results_data, dict):

            #处理字典单个数据节点的数据
            value_nde_key_list=in_results_data.keys()
            for key in value_nde_key_list:
                
                child_data_node_key=key
                child_data_node_value=in_results_data[key]
                
                #拦截非常用数据类型处理
                if not XMLConstructControl.check_node_value_type_is_identified(child_data_node_key, True):
                    continue
                
                if not XMLConstructControl.check_node_value_type_is_identified(child_data_node_value):
                    continue
                
                #[KEY]
                #添加value:list节点
                node_result_value = Element(CHILD_NODE_RESULT, {NODE_ATTRIBUTE_DATA_TYPE: NODE_PARAMETER_DATA_LIST})
                in_results_element.append(node_result_value)
                parse_process_log("Create value node, value type is list")
                
                #生成KEY数据节点
                #type:int,float,log
                if isinstance(child_data_node_key, (int,float,long)):
                        
                    #转str类型并通过递归调用数据处理节点
                    item_value_string=str(child_data_node_key)
                    XMLConstructControl.construct_result_node(node_result_value,item_value_string)
    
                #type:str  
                elif isinstance(child_data_node_key, str):
                    #添加value节点
                    XMLConstructControl.construct_value_node(node_result_value,child_data_node_key)

                #[VALUE]
                #生成VALUE数据数据节点
                #type:int,float,log
                if isinstance(child_data_node_value, (int,float,long)):
                        
                    #转str类型并通过递归调用数据处理节点
                    item_value_string=str(child_data_node_value)
                    XMLConstructControl.construct_result_node(node_result_value,item_value_string)

                #type:datetime.datetime #add by wangjun 20130830
                elif isinstance(child_data_node_value, datetime.datetime):
                    
                    #格式化时间对象为字符串
                    item_value_string=child_data_node_value.strftime("%Y-%m-%d %H:%M:%S")
                    XMLConstructControl.construct_result_node(node_result_value,item_value_string)
                
                #type:unicode #add by wangjun 20130902
                elif isinstance(child_data_node_value, unicode):

                    #将unicode类型转换为str类型
                    item_value_string=child_data_node_value.encode('utf8')
                    XMLConstructControl.construct_result_node(node_result_value,item_value_string)

                #type:str
                elif isinstance(child_data_node_value, str):
    
                    #添加value节点
                    XMLConstructControl.construct_value_node(node_result_value,child_data_node_value)
                
                #type:list/type:dict #键值为容器类型
                elif isinstance(child_data_node_value, dict) or isinstance(child_data_node_value, (list,tuple,)):
                    
                    #设置节点的类型
                    if isinstance(child_data_node_value, (list,tuple,)):
                        value_node_type=NODE_PARAMETER_DATA_LIST
                        
                    else:
                        value_node_type=NODE_PARAMETER_DATA_DICT
                        
                    #创建result节点，并将改节点插入到results子节点中
                    node_result = Element(CHILD_NODE_VALUE, {NODE_ATTRIBUTE_DATA_TYPE: value_node_type} )
                    node_result_value.append(node_result)
                    parse_process_log("ROOT-DATA, Create result node, type=%s" % value_node_type)
                    
                    #处理value节点
                    XMLConstructControl.construct_result_node(node_result,child_data_node_value)
                            
                

    @staticmethod
    def construct_result_node(in_result_element,in_value_node_data):
        """
        构造<result/>数据节点
        """
        #拦截非常用数据类型处理
        if not XMLConstructControl.check_node_value_type_is_identified(in_value_node_data):
            return
                
        #type:int,float,log
        if isinstance(in_value_node_data, (int,float,long)):
            
            #转str类型并通过递归调用数据处理节点
            item_value_string=str(in_value_node_data)
            XMLConstructControl.construct_result_node(in_result_element,item_value_string)
        
        #type:datetime.datetime #add by wangjun 20130830
        elif isinstance(in_value_node_data, datetime.datetime):
                    
            #格式化时间对象为字符串
            item_value_string=in_value_node_data.strftime("%Y-%m-%d %H:%M:%S")
            XMLConstructControl.construct_result_node(in_result_element,item_value_string)
        
        #type:unicode #add by wangjun 20130902
        elif isinstance(in_value_node_data, unicode):

            #将unicode类型转换为str类型
            item_value_string=in_value_node_data.encode('utf8')
            XMLConstructControl.construct_result_node(in_result_element,item_value_string)
            
        #type:str     
        elif isinstance(in_value_node_data, str):
            #添加value节点
            XMLConstructControl.construct_value_node(in_result_element,in_value_node_data)
            
        #type:list 
        elif isinstance(in_value_node_data, (list,tuple,)):
            
            #处理列表单个数据节点的数据
            XMLConstructControl.construct_result_node_type_is_list(in_result_element,in_value_node_data)
        
        #type:dict
        elif isinstance(in_value_node_data, dict):
            
            #处理字典单个数据节点的数据
            XMLConstructControl.construct_result_node_type_is_dict(in_result_element,in_value_node_data)
        
        
    @staticmethod
    def construct_result_node_type_is_list(in_result_element,in_value_node_data):
        """
        构造列表数据类型数据节点
        """
        #type:list 
        if not isinstance(in_value_node_data, (list,tuple,)):
            return
        
        #处理列表单个数据节点的数据
        for child_data_node in in_value_node_data:

            #拦截非常用数据类型处理
            if not XMLConstructControl.check_node_value_type_is_identified(child_data_node):
                continue
            
            #type:int,float,log
            if isinstance(child_data_node, (int,float,long,)):
                    
                #转str类型并通过递归调用数据处理节点
                item_value_string=str(child_data_node)
                XMLConstructControl.construct_result_node(in_result_element,item_value_string)
                
            #type:datetime.datetime #add by wangjun 20130830
            elif isinstance(child_data_node, datetime.datetime):
                        
                #格式化时间对象为字符串
                item_value_string=child_data_node.strftime("%Y-%m-%d %H:%M:%S")
                XMLConstructControl.construct_result_node(in_result_element,item_value_string)
        
            #type:unicode #add by wangjun 20130902
            elif isinstance(child_data_node, unicode):
                
                #将unicode类型转换为str类型
                item_value_string=child_data_node.encode('utf8')
                XMLConstructControl.construct_result_node(in_result_element,item_value_string)
            
            #type:str  
            elif isinstance(child_data_node, str):

                #添加value节点
                XMLConstructControl.construct_value_node(in_result_element,child_data_node)

            #type:list
            elif isinstance(child_data_node, (list,tuple,)):
                        
                #添加value:list节点
                node_result_value = Element(CHILD_NODE_VALUE, {NODE_ATTRIBUTE_DATA_TYPE: NODE_PARAMETER_DATA_LIST})
                in_result_element.append(node_result_value)
                parse_process_log("Create value node, value type is list")
                    
                #递归将列表中的数据加入到节点中
                XMLConstructControl.construct_result_node(node_result_value,child_data_node)
            
            #type:dict
            elif isinstance(child_data_node, dict):
                
                #添加value:type节点
                node_result_value = Element(CHILD_NODE_VALUE, {NODE_ATTRIBUTE_DATA_TYPE: NODE_PARAMETER_DATA_DICT})
                in_result_element.append(node_result_value)
                parse_process_log("Create value node, value type is dict")
                
                #递归将字典中的数据加入到节点中
                XMLConstructControl.construct_result_node_type_is_dict(node_result_value,child_data_node)

            
    @staticmethod
    def construct_result_node_type_is_dict(in_result_element,in_value_node_data):
        """
        构造字典数据类型数据节点
        """
        #type:dict 
        if not isinstance(in_value_node_data, dict):
            return
        
        #处理字典单个数据节点的数据
        value_nde_key_list=in_value_node_data.keys()
        
        #print list(value_nde_key_list).sort()
        
        for key in value_nde_key_list:

            child_data_node_key=key
            child_data_node_value=in_value_node_data[key]
            
            #拦截非常用数据类型处理
            if not XMLConstructControl.check_node_value_type_is_identified(child_data_node_key,True):
                continue
            
            if not XMLConstructControl.check_node_value_type_is_identified(child_data_node_value):
                continue
            
            #[KEY]
            #添加value:list节点
            node_result_value = Element(CHILD_NODE_VALUE, {NODE_ATTRIBUTE_DATA_TYPE: NODE_PARAMETER_DATA_LIST})
            in_result_element.append(node_result_value)
            parse_process_log("Create value node, value type is list")
            
            #生成KEY数据节点
            #type:int,float,log
            if isinstance(child_data_node_key, (int,float,long)):
                    
                #转str类型并通过递归调用数据处理节点
                item_value_string=str(child_data_node_key)
                XMLConstructControl.construct_result_node(node_result_value,item_value_string)

            #type:str  
            elif isinstance(child_data_node_key, str):
                #添加value节点
                XMLConstructControl.construct_value_node(node_result_value,child_data_node_key)
            
            
            #[VALUE]
            #生成VALUE数据数据节点
            #type:int,float,log
            if isinstance(child_data_node_value, (int,float,long)):
                    
                #转str类型并通过递归调用数据处理节点
                item_value_string=str(child_data_node_value)
                XMLConstructControl.construct_result_node(node_result_value,item_value_string)
            
            #type:datetime.datetime #add by wangjun 20130830
            elif isinstance(child_data_node_value, datetime.datetime):
                
                #格式化时间对象为字符串
                item_value_string=child_data_node_value.strftime("%Y-%m-%d %H:%M:%S")
                XMLConstructControl.construct_result_node(node_result_value,item_value_string)
            
            #type:unicode #add by wangjun 20130902
            elif isinstance(child_data_node_value, unicode):

                #将unicode类型转换为str类型
                item_value_string=child_data_node_value.encode('utf8')
                XMLConstructControl.construct_result_node(node_result_value,item_value_string)
                
            #type:str  
            elif isinstance(child_data_node_value, str):

                #添加value节点
                XMLConstructControl.construct_value_node(node_result_value,child_data_node_value)

            #type:list/type:dict #键值为容器类型
            elif isinstance(child_data_node_value, dict) or isinstance(child_data_node_value, list):
                    
                #设置节点的类型
                if isinstance(child_data_node_value, (list,tuple,)):
                    value_node_type=NODE_PARAMETER_DATA_LIST
                        
                else:
                    value_node_type=NODE_PARAMETER_DATA_DICT
                    
                #创建result节点，并将改节点插入到results子节点中
                node_result = Element(CHILD_NODE_VALUE, {NODE_ATTRIBUTE_DATA_TYPE: value_node_type} )
                node_result_value.append(node_result)
                parse_process_log("ROOT-DATA, Create result node, type=%s" % value_node_type)
                    
                #处理value节点
                XMLConstructControl.construct_result_node(node_result,child_data_node_value)



def test():
    
    try:
        in_message_id="0126345"
        in_status=0

        in_data0=None
        in_data1=['testing1',8000,'testing2',0.54728]
        in_data2={'key1':'somevalue1','key2':'somevalue2',"key3":[1,2,5,8,],'key4':{"chind_key1":"child_somevalue1","chind_key2":['a','bcdf']}}
        in_data3=['arg1',['arg2',{"arg3":"abc","arg4":[1,2,4]}],{"arg5":"5cdef","arg6":["3df3",3],"arg7":1000},0.75,493]
        
        tflag=False
        a = datetime.datetime(2012, 7, 10, 8, 45, 23)
        in_data4=[tflag,None,a, [a,[a,('b','x','e'),],{"key1:": a}],{"key12:": a}, u'测试中文unicode']

        XMLConstructControl.construct_xml_stream_data(in_message_id,in_status,in_data4)
        
    except Exception, e:
        parse_process_log('\n\nXMLConstructControl construct_xml_stream_data error: %s' % e )


if __name__ == '__main__':
    test()