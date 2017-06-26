#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: dataprocess
#  function: MethondData,ParseRecvData,ConstructResponseData
#            
#  Author: ATT development group
#  version: V1.0
#  date: 2013.8.29
#  change log:
#  wangjun  20130829    create
# ***************************************************************************

#user denfine interface
from xmlparsecontrol import XMLParseControl
from xmlconstructcontrol import XMLConstructControl

#import log
from constantdefinitions import DEBUG_FLAG
if DEBUG_FLAG:
    from outlog import OutLog as log
else:
    import TR069.lib.common.logs.log  as log


class MethondData():
    """
    解析从客户端发送过来的数据，并将数据格式化成下面的模板
    """
    def __init__(self):
        self._client_addr=None
        self._client_port=None
        self._client_conn_handle=None
        
        self._sequence=None
        self._method_name=None
        self._method_parameters_list=[]
        
        self._cpe_id=None
        
    def set_method_data(self,in_client_addr,
                            in_client_port,
                            in_client_conn_handle,
                            in_sequence,
                            in_method_name,
                            in_cpe_id,
                            in_method_parameters_list):
        """
        保存数据到对应的节点中
        """
        self._client_addr=in_client_addr
        self._client_port=in_client_port
        self._client_conn_handle=in_client_conn_handle
        
        self._sequence=in_sequence
        self._method_name=in_method_name
        self._cpe_id=in_cpe_id
        self._method_parameters_list=in_method_parameters_list
        
        
    def get_client_addr_and_port(self):
        return self._client_addr, self._client_port

    def get_client_conn_handle(self):
        return self._client_conn_handle
    
    def get_request_sequence_id(self):
        return self._sequence
    
    def get_request_method_name(self):
        return self._method_name

    def get_request_cpe_id(self):
        return self._cpe_id
    
    def get_request_method_parameters(self):
        return self._method_parameters_list


class ParseRecvData():
    
    @staticmethod
    def parse_recv_data(int_recvdatabuffer):
        """
        解析XML流数据
        """
        rc_flag=False
        
        try:
            print int_recvdatabuffer

            rc_flag,rc_data_list=XMLParseControl.parse_xml_stream_data(int_recvdatabuffer)
            #log.debug_info(rc_data_list)
            
        except Exception, e:
            log.debug_info(e)
            return None, None, []
        
        if (True == rc_flag and
            4==len(rc_data_list)):
            
            out_sequence=rc_data_list[0]
            out_method_name=rc_data_list[1]
            out_cpe_id=rc_data_list[2]
            out_method_parameters_list=rc_data_list[3]
            return out_sequence, out_method_name, out_cpe_id,out_method_parameters_list

        else:
            
            return None, None, []

        

class ConstructResponseData():
    
    #发送给TCL客户端的数据以\x1a为结束符
    RESPONSE_DATA_TCL_MODE_END_CHARS='\x1a'
    
    @staticmethod
    def construct_response_data(in_message_id,
                                in_status,
                                in_response_data):
        
        try:
            construct_xml_stream_data=XMLConstructControl.construct_xml_stream_data(in_message_id,in_status,in_response_data)
            #log.debug_info(construct_xml_stream_data)
            
        except Exception, e:
            log.debug_info(e)
            return None

        #删除介绍符追加
        #out_data=("%s%s" % (construct_xml_stream_data,ConstructResponseData.RESPONSE_DATA_TCL_MODE_END_CHARS))
        
        return construct_xml_stream_data





#测试解析                 
def test_parse():
                        
    try:
        message="""<?xml version='1.0' encoding='UTF-8'?>
                <root>
                    <messageid>0123456</messageid>
                    <function>test_method</function>
                    <parameters>
                        <parameter name='data1' type="basictype">
                            <value type="string">dGVzdGluZzE=</value>
                        </parameter>
                        <parameter name='data2' type="basictype">
                            <value type="string">dGVzdGluZzI=</value>
                        </parameter>
                        <parameter name='data3' type="list">
                            <value type="int">124</value>
                            <value type="bool">True</value>
                            <value type="string">dGVzdGluZzE=</value>
                        </parameter>
                        <parameter name='data4' type="dict">
                            <item>
                                <key>test</key>
                                <value type="string">dGVzdGluZzE=</value>
                            </item>
                        </parameter>
                    </parameters>
                </root>
                """
                
        tmp_sequence, \
        tmp_method_name, \
        tmp_method_parameters_list=ParseRecvData.parse_recv_data(message)
        
        log.debug_info('\n\nmessage_id=%s, method_name=%s, parameters_list=%s' % (tmp_sequence,tmp_method_name,tmp_method_parameters_list) )
        
    except Exception, e:
        log.debug_err('\n\n%s' % e )
        

#测试构造   
def test_construct():

    try:
        in_message_id="0126345"
        in_status=0

        in_data0=None
        in_data1=['testing1',8000,'testing2',0.54728]
        in_data2={'key1':'somevalue1','key2':'somevalue2',"key3":[1,2,5,8,],'key4':{"chind_key1":"child_somevalue1","chind_key2":['a','bcdf']}}
        in_data3=['arg1',['arg2',{"arg3":"abc","arg4":[1,2,4]}],{"arg5":"5cdef","arg6":["3df3",3],"arg7":1000},0.75,493]
        
        tflag=False
        in_data4=[tflag,None]
        
        in_message_id='0123456'
        out_construct_xml_stream_data=ConstructResponseData.construct_response_data(in_sequence_id,in_status,in_data1)
        log.debug_info(out_construct_xml_stream_data )
        
    except Exception, e:
        parse_process_log('\n\n%s' % e )
        


 
if __name__ == '__main__':
    #test_parse()
    test_construct()







