# -*- coding: utf-8 -*-

from django.db import connection

def get_method_parameter(is_public=1):
    """
    获取所有的工单方法、参数及初始默认值
    """
    cursor = connection.cursor()
    sql = "SELECT METHOD_ID, METHOD_NAME FROM METHOD WHERE IS_PUBLIC=%s ORDER BY METHOD_NAME" % is_public
    cursor.execute(sql)
    results = cursor.fetchall()
    if not results:
        return None
        
    dict_methods = {}
    sql_temp = "SELECT NAME, VALUE FROM PARAMETER WHERE METHOD_ID = %s ORDER BY ROW_NO"
    for item in results:
        method_id = item[0]
        method_name = item[1]
        sql = sql_temp % method_id
        cursor.execute(sql)
        #parameters = list(cursor.fetchall())
        parameters = []
        for para in cursor.fetchall():
            parameters.append(list(para))
            
        dict_methods[method_name] = parameters
    
    return dict_methods

def get_domain_method():
    """
    获取所有ISP下支持的设备类型及工单方法
    """
    cursor = connection.cursor()
    sql = "SELECT ISP_ID, ISP_NAME FROM ISP"
    cursor.execute(sql)
    results = cursor.fetchall()
    if not results:
        return None
    
    dict_isp = {}
    for isp in results:
        isp_id = isp[0]
        isp_name = isp[1]
        # get domain_id and domain_name
        # eg.((12L, u'ADSL_2LAN'),(5L, u'ADSL_4+1'),(2L, u'ADSL_4LAN'))
        sql_select = "SELECT w.DOMAIN_ID, d.DOMAIN_NAME FROM WORKLIST_TEMPLATE AS w, DOMAIN AS d "
        sql_where = "WHERE w.ISP_ID=%s AND w.DOMAIN_ID=d.DOMAIN_ID GROUP BY w.DOMAIN_ID ORDER BY d.DOMAIN_NAME" % isp_id
        sql = sql_select + sql_where
        cursor.execute(sql)
        domains = cursor.fetchall()
        if not domains:
            continue
        
        list_domains = []
        # get method_name
        # eg. [u'Eagleeyes_Disable', u'Eagleeyes_Enable', u'IPTV_Disable', u'IPTV_Enable']
        sql_select = "SELECT m.METHOD_NAME FROM WORKLIST_TEMPLATE AS w, METHOD AS m "
        sql_where = "WHERE w.ISP_ID=%s AND w.DOMAIN_ID=%s AND w.METHOD_ID=m.METHOD_ID GROUP BY w.METHOD_ID ORDER BY m.METHOD_NAME"
        for domain in domains:
            domain_id = domain[0]
            domain_name = domain[1]
            sql = sql_select + sql_where % (isp_id, domain_id)
            cursor.execute(sql)
            # methods = list(cursor.fetchall())
            methods = []
            for name in cursor.fetchall():
                methods.append(name[0])
            
            dict_domain = {}
            dict_domain[domain_name] = methods
            list_domains.append(dict_domain)
        
        dict_isp[isp_name] = list_domains
        
    return dict_isp

def get_one_field(col_name=''):
    """
    获取工单模板中的单列不重复的值
    """
    list_ret = []
    
    if not col_name:
        return list_ret
    
    sql = "SELECT %s FROM `WL_TEMPLATE` GROUP BY %s" % (col_name, col_name)
    cursor = connection.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    if not results:
        return list_ret
    
    for item in results:
        list_ret.append((item[0], item[0]))
    
    return list_ret

def get_config_user_pwd(isp='', version=''):
    """
    获取工单配置表中指定运营商和版本的上下行用户名及密码
    """
    
    if not isp or not version:
        return None
    
    sql = "SELECT CPE2ACS_NAME, CPE2ACS_PASSWORD, ACS2CPE_NAME, ACS2CPE_PASSWORD FROM `WL_CONFIG` "
    sql += "WHERE ISP='%s' AND VERSION='%s'" % (isp, version)
    cursor = connection.cursor()
    cursor.execute(sql)
    results = cursor.fetchone()
    
    return results

def get_worklist_args(isp='', version='', domain='', method=''):
    """
    获取工单模板中指定的工单参数
    """
    
    return get_worklist_template('PARAMETERS', isp, version, domain, method)

def get_worklist_doc(isp='', version='', domain='', method=''):
    """
    获取工单模板中指定的工单文档
    """
    
    return get_worklist_template('DOC', isp, version, domain, method)


def get_worklist_template(value='PARAMETERS', isp='', version='', domain='', method=''):
    """
    获取工单模板中的全部或部分内容
    """ 
    if not isp:
        # 获取所有运营商
        sql = "SELECT ISP FROM `WL_CONFIG` GROUP BY ISP"
    elif not version:   
        # 获取指定指定运营商下所有版本号
        sql = "SELECT VERSION FROM `WL_CONFIG` WHERE ISP='%s' GROUP BY VERSION" % isp
    elif not domain:
        # 获取指定运营商和版本号下所有设备类型
        sql = "SELECT DOMAIN FROM `WL_TEMPLATE` WHERE ISP='%s' AND VERSION='%s' GROUP BY DOMAIN" % (isp, version)
    elif not method:
        # 获取指定运营商、版本号和设备类型下所有支持的工单
        sql = "SELECT METHOD FROM `WL_TEMPLATE` WHERE ISP='%s' AND VERSION='%s' AND DOMAIN='%s' GROUP BY METHOD" % (isp, version, domain)
    else:
        # 获取指定运营商、版本号、设备类型和支持工单的参数或文档
        sql = "SELECT %s FROM `WL_TEMPLATE` WHERE ISP='%s' AND VERSION='%s' " % (value, isp, version)
        sql += "AND DOMAIN='%s' AND METHOD='%s'" % (domain, method)
        
    cursor = connection.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    if not results:
        return None
    
    list_ret = []
    for item in results:
        list_ret.append(item[0])
    
    return list_ret

# global 
__all__ = [
            'get_method_parameter',
            'get_domain_method',
            'get_one_field',
            'get_config_user_pwd',
            'get_worklist_args',
            'get_worklist_doc',
            'get_worklist_template',
          ]
