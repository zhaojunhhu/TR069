#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: parse
#  function: provide basice API to parse SOAP envelope
#  Author: ATT development group
#  version: V1.0
#  date: 2012.08.20
#  change log:
#  lana     20120820     created
#  lana     20120910     use lxml.etree instead xml.etree, convert the returned
#                        iteraor of getiterator() to list
#                        
# ***************************************************************************

import os

#from xml.etree import ElementTree
import lxml.etree as ElementTree

import TR069.lib.common.logs.log as log 

CHECK_XML_SCHEMA_VALIDATE  = 0

class Parse:
    """
    parse module:provide basice API to parse SOAP envelope
    """
    m_xmlschema_list = []
    
    @staticmethod
    def get_xmlschema_obj():
        """
        parse xmlschema xsd files, and return the object to verify xml file's validate
        """
        # get the xsd files path
        path = os.path.dirname(__file__) + '\\schema\\'
        # get all files name
        list_all_file = os.listdir(path)
        
        for filename in list_all_file:
            try:
                full_path = path + filename
                xmlschema_doc = ElementTree.parse(full_path).getroot()
                xmlschema = ElementTree.XMLSchema(xmlschema_doc)
                Parse.m_xmlschema_list.append(xmlschema)
            except Exception,e:
                err_info = "Parse xml schema files occures error:%s" % e
                log.debug_info(err_info)
                
            
            
    def __init__(self):
        pass
    
    def analyze_soap_envelope(self, xml_src, soap_envelope_tag):
        """
        Analyze xml_src,  and return the list of soap envelope object.
        """
         
        # when xml_src is a filepath
        if xml_src[0] != '<':
            root = ElementTree.parse(xml_src).getroot()
        # when xml_src is a string
        else:
            root = ElementTree.fromstring(xml_src)
        
        # check xml schama validate    
        if CHECK_XML_SCHEMA_VALIDATE == 1:
            
            if Parse.m_xmlschema_list == []:
                Parse.get_xmlschema_obj()
                
            for obj_xmlschema in Parse.m_xmlschema_list:
                
                if obj_xmlschema.validate(root):
                    break
            else:
                return None
                
        return list(root.getiterator(tag = soap_envelope_tag))

    def element_is_existed(self, element_object, element_name):
        """
        whether exist element named element_name under element_object.
        if existed return 1, or return 0
        """
        
        element_list = list(element_object.getiterator(tag = element_name))
        if len(element_list) >= 1:
            return 1
        else:
            return 0
    
    def get_element_name(self, element_object):
        """
        get name of element_object, return tag of element_object
        """
            
        return element_object.tag
    
    def get_element_attribute(self, element_object, element_name):
        """
        get the attribute of element_name under element_object. if element_name is
        not existed or there are more than one element_name,return none
        """
        
        element_list = list(element_object.getiterator(tag = element_name))
        if len(element_list) == 1:	
            return element_list[0].attrib
        elif len(element_list) > 1:
            log.debug_info("There are more then one",element_name,"under", element_object)
            return None
        else:
            log.debug_info("There is no",element_name,"under", element_object)
            return None
    
    def get_element_value(self, element_object, element_name):
        """
        get the value of element_name under element_object. if element_name is
        not existed, return none
        """
        
        element_list = list(element_object.getiterator(tag = element_name))
        if len(element_list) >= 1:
            element_value_list = []
            
            for element in element_list:
                element_value_list.append(element.text)
                
            return element_value_list
        else:
            return None

    def get_children_name_list(self, element_object):
        """
        get children name of element_object, return the list of children name
        """
        
        children_list = element_object.getchildren()
        children_name_list = []
        for element in children_list:
            children_name_list.append(element.tag)
            
        return children_name_list
    
    def get_children_list(self, element_object):
        """
        get children element of element_object, return the list of children element
        """
            
        return element_object.getchildren()
    
    def get_children_value(self, element_object):
        """
        get value of  element_object's children_element recursively,
        return all children_element's [name,value] by list
        """
        tmp_list = []
        children_element_list = element_object.getchildren()
        if len(children_element_list) == 0:
            log.debug_info("element_object have no children")
            return None
        for element in children_element_list:
            sub_children_list = element.getchildren()
            if len(sub_children_list) == 0:
                tmp_list.append([element.tag, element.text, element.attrib])
            else:
                tmp_list.append([element.tag, get_children_value(element)])
        return tmp_list

# create an instance of class and binding all object methods to varialbles
# then we don't need to create instance everytime when we call the class's method
try:
    g_parse
except NameError:
    g_parse = Parse()
    analyze_soap_envelope = g_parse.analyze_soap_envelope
    element_is_existed = g_parse.element_is_existed
    get_element_name = g_parse.get_element_name
    get_element_value = g_parse.get_element_value
    get_element_attribute = g_parse.get_element_attribute
    get_children_list = g_parse.get_children_list
    get_children_name_list = g_parse.get_children_name_list
    get_children_value = g_parse.get_children_value


def test(xml_src, envelope_tag):
    
    soap_list = analyze_soap_envelope(xml_src, envelope_tag)
    
    if len(soap_list) == 1:
        print get_children_name_list(soap_list[0])
        body = get_children_list(soap_list[0])[1]
        element_list = get_children_value(body)
        print element_list
        
        print get_element_name(body)
        print get_element_value(body, "Fault")
        print get_element_attribute(body, "Fault")
        print element_is_existed(body, "Fault")
    else:
        print "not support more than one soap envelope"
    
if __name__ == '__main__':
    
    test(open('D:/test/test.txt').read(),"{http://schemas.xmlsoap.org/soap/envelope/}Envelope")