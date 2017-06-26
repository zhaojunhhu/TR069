
#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: parseparameterstype
#  function: parse tr069 data model definition xml files, get parameters and their type
#  Author: ATT development group
#  version: V1.0
#  date: 2012.09.10
#  change log:
#  lana     20120910     created
#  lana     20120926     optimize code
#  lana     20140301     support for motive xml file parsing
# ***************************************************************************


import os

import lxml.etree as ElementTree

import TR069.lib.common.logs.log as log 

PARSE_UNFINISH = "parse unfinish"

class ParseParametersType:
    """
    parse TR-069 data model definitions xml files, get all parameters's type
    """
    
    def __init__(self, file_path=""):
        """
        initialize
        """
        self.file_path = file_path          # xml files be saved directory
        self.data_type = {}                 # save the parse result of tr-106-1-0-0-types.xml
        self.dict_parameters_type = {}      # save all parsed parameters and their type  
        self.dict_component = {}            # save all files' component definition
        
    def parse_data_type(self):
        """
        parse "tr-106-1-0-0-types.xml", get TR-069 Data Model Data Types
        save all defined data type in data_type dict. 
        """
        
        log.debug_info("parsing tr-106-1-0-0-types.xml")
        # get file full path
        file_full_path = os.path.join(self.file_path, "tr-106-1-0-0-types.xml")
        
        # parse xml file, and get the root object
        root = ElementTree.parse(file_full_path).getroot()
        
        # get all "dataType" object iterator
        iter_data_type = root.getiterator(tag="dataType")
        
        for object in iter_data_type:
            
            # get attributes of object
            dict_object_attrib = object.attrib
            
            # get name attribute value
            object_name = dict_object_attrib['name']
            
            # if dataType have 'base' attribute, get data type from base dataType
            if 'base' in dict_object_attrib:
                    
                object_base_name = dict_object_attrib['base']
                
                # check 'base' name whether save in self.data_type or not
                if object_base_name in self.data_type:
                    
                    self.data_type[object_name] = self.data_type[object_base_name]
                else:
                    log.debug_info(object_name, "base", object_base_name,
                                   "but the base type is not exist, something is wrong!")
                    
            else:
                
                # get data type from the second child element of dataType,the first is description
                list_object_children = object.getchildren()
                if len(list_object_children) == 2:
                    
                    # dataType have children object difined its data type
                    self.data_type[object_name] = list_object_children[1].tag
                    
                else:
                    log.debug_info(object_name, "dataType struct is error, \
                                   it have more than two children.")
        
    
    def parse_tr069_parameters_definition(self, xml_file):
        """
        parsed tr069 parameters definition xml file. return dict contain xml file's
        parameters' full name(keys) and parameters type(values)
        xml_file: be parsed xml file name
        """
        
        log.debug_info("parsing ", xml_file)
        
        dict_results = {}       # save current file parse parameter type results
        dict_components = {}    # save current file parse components results
        
        # parse xml file, and get the root object
        file_full_path = os.path.join(self.file_path, xml_file)
        root = ElementTree.parse(file_full_path).getroot()
        
        # get root children object
        list_root_children = root.getchildren()
        
        # go through all root children elements
        for root_children in list_root_children:
            
            # get import components, save to dict_components
            if root_children.tag == "import":
                
                list_import_children = root_children.getchildren()
                
                if list_import_children != []:
                    
                    import_file_name = root_children.attrib['file']
                    
                    check_flag = 1  # whether need to check imported file parsed or not
                    
                    for import_children in list_import_children:
                        
                        if import_children.tag == "component":
                            
                            if check_flag == 1:
                                check_flag = 0   # just check one times
                                
                                if import_file_name not in self.dict_component:
                                    
                                    log.debug_info("parse unfinish, need file ", import_file_name)
                                    return PARSE_UNFINISH
                            
                            component_name = import_children.attrib['name']
                            # component is rename in this file, get component definition from 'ref' 
                            if 'ref' in import_children.attrib:
                                ref_name = import_children.attrib['ref']
                                dict_components[component_name] = \
                                    self.dict_component[import_file_name][ref_name]
                            else:
                                dict_components[component_name] = \
                                    self.dict_component[import_file_name][component_name]
                            
            elif root_children.tag == "component":
                
                component_name = root_children.attrib['name']
                
                # parse component's object-parameter struct
                dict_tmp_component = self.parse_parameter_struct(root_children)
                
                # get sub "component" defined in "component"
                list_children_component = root_children.getchildren()
                for children_component in list_children_component:
                    
                    if children_component.tag == "component":
                        ref_name = children_component.attrib['ref']
                        dict_tmp_component.update(dict_components[ref_name])
                
                # save parsed result to dict_components, use component_name as key
                dict_components[component_name] = dict_tmp_component
                
            elif root_children.tag == "model":
                
                # parse model's object-parameter struct
                dict_tmp_model = self.parse_parameter_struct(root_children)
                # save parsed result to dict_results
                dict_results.update(dict_tmp_model)
                
                # parse model's component struct
                list_model_children = root_children.getchildren()
                
                for model_children in list_model_children:
                    if model_children.tag == "component":
                        
                        path_name = model_children.attrib['path']
                        ref_name = model_children.attrib['ref']
                        
                        # get ref component dict
                        dict_ref_component = dict_components[ref_name]
                        
                        # add path_name prefix to each key of dict_ref_component 
                        for key in dict_ref_component.keys():
                            
                            full_name = path_name + key
                            # add full_name and key corresponding value to dict_results
                            dict_results[full_name] = dict_ref_component[key]
                            
        # save all components of current file
        self.dict_component[xml_file] = dict_components
        
        return dict_results	
        
        
    def parse_parameter_struct(self, element):
        """
        parse parameter struct and object-parameter struct, return dict contain
        parameters' full name and parameters type 
        element: the parents element of parameter or object
        """
        
        dict_results = {}
        
        # get all children object of element
        list_children_element = element.getchildren()
        
        for children_element in list_children_element:
            
            # when children_element is 'parameter'
            if children_element.tag == 'parameter':
                dict_para_attrib = children_element.attrib
                if "name" in dict_para_attrib:
                    parameter_name = dict_para_attrib['name']
                elif "base" in dict_para_attrib:
                    parameter_name = dict_para_attrib['base']
                else:
                    log.debug_info("This parameter have no name or base, unknown definition!")
                    
                # get parameter children object
                list_para_children = children_element.getchildren()
                    
                # if parameter have no children, don't need to save it, it have saved in base model
                if list_para_children == []:
                    continue
                else:
                    
                    parameter_type = ""
                    for para_children in list_para_children:
                        
                        # if parameter have 'syntax' element
                        if para_children.tag == 'syntax':
                            # get syntax's children list
                            list_syntax_children = para_children.getchildren()
                            
                            # get parameter's type from syntax children element
                            for syntax_children in list_syntax_children:
                                if syntax_children.tag == "list":
                                    continue
                                elif syntax_children.tag == "default":
                                    continue
                                elif syntax_children.tag == "dataType":
                                    # get dataType's 'ref' attribute value
                                    data_type_ref = syntax_children.attrib['ref']
                                    # find parameter_type from self.data_type dict
                                    parameter_type = self.data_type[data_type_ref]
                                else:
                                    parameter_type = syntax_children.tag
                            
                            # add parameter and its type to dict
                            dict_results[parameter_name] = parameter_type
                            
            elif children_element.tag == 'object':
                
                # get object name from object attribute 'name' or 'base'
                dict_object_attrib = children_element.attrib
                if "name" in dict_object_attrib:
                    object_name = dict_object_attrib['name']
                elif "base" in dict_object_attrib:
                    object_name = dict_object_attrib['base']
                else:
                    log.debug_info("The object have no name or base, unknown definition!")
                
                # get children of 'object'	
                list_children_object = children_element.getchildren()
                
                # if object have no parameter sub element, ignore this object
                if list_children_object == []:
                    continue
                
                for children_object in list_children_object:
                    # ignore the others sub element,eg: 'uniqueKey', 'description'
                    # just parse 'parameter'
                    if children_object.tag == 'parameter':
                        # get parameter name from parameter attribute 'name' or 'base'
                        dict_para_attrib = children_object.attrib
                        if "name" in dict_para_attrib:
                            parameter_name = dict_para_attrib['name']
                        elif "base" in dict_para_attrib:
                            parameter_name = dict_para_attrib['base']
                        else:
                            log.debug_info("The parameter have no name or base, unknown definition!")
                        
                        
                        # get parameter children object
                        list_para_children = children_object.getchildren()
                        
                        # if parameter have no children, don't need to save it, it have saved in base model
                        if list_para_children == []:
                            continue
                        else:
                            # build parameter's full name
                            full_name = object_name + parameter_name
                            parameter_type = ""
                            for para_children in list_para_children:
                                
                                # if parameter have 'syntax' element
                                if para_children.tag == 'syntax':
                                    # get syntax's children list
                                    list_syntax_children = para_children.getchildren()
                                    
                                    # get parameter's type from syntax children element
                                    for syntax_children in list_syntax_children:
                                        if syntax_children.tag == "list":
                                            continue
                                        elif syntax_children.tag == "default":
                                            continue
                                        elif syntax_children.tag == "dataType":
                                            # get dataType's 'ref' attribute value
                                            data_type_ref = syntax_children.attrib['ref']
                                            # find parameter_type from self.data_type dict
                                            parameter_type = self.data_type[data_type_ref]
                                        else:
                                            parameter_type = syntax_children.tag
                                    
                                    # add parameter and its type to dict
                                    dict_results[full_name] = parameter_type
            else:
                pass  
            
        return dict_results
        
        
    def get_all_parameters_type(self):
        """
        parse all files in self.file_path, and save the parse result 
        in self.dict_parameters_type
        """
        
        try:
            # parse custom xml file 
            self.file_path = os.path.join(os.path.dirname(__file__), "customdatadef", "motive")
            self.get_all_motive_parameters_type()
            
            # parse datamodeldef
            self.file_path = os.path.join(os.path.dirname(__file__), "datamodeldef")
            
            # first parse "tr-106-1-0-0-types.xml"
            self.parse_data_type()
            
            # get all files name in self.file_path
            list_all_file = os.listdir(self.file_path)
            
            # removed the parsed file "tr-106-1-0-0-types.xml"
            list_all_file.remove("tr-106-1-0-0-types.xml")
            
            count = 0
            
            while list_all_file != []:
                count += 1
                log.debug_info( "count:", str(count))
                
                # backup files name list	
                tmp_list_all_file = list_all_file[:]
                
                for i in range(len(tmp_list_all_file)):
                    # ignore directory
                    if os.path.isdir(os.path.join(self.file_path, tmp_list_all_file[i])):
                        list_all_file.remove(tmp_list_all_file[i])
                        continue
                    
                    # parse each file in tmp_list_all_file
                    res = self.parse_tr069_parameters_definition(tmp_list_all_file[i])
                    if res == PARSE_UNFINISH:
                        continue
                    else:
                        log.debug_info("parse suc:", tmp_list_all_file[i])
                        # remove the parsed successfully file
                        list_all_file.remove(tmp_list_all_file[i])
                        # update dict_parameters_type
                        self.dict_parameters_type.update(res)
                        
            
            log.debug_info("parse motive xml file end")
        
        except Exception, e:
            log.debug_err(e)
        
        
    def parse_motive_xml_definition(self, xml_file):
        """
        parsed custom define motive xml file. return dict contain xml file's
        parameters' full name(keys) and parameters type(values)
        xml_file: be parsed xml file name
        """
        
        log.debug_info("parsing ", xml_file)
        
        dict_results = {}       # save current file parse parameter type results
        
        # parse xml file, and get the root object
        file_full_path = os.path.join(self.file_path, xml_file)
        root = ElementTree.parse(file_full_path).getroot()
        
        # get root children object
        list_root_children = root.getchildren()
        
        # go through all root children elements
        for root_children in list_root_children:
            
            # find dataModel node
            if root_children.tag == "dataModel":
                
                # find parameters node
                list_datamodel_children = root_children.getchildren()
                for datamodel_children in list_datamodel_children:
                    if datamodel_children.tag == "parameters":
                        
                        # parse parameters's children node parameter
                        list_parameters_children = datamodel_children.getchildren()
                        for parameters_children in list_parameters_children:
                            tmp_dict_parameter = self.parse_motive_parameter(parameters_children)
                            # save parsed result to dict_results
                            dict_results.update(tmp_dict_parameter)
                            
                        # ignore the node not parameters
                        break
                    
                # ignore the node not dataModel
                break
        
        return dict_results
    
    
    def parse_motive_parameter(self, element, parents_node_path=""):
        """
        parse parameter struct return dict contain
        parameters' full name and parameters type 
        element: the parameter node
        parents_node_path: the parents node's full path
        """
        
        dict_results = {}
        cur_node_name = ""
        cur_node_type = ""
        cur_node_is_array = ""
        
        # get all children object of element
        list_children_element = element.getchildren()
        
        for children_element in list_children_element:
            
            # parse node's name,type and is_array 
            if children_element.tag == 'parameterName':
                cur_node_name = children_element.text
                
            elif children_element.tag == 'parameterType':
                cur_node_type = children_element.text
                
            elif children_element.tag == 'array':
                cur_node_is_array = children_element.text
                
        # check parameter type
        if cur_node_type == "object":
            # not leaf node
            # check is_array
            if cur_node_is_array == "false":
                cur_node_path = parents_node_path + cur_node_name + "."
            else:
                cur_node_path = parents_node_path + cur_node_name + ".{i}."
            
            # find parameters node
            for children_element in list_children_element:
                if children_element.tag == 'parameters':
                    list_parameters_children = children_element.getchildren()
                    for parameters_children in list_parameters_children:
                        tmp_dict_parameter = self.parse_motive_parameter(parameters_children, cur_node_path)
                        # save parsed result to dict_results
                        dict_results.update(tmp_dict_parameter)
        else:
            # leaf node
            cur_node_full_path = parents_node_path + cur_node_name
            # save current node full path to dict_results
            dict_results.update({cur_node_full_path:cur_node_type})
            
        return dict_results
    
    
    def get_all_motive_parameters_type(self):
        """
        parse all files in motive directory, and save the parse result 
        in self.dict_parameters_type
        """
        
        try:
            
            # get all files name in self.file_path
            list_all_file = os.listdir(self.file_path)
            
            while list_all_file != []:
                
                # backup files name list	
                tmp_list_all_file = list_all_file[:]
                
                for i in range(len(tmp_list_all_file)):
                    # ignore directory
                    if os.path.isdir(os.path.join(self.file_path, tmp_list_all_file[i])):
                        list_all_file.remove(tmp_list_all_file[i])
                        continue
                    
                    # parse each file in tmp_list_all_file
                    res = self.parse_motive_xml_definition(tmp_list_all_file[i])
                    if res == PARSE_UNFINISH:
                        continue
                    else:
                        log.debug_info("parse suc:", tmp_list_all_file[i])
                        # remove the parsed successfully file
                        list_all_file.remove(tmp_list_all_file[i])
                        # update dict_parameters_type
                        self.dict_parameters_type.update(res)
                        
            
            log.debug_info("parse end")
        
        except Exception, e:
            log.debug_err(e)



try:
    g_object
except NameError:
    g_object = ParseParametersType() 
    get_all_parameters_type = g_object.get_all_parameters_type
    
# test
def test():
    get_all_parameters_type()
    list_values = g_object.dict_parameters_type.values()
    set_values = set(list_values)
    res2 = [(value, list_values.count(value)) for value in set_values]
    log.debug_info(res2)


      
if __name__ == '__main__':
    
    test()