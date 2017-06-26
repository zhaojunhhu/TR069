#coding:utf-8

"""
    nwf 2013-05-09  create

"""

# sys lib
import  sys
import  os
import  random
import  time
from    datetime                        import  datetime
from    datetime                        import  timedelta


# user lib
from    TR069.lib.common.error          import  *
from    TR069.lib.common.event          import  *
import  TR069.lib.common.logs.log       as      log 
import  TR069.lib.common.database       as      db
import  TR069.lib.acss.acs.webservercfg         as      webservercfg
from    TR069.lib.common.function       import  print_trace, get_id
import  verify      # SOAP
from    cpe_operator                    import  CpeOperator


# ---------------------------------- real time ----------------------------
def insert_acs_cpe(sn):
    """
    """
    
    db1 = db.Database()
    
    try:        

        # dynamic
        sql = """ SELECT CPE_ID, SN FROM `CPE` WHERE SN="%s" """ %(sn)
        db1.execute(sql)
        row = db1.fetchone()
        if (not row):
            '''
            sql = """INSERT INTO `CPE`(SN, AUTH_TYPE, CWMP_VERSION, SOAP_INFORM_TIMEOUT, CPE_OPERATOR)
                    VALUES("%s", "%s", "%s", "%s", "%s")""" % (
                    sn, 
                    "digest",
                    "cwmp-1-0",
                    "60",
                    "standard")
            '''
            dict_data = {}
            dict_data['SN'] = sn
            dict_data['AUTH_TYPE'] = 'digest'
            dict_data['CWMP_VERSION'] = 'cwmp-1-0'
            dict_data['SOAP_INFORM_TIMEOUT'] = '60'
            dict_data['CPE_OPERATOR'] = 'standard'
            dict_data['INTERFACE_VERSION'] = 'v1.0'
            
            dict_data['CPE2ACS_NAME'] = webservercfg.CPE2ACS_LOGIN_NAME
            dict_data['CPE2ACS_PASSWORD'] = webservercfg.CPE2ACS_LOGIN_PASSWORD
            dict_data['ACS2CPE_NAME'] = webservercfg.ACS2CPE_LOGIN_NAME
            dict_data['ACS2CPE_PASSWORD'] = webservercfg.ACS2CPE_LOGIN_PASSWORD
            
            sql = insert_into_tbl('CPE', dict_data)         
            db1.execute(sql)

    except Exception,e:
        print_trace(e)
       
    if not row: 
        sql = "SELECT LAST_INSERT_ID() AS CPE_ID"
        db1.execute(sql)
        row = db1.fetchone()
        
    return row.CPE_ID
    
def operate_db(tbl_name, operate_type, dict_data):
    """
    数据库操作，主要提供记录的新增和更新，及查询处理
    """
    #Add by lizn 2014-04-14
    op_type = operate_type.upper()
    if op_type == 'INSERT':
        insert_into_tbl(tbl_name, dict_data)
    elif op_type == 'UPDATE':
        update_tbl(tbl_name, dict_data)
    elif op_type == 'SELECT':
        select_from_tbl(tbl_name, dict_data)
    else:
        info = 'operate_type[%s] is not support!' % operate_type
        log.app_err(info)
      
def select_from_tbl(tbl_name, dict_data):
    """
    查询表记录，数据字典含查询字段dict和查询条件str
    """
    if dict_data == None:
        return None
    
    dict_col = dict_data['columns']
    str_condition = dict_data['condition']
    str_columns = ''
    
    first = True
    for col in dict_col:
        if first == True:
            str_columns = '%s' % col
            first = False
        else:
            str_columns += ', %s' % col
    
    sql = "SELECT %s FROM %s WHERE %s" % (str_columns, tbl_name, str_condition)
    log.app_info(sql)
    
    db1 = db.Database()
    try:
        db1.execute(sql)
        row = db1.fetchone()
        if (not row):
            return None
        
        for col in dict_col:
            dict_col[col] = row.col
        
    except Exception,e:
        print_trace(e)
    
    return True
  
def insert_into_tbl(tbl_name, dict_data):
    """
    新增表记录，暂不支持一次新增多条记录，数据字典为待新增数据键值对
    """
    if dict_data == None:
        return None
    
    str_columns = ''
    str_values = ''
    
    first = True
    for col in dict_data:
        if first == True:
            str_columns = '%s' % col
            str_values = "'%s'" % dict_data[col]
            first = False
        else:
            str_columns += ', %s' % col
            str_values += ", '%s'" % dict_data[col]
    
    sql = "INSERT INTO %s(%s) VALUES(%s)" % (tbl_name, str_columns, str_values)
    log.app_info(sql)
    
    return sql

def update_tbl(tbl_name, dict_data):
    """
    更新表记录，数据字典含更新字段dict和查询条件str
    """
    if dict_data == None:
        return None
    
    dict_col = dict_data['columns']
    str_condition = dict_data['condition']
    str_values = ''
   
    first = True
    for col in dict_col:
        value = dict_col[col]
        if isinstance(value, str):      # type(value) in [type('')]:
            value = db.mdb.escape_string(dict_col[col])
        if first == True:
            str_values = "%s='%s'" % (col, value)
            first = False
        else:
            str_values += ", %s='%s'" % (col, value)
   
    sql = "UPDATE %s SET %s WHERE %s" % (tbl_name, str_values, str_condition)
    log.app_info(sql)
    
    db1 = db.Database()
    try:
        db1.execute(sql)
    except Exception,e:
        print_trace(e)

def update_acs_cpe_new(cpe_id, col_name, col_value):
    """
    """
    
    db1 = db.Database()
    
    try:        
       
        safe_value = col_value
        if isinstance(col_value, str):      # type(value) in [type('')]:
            safe_value = db.mdb.escape_string(col_value)
        
        sql = """UPDATE `CPE` SET %s="%s" WHERE CPE_ID=%s """ %(
                    col_name, safe_value, cpe_id)
        
        log.app_info(sql)
        db1.execute(sql)

    except Exception,e:
        print_trace(e)               
                  

def insert_acs_log(message, body):
    """
    nwf 2014-03-05; not use
    """
    
    db1 = db.Database() 
    
    try:        

        time1 = datetime.now()

        body = db1.escape_string(body)
        
        sql = """INSERT INTO `LOG`(MESSAGE, MESSAGE2, TIME_START) VALUES 
                            ("%s", "%s", "%s")""" %(
                            message, body, str(time1))         
        db1.execute(sql)         

    except Exception,e:
        print_trace(e)            
           

def insert_acs_rpc(sn, rpc_name, rpc_args, worklist_id):
    """
    """
    
    from cpe import CPE
    
    db1 = db.Database()
    cpe = CPE.get_cpe(sn)
    cpe_id = cpe.get_cpe_id()
        
    try:

        #args = db1.escape_string(str(rpc_args))
        time1 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if not worklist_id:
            worklist_id = 0
   
        sql = """INSERT INTO `RPC`(RPC_NAME, WORKLIST_ID, CPE_ID, SN, TIME_START)
                VALUES("%s", %s, %s, "%s", "%s") """ % (
                    rpc_name,
                    worklist_id,
                    cpe_id,
                    sn,
                    str(time1))
        db1.execute(sql)    

    except Exception,e:
        print_trace(e) 

    sql = "SELECT LAST_INSERT_ID() as RPC_ID"
    db1.execute(sql)
    row = db1.fetchone()
    rpc_id = row.RPC_ID
    
    try:
        
        args = db1.escape_string(str(rpc_args))
        sql2 = """INSERT INTO RPC_EX(RPC_ID, RPC_PARAMETERS, RESULT_CONTENT) VALUES(%s, "%s", "") """ % (rpc_id, args)
        db1.execute(sql2)
        
    except Exception, e:
        print_trace(e)

    return rpc_id

def update_acs_rpc_time(cpe, col_name, col_value):
    """
    """  
    db1 = db.Database()
    
    # 从缓存中读取当前RPC的ID
    curr_rpc_id = cpe.cpe_db_index.get_rpc_id()
    
    try:        
        sql = """UPDATE `RPC` SET %s="%s" WHERE RPC_ID=%s """ %(
                    col_name, col_value, curr_rpc_id)         
        db1.execute(sql)    

    except Exception,e:
        print_trace(e) 

def update_acs_rpc_response(request, msg, obj):
    """
    """    
    from cpe import CPE
    
    db1 = db.Database()
    cpe = CPE.get_cpe(obj.sn)
    
    for nwf in [1]:
    
        try: 

            time1       = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            result1     = int(msg - EVENT_RPC_GROUP) % 3
            if (result1 == 1):
                result11 = "success"
            elif (result1 == 2):
                result11 = "fail"

            # nwf 2014-02-25; from memory
            id_ = cpe.cpe_db_index.get_rpc_id()     

            result2 = db1.escape_string(str(obj.dict_ret))
            sql = """UPDATE RPC SET RESULT_STATUS="%s", TIME_FINISH="%s" WHERE RPC_ID=%s """ %(
                        result11,                       
                        str(time1), 
                        id_)         
            db1.execute(sql)
            
            sql2 = """UPDATE RPC_EX SET RESULT_CONTENT="%s" WHERE RPC_ID=%s """ % (result2, id_)
            db1.execute(sql2)

        except Exception,e:
            print_trace(e)
   
def update_inform_rpc(cpe, time):
    """
    Add by lizn 2014-03-11
    只更新CPE主动Inform时，且 event_code != '6 CONNECTION REQUEST'时的RPC信息
    """    
    from cpe import CPE
    
    db1 = db.Database()
    
    for i in [1]:
    
        try: 

            #time = datetime.now()
            result_status = 'success'

            # 从缓存中读取当前RPC的ID
            curr_rpc_id = cpe.cpe_db_index.get_rpc_id()

            sql = """UPDATE RPC SET RESULT_STATUS="%s", TIME_FINISH="%s" WHERE RPC_ID=%s """ %(
                        result_status, str(time), curr_rpc_id)       
            db1.execute(sql)
            
            '''
            result_content = ''
            sql2 = """UPDATE RPC_EX SET RESULT_CONTENT="%s" WHERE RPC_ID=%s """ % (result_content, curr_rpc_id)
            db1.execute(sql2)
            '''

        except Exception,e:
            print_trace(e)      


def update_acs_rpc_tx(sn):
    """
    """
    from cpe import CPE
    
    db1 = db.Database()
    cpe = CPE.get_cpe(sn)
    
    for nwf in [1]:
    
        try:      

            # from memory(max(ID) from RPC and SN)
            curr_rpc_id = cpe.cpe_db_index.get_rpc_id()
            
            # from memory
            time_s1_start = cpe.cpe_soap.time_s1_start
            time_s1_finish = cpe.cpe_soap.time_s1_finish
            
            sql = """UPDATE RPC SET TIME_S1_START="%s", TIME_S1_FINISH="%s" WHERE RPC_ID=%s """ %(
                        time_s1_start, time_s1_finish, curr_rpc_id)
            db1.execute(sql)                  

        except Exception,e:
            print_trace(e)         
   

def insert_acs_soap(message, direction, sn, content_head, content_head2="", content_body="", eventcodes=""):
    """
    
    """      
    from cpe import CPE

    ret = None
    
    db1 = db.Database() 
        
    try:                                     

        cpe = CPE.get_cpe(sn)
            
        curr_rpc_id = cpe.cpe_db_index.get_rpc_id()
        cpe_id = cpe.get_cpe_id()
        
        time_exec = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        content_head    = db1.escape_string(content_head)
        content_head2   = db1.escape_string(content_head2)
        content_body    = db1.escape_string(content_body)
        eventcodes2     = db1.escape_string(eventcodes)
                    
        sql = """INSERT INTO `SOAP`(RPC_ID, MSG_TYPE, TIME_EXEC, DIRECTION, CPE_ID, SN, EVENT_CODE) VALUES
                    ('%s', '%s', '%s', '%s', '%s', '%s', '%s')""" %(
                    curr_rpc_id,
                    message,
                    time_exec,
                    direction,
                    cpe_id,
                    sn,
                    eventcodes2)         
        db1.execute(sql)

        # 
        sql = "SELECT LAST_INSERT_ID() AS SOAP_ID"
        db1.execute(sql)
        row = db1.fetchone()        
        soap_id = row.SOAP_ID
        
        sql2 = """INSERT INTO `SOAP_EX`(SOAP_ID, CONTENT_HEAD, HEAD_EX, CONTENT_BODY) VALUES(%s, '%s', '%s', '%s')""" %(
                    soap_id, content_head, content_head2, content_body)
        db1.execute(sql2)
        
        
    except Exception,e:
        print_trace(e) 

    return soap_id
       

def insert_acs_worklist(obj_database, id_desc):
    """
    """
    
    db1 = db.Database() 
        
    try:

        args = db1.escape_string(str(obj_database.dict_data))
        username = db1.escape_string(obj_database.username)
        password = db1.escape_string(obj_database.userid)

        sql = """INSERT INTO `WORKLIST`(WORKLIST_DESC, WORKLIST_TYPE, WORKLIST_NAME, STATUS,
                                        USER_NAME, USER_ID,
                                        TIME_INIT, TIME_BIND,
                                        WORKLIST_GROUP) VALUES 
                        ("%s", "%s", "%s", "%s",
                        "%s", "%s",
                        "%s", "%s",
                        "%s")""" %(
                    id_desc, obj_database.type_, obj_database.worklist_name, obj_database.status,
                    username, password,
                    obj_database.time_build, obj_database.time_bind, 
                    obj_database.group)
        log.app_info(sql)
        db1.execute(sql)
        
        sql = "SELECT LAST_INSERT_ID() AS WORKLIST_ID"
        db1.execute(sql)
        row = db1.fetchone()        
        worklist_id = int(row.WORKLIST_ID)
        
        sql2 = """INSERT INTO `WORKLIST_EX`(WORKLIST_ID, PARAMETERS, RESULT) VALUES(%s, '%s', '')""" %(
                    worklist_id, args)
        db1.execute(sql2)

    except Exception,e:
        print_trace(e)
        
    return worklist_id
        
   
def update_acs_worklist(obj_database, col_name, col_value):
    """
    """
    """
    # 先将str或unicode类型的描述转换成int类型标识，提高查询效率 Alter by lizn 2014-05-21
    # eg. 'worklist_2014-05-20_18:00:36.713_24629926' ---> 106
    from cpe_user_worklist import CpeUserWorklist
    id_ = obj_database.id_
    if isinstance(id_, str):
        worklist_id = CpeUserWorklist.m_dict_desc_id[id_]
    elif isinstance(id_, unicode):
        id_temp = id_.encode('utf8')
        worklist_id = CpeUserWorklist.m_dict_desc_id[id_temp]
    else:
        worklist_id = id_
    """
    
    db1 = db.Database() 
        
    try:

        col_value = db1.escape_string(str(col_value))

        sql = """UPDATE `WORKLIST`  SET %s = "%s" WHERE WORKLIST_DESC='%s' """ %(
                    col_name,
                    col_value, 
                    obj_database.id_)
        
        log.app_info(sql)
        db1.execute(sql)   

    except Exception,e:
        print_trace(e)
        
def update_acs_worklist_by_id(worklist_id, col_name, col_value):
    """
    """
    
    db1 = db.Database() 
        
    try:

        col_value = db1.escape_string(str(col_value))

        sql = """UPDATE `WORKLIST`  SET %s = "%s" WHERE WORKLIST_ID=%s """ %(
                    col_name,
                    col_value, 
                    worklist_id)
        
        log.app_info(sql)
        db1.execute(sql)   

    except Exception,e:
        print_trace(e)
        
def update_acs_worklist_ex_by_id(worklist_id, col_name, col_value):
    """
    """
    db1 = db.Database() 
        
    try:

        col_value = db1.escape_string(str(col_value))

        sql = """UPDATE `WORKLIST_EX`  SET %s = "%s" WHERE WORKLIST_ID=%s """ %(
                    col_name,
                    col_value, 
                    worklist_id)
        
        log.app_info(sql)
        db1.execute(sql)   

    except Exception,e:
        print_trace(e) 
           

def update_acs_logic_worklists_status():
    """
    """
    db1 = db.Database() 
        
    try:

        # 2014-03-06 09:08:15.860000 -> 2014-03-06 09:08:16.047000
        # 1 ;running->fail
        sql = """update `WORKLIST` SET STATUS="%s" WHERE 
                    WORKLIST_TYPE="%s" AND  
                    STATUS="%s" AND 
                    SN<>"" """ %(
                    WORK_LIST_STATUS_FAIL, 
                    WORK_LIST_TYPE_LOGIC, 
                    WORK_LIST_STATUS_RUNNING)         
        db1.execute(sql)           

        # 2 ;bind->abnormal
        sql = """update `WORKLIST` SET STATUS="%s" WHERE 
                    WORKLIST_TYPE="%s" AND  
                    STATUS="%s" """ %(
                    WORK_LIST_STATUS_ABNORMAL, 
                    WORK_LIST_TYPE_LOGIC, 
                    WORK_LIST_STATUS_BIND)         
        db1.execute(sql)

    except Exception,e:
        print_trace(e)
    
def insert_ex_acs_worklist_log(worklist_id, obj_database):
    """
    """
    """
    # 先将str或unicode类型的描述转换成int类型标识，提高查询效率 Alter by lizn 2014-05-21
    # eg. 'worklist_2014-05-20_18:00:36.713_24629926' ---> 106
    from cpe_user_worklist import CpeUserWorklist
    id_ = obj_database.id_
    if isinstance(id_, str):
        worklist_id = CpeUserWorklist.m_dict_desc_id[id_]
    elif isinstance(id_, unicode):
        id_temp = id_.encode('utf8')
        worklist_id = CpeUserWorklist.m_dict_desc_id[id_temp]
    else:
        worklist_id = id_
    """
    #worklist_id = obj_database.worklist_id
    
    result = obj_database.dict_ret['str_result']
    #if not result:
        #log.app_info(result)
        #return
    
    db1 = db.Database() 
    db2 = db.Database() 
    
    try:

        # worklist use unicode, escape not support
        # result = obj_database.dict_ret["str_result"]
        if (isinstance(result, unicode)):
            result = result.encode('utf8')
            #log.app_info(result)
        #result_extra = "执行工单前的CPE信息:\n"
        result_extra = "\noperator运营商=%s,\n"
        result_extra += "interface version接口规范=%s,\n"
        result_extra += "cpe device type设备类型=%s\n\n"
        
        result_ex = result_extra % (obj_database.operator, obj_database.cpe_interface_version, obj_database.domain)
        # nwf 2014-07-09; only user need, sys worklist no need
        if (obj_database.group == "USER"):
            result = result_ex + result
        
        result2 = db1.escape_string(result)
        log.app_info(result2)

        # exist?
        sql = """ SELECT RESULT FROM `WORKLIST_EX` WHERE WORKLIST_ID=%s """ % worklist_id
        db1.execute(sql)
        row = db1.fetchone()
        if (row):
            #log.app_info(result2)
            log.app_info(row.RESULT)
            # update
            if row.RESULT:  # 若原来值为'', 则直接写入；否则，合并再写入
                result2 = row.RESULT + "\n" + result2

            sql = """UPDATE `WORKLIST_EX` SET RESULT="%s" WHERE WORKLIST_ID=%s """ %(
                        result2, worklist_id)
                        
            sql2 = sql.decode("utf8")   # odbc is unicode
            db2.execute(sql2)             
        else:
            # insert                
            sql = """INSERT INTO `WORKLIST_EX`(WORKLIST_ID, RESULT) VALUES                        
                            (%s, "%s")""" %(
                        worklist_id,
                        result2)
                        
            sql2 = sql.decode("utf8")   # odbc is unicode
            db2.execute(sql2)   

    except Exception,e:
        print_trace(e) 


# --------------------------------save -----------------------------
def exit_acs_db():
    """
    """           
    pass    

# --------------------------------restore -----------------------------

def restore_acs_from_mysql():    
    """
    """
    restore_all_cpe()
    restore_operators()
    

def restore_operators():
    """
    """
    restore_operators_cfg()
    restore_operators_interface_version_default()
    restore_operators_name()
    restore_operators_versions()
    

def restore_operators_cfg():
    """
    """
    from cpe_operator import CpeOperator    

    db1 = db.Database() 
        
    try:

        sql = """SELECT * FROM `WL_CONFIG`"""
        db1.execute(sql)        
        results = db1.fetchall()
        for row in results:
            # get
            name                        = row.ISP
            interface_version           = row.VERSION
                    
            # update cfg
            interface_version = interface_version.lower()
            operator = CpeOperator.get_operator(name, interface_version)
            operator.base_isp          = row.BASE_ISP
            operator.eventcode_map      = row.EVENTCODE_MAP
            operator.cpe2acs_name       = row.CPE2ACS_NAME
            operator.cpe2acs_password   = row.CPE2ACS_PASSWORD
            operator.acs2cpe_name       = row.ACS2CPE_NAME
            operator.acs2cpe_password   = row.ACS2CPE_PASSWORD            
            CpeOperator.set_operator(name, interface_version, operator)
            
    except Exception,e:
        print_trace(e)
    

def restore_operators_interface_version_default():
    """
    """
    from cpe_operator import CpeOperator    

    db1 = db.Database() 
        
    try:

        sql = """SELECT ISP, min(VERSION) as INTERFACE_VERSION_DEFAULT from WL_CONFIG GROUP BY ISP"""
        db1.execute(sql)        
        results = db1.fetchall()
        for row in results:
            # get
            name                        = row.ISP
            interface_version_default   = row.INTERFACE_VERSION_DEFAULT                    

            # update default
            interface_version_default = interface_version_default.lower()
            CpeOperator.set_operator_interface_version_default(name, interface_version_default)
            
    except Exception,e:
        print_trace(e)


def restore_operators_name():
    """
    """
    from cpe_operator import CpeOperator    

    db1 = db.Database() 
        
    try:

        sql = """SELECT distinct ISP FROM `WL_CONFIG`"""
        db1.execute(sql)        
        results = db1.fetchall()
        for row in results:
            # get
            name                        = row.ISP           
            CpeOperator.set_operator_name(name)
            
    except Exception,e:
        print_trace(e)


def restore_operators_versions():
    """
    """
    from cpe_operator import CpeOperator    

    db1 = db.Database() 
        
    try:

        sql = """SELECT ISP, VERSION FROM `WL_CONFIG`"""
        db1.execute(sql)        
        results = db1.fetchall()
        for row in results:
            # get
            name                        = row.ISP
            version1                    = row.VERSION
            CpeOperator.set_operator_version(name, version1)
            
    except Exception,e:
        print_trace(e)



def restore_all_cpe():
    """
    """

    from cpe import CPE    

    db1 = db.Database() 
        
    try:

        sql = """SELECT * FROM `CPE`"""
        db1.execute(sql)        
        results = db1.fetchall()
        for row in results:
            # get
            cpe_id                  = row.CPE_ID
            sn                      = row.SN
            authtype                = row.AUTH_TYPE
            cpe2acs_loginname       = row.CPE2ACS_NAME
            cpe2acs_loginpassword   = row.CPE2ACS_PASSWORD
            acs2cpe_loginname       = row.ACS2CPE_NAME
            acs2cpe_loginpassword   = row.ACS2CPE_PASSWORD
            acs2cpe_url             = row.CONN_RQST_URL
            cwmp_version            = row.CWMP_VERSION
            soap_inform_timeout     = row.SOAP_INFORM_TIMEOUT
            operator                = row.CPE_OPERATOR
            domain                  = row.CPE_DEVICE_TYPE
            software_version        = row.SOFTWARE_VERSION
            hardware_version        = row.HARDWARE_VERSION
            root_node               = row.ROOT_NODE
            time_last_contact       = row.TIME_LAST_CONTACT
            interface_verion        = row.INTERFACE_VERSION
            cpe_worklist_rollback   = row.CPE_WORKLIST_ROLLBACK

            # restore
            #cpe = CPE.add(sn)
            cpe = CPE(sn)            
            d1 = {sn: cpe}   

            log.app_info("restore cpe info([%s]sn=%s)" %(cpe_id, sn))
            CPE.m_dict_sn2cpe.update(d1)
            cpe.set_cpe_id(cpe_id)      # 保存CPE_ID
            cpe.cpe_property.cpe_authtype = authtype
            cpe.cpe_property.cpe2acs_loginname = cpe2acs_loginname
            cpe.cpe_property.cpe2acs_loginpassword = cpe2acs_loginpassword
            cpe.cpe_property.acs2cpe_loginname = acs2cpe_loginname
            cpe.cpe_property.acs2cpe_loginpassword = acs2cpe_loginpassword
            cpe.cpe_property.acs2cpe_url = acs2cpe_url
            cpe.cpe_property.cpe_operator = operator
            cpe.cpe_property.cpe_domain = domain
            cpe.cpe_property.software_version = software_version
            cpe.cpe_property.hardware_version = hardware_version
            cpe.cpe_property.root_node = root_node
            cpe.cpe_property.cpe_interface_version  = interface_verion
            cpe.cpe_property.cpe_worklist_rollback  = cpe_worklist_rollback
            
            cpe.cpe_soap.cwmp_version = cwmp_version
            cpe.cpe_soap.soap_inform_timeout = soap_inform_timeout
            cpe.cpe_soap.time_last_contact = time_last_contact

    except Exception,e:
        print_trace(e)
        
def restore_acs_part_worklist_by_id(worklist_id):
    """
    获取指定工单表记录的部分字段，工单描述、工单名称、状态、SN号等
    """
    sql = "SELECT WORKLIST_DESC, WORKLIST_NAME, STATUS, SN, OPERATOR, "
    sql += "OPERATOR_VERSION, DOMAIN, USER_NAME, USER_ID, WORKLIST_GROUP FROM WORKLIST "
    sql += "WHERE WORKLIST_ID=%s" % worklist_id
    
    obj = None
    
    db1 = db.Database()
    try:
        db1.execute(sql)
        row = db1.fetchone()
        if not row:
            return None
    
        obj = MsgWorklist()
        #obj.id_ = worklist_id
        #obj.worklist_id = int(row.WORKLIST_ID)
        obj.id_ = row.WORKLIST_DESC
        obj.worklist_name = row.WORKLIST_NAME
        obj.group = row.WORKLIST_GROUP
        obj.status = row.STATUS
        obj.operator               = row.OPERATOR
        obj.cpe_interface_version  = row.OPERATOR_VERSION
        obj.domain                 = row.DOMAIN
        if row.SN:
            obj.sn = row.SN
        if row.USER_NAME:
            obj.username = row.USER_NAME
        if row.USER_ID:
            obj.userid = row.USER_ID
            
    except Exception,e:
            print_trace(e) 
        
    return obj
       

def restore_acs_part_worklist(worklist_desc):
    """
    获取指定工单表记录的部分字段，工单标识，工单描述、工单名称、状态、SN号等
    """
    sql = "SELECT WORKLIST_ID, WORKLIST_DESC, WORKLIST_NAME, STATUS, SN, "
    sql += "OPERATOR, OPERATOR_VERSION, DOMAIN, USER_NAME, USER_ID, WORKLIST_GROUP FROM WORKLIST "
    sql += "WHERE WORKLIST_DESC='%s'" % worklist_desc
    
    obj = None
    
    db1 = db.Database()
    try:
        db1.execute(sql)
        row = db1.fetchone()
        if not row:
            return None
    
        obj = MsgWorklist()
        #obj.id_ = worklist_id
        obj.worklist_id = int(row.WORKLIST_ID)
        obj.id_ = row.WORKLIST_DESC
        obj.worklist_name = row.WORKLIST_NAME
        obj.group = row.WORKLIST_GROUP
        obj.status = row.STATUS
        obj.operator               = row.OPERATOR
        obj.cpe_interface_version  = row.OPERATOR_VERSION
        obj.domain                 = row.DOMAIN
        if row.SN:
            obj.sn = row.SN
        if row.USER_NAME:
            obj.username = row.USER_NAME
        if row.USER_ID:
            obj.userid = row.USER_ID
            
    except Exception,e:
            print_trace(e) 
        
    return obj
    
def restore_acs_worklist(id_):
    """
    """
    """
    # 先将str或unicode类型的描述转换成int类型标识，提高查询效率 Alter by lizn 2014-05-21
    # eg. 'worklist_2014-05-20_18:00:36.713_24629926' ---> 106
    from cpe_user_worklist import CpeUserWorklist
    if isinstance(id_, str):
        worklist_id = CpeUserWorklist.m_dict_desc_id[id_]
    elif isinstance(id_, unicode):
        id_temp = id_.encode('utf8')
        worklist_id = CpeUserWorklist.m_dict_desc_id[id_temp]
    else:
        worklist_id = id_
    """
    
    obj_database        = None

    db1 = db.Database() 

    for nwf in [1]:
    
        try:

            #sql = """SELECT * FROM `WORKLIST` WHERE WORKLIST_ID=%s """ % worklist_id
            sql = """SELECT * FROM `WORKLIST` WHERE WORKLIST_DESC='%s' """ % id_
            db1.execute(sql)            
            row = db1.fetchone()
            if (not row):
                break
            
            worklist_id                     = int(row.WORKLIST_ID)

            obj_database                    = MsgWorklist()
            obj_database.id_                = row.WORKLIST_DESC
            obj_database.worklist_id        = worklist_id
                            
            obj_database.worklist_name      = row.WORKLIST_NAME
            obj_database.group              = row.WORKLIST_GROUP

            #obj_database.cpe_id             = row.CPE_ID
            #obj_database.sn                 = row.SN
            # convert None->""
            if (not row.SN):
                obj_database.sn = ""
            else:
                obj_database.sn = row.SN
                
            obj_database.operator               = row.OPERATOR
            obj_database.cpe_interface_version  = row.OPERATOR_VERSION
            obj_database.domain                 = row.DOMAIN
            obj_database.type_                  = row.WORKLIST_TYPE                
            obj_database.username               = row.USER_NAME
            obj_database.userid                 = row.USER_ID
            obj_database.status                 = row.STATUS  
            obj_database.rollback               = row.ROLLBACK 
            # in next table ; nwf 2014-06-28
            #obj_database.dict_data          = eval(row.ARGS)   # str->dict

            #fomat1 = "%Y-%m-%d %H:%M:%S.%f"
            fomat1 = "%Y-%m-%d %H:%M:%S"        # compatible
            if (row.TIME_INIT):    
                try:
                    obj_database.time_build         = datetime.strptime(row.TIME_INIT, fomat1)
                except Exception,e:
                    obj_database.time_build         = datetime.strptime(row.TIME_INIT, fomat2)
            if (row.TIME_BIND):
                try:
                    obj_database.time_bind          = datetime.strptime(row.TIME_BIND, fomat1)
                except Exception,e:
                    obj_database.time_bind          = datetime.strptime(row.TIME_BIND, fomat2)
            if (row.TIME_RESERVE):
                try:
                    obj_database.time_reserve       = datetime.strptime(row.TIME_RESERVE, fomat1)
                except Exception,e:
                    obj_database.time_reserve       = datetime.strptime(row.TIME_RESERVE, fomat2)
            if (row.TIME_EXEC_START):
                try:
                    obj_database.time_exec_start    = datetime.strptime(row.TIME_EXEC_START, fomat1)
                except Exception,e:
                    obj_database.time_exec_start    = datetime.strptime(row.TIME_EXEC_START, fomat2)
            if (row.TIME_EXEC_FINISH):
                try:
                    obj_database.time_exec_end      = datetime.strptime(row.TIME_EXEC_FINISH, fomat1)
                except Exception,e:
                    obj_database.time_exec_end      = datetime.strptime(row.TIME_EXEC_FINISH, fomat2)

            # worklist_log
            sql = """SELECT * FROM `WORKLIST_EX` WHERE WORKLIST_ID=%s """ % worklist_id
            db1.execute(sql)            
            row = db1.fetchone()
            if (not row):
                break  
            # utf8->unicode
            result = row.RESULT
            obj_database.dict_data = eval(row.PARAMETERS)   # str->dict
            if result:
                obj_database.dict_ret["str_result"] = result.decode("utf8")
            else:
                obj_database.dict_ret['str_result'] = ''
            
        except Exception,e:
            print_trace(e) 

    return obj_database


def restore_acs_logic_worklists():
    """
    """
    obj_databases       = []
    
    db1 = db.Database() 

    try:

        time1           = datetime.now()
        
        sql = """SELECT WORKLIST_ID AS ID FROM `WORKLIST` WHERE WORKLIST_TYPE="%s" and
                    DATEDIFF("%s", `TIME_INIT`)<="%s" """ %(
                    WORK_LIST_TYPE_LOGIC,
                    time1,
                    webservercfg.LOGIC_WORKLIST_LIFETIME)
        db1.execute(sql)
        
        results = db1.fetchall()
        for row in results:
                        
            obj_database = restore_acs_part_worklist_by_id(int(row.ID))
            obj_databases.append(obj_database)
        
    except Exception,e:
        print_trace(e)     

    return obj_databases
  


# --------------------------------memory->db -----------------------------
def restore_acs_wait_eventcode(id_):
    """
    """
    obj_database        = None

    db1 = db.Database() 

    for nwf in [1]:
    
        try:

            sql = """SELECT * FROM `MONITOR_RULES` WHERE MONITOR_DESC="%s" """ %(id_)
            db1.execute(sql)            
            row = db1.fetchone()
            if (not row):
                break

            obj_database                    = MsgWaitEventCode()
            obj_database.id_                = id_

            obj_database.sn                 = row.SN
            if (not row.SN):
                obj_database.sn             = ""
                
            obj_database.status             = row.STATUS

            d1 = eval(row.CFG)                
            include = d1.get("INCLUDE", None)
            exclude = d1.get("EXCLUDE", None)
            obj_database.include_eventcodes = include
            obj_database.exclude_eventcodes = exclude
                       
            fomat1 = "%Y-%m-%d %H:%M:%S.%f"
            fomat2 = "%Y-%m-%d %H:%M:%S"
            if (row.TIME_START):   
                try:
                    obj_database.time_start     = datetime.strptime(row.TIME_START, fomat1)
                except Exception,e:
                    obj_database.time_start     = datetime.strptime(row.TIME_START, fomat2)
            if (row.TIME_STOP):            
                try:
                    obj_database.time_stop      = datetime.strptime(row.TIME_STOP, fomat1)
                except Exception,e:
                    obj_database.time_stop      = datetime.strptime(row.TIME_STOP, fomat2)
        except Exception,e:
            print_trace(e) 

    return obj_database


def restore_acs_soap_inform(obj_database):
    """
 
    return [inform1, inform2)], [time1, time2]
    """
    informs             = []
    times               = []
    
    db1 = db.Database() 
    db2 = db.Database() 

    sn = obj_database.sn
    try:
        sql = """SELECT SOAP_ID FROM `MONITOR_RESULT` WHERE MONITOR_DESC="%s" """ %(
                obj_database.id_)            
        db1.execute(sql)        
        results = db1.fetchall()        
        for row in results:
            soap_id  = row.SOAP_ID

            sql = """SELECT CONTENT_BODY, TIME_START FROM `SOAP`, `SOAP_EX`, `RPC` 
                    WHERE SOAP.SOAP_ID="%s" 
                        AND SOAP.SOAP_ID=SOAP_EX.SOAP_ID 
                        AND SOAP.RPC_ID = RPC.RPC_ID""" %(
                    soap_id)
            db2.execute(sql)            
            row = db2.fetchone()            
            if (not row):
                continue
                            
            body    = row.CONTENT_BODY                                      
            # get inform
            inform1 = get_soap_inform(body)
            if (not inform1):
                continue                

            fomat1 = "%Y-%m-%d %H:%M:%S.%f"
            fomat2 = "%Y-%m-%d %H:%M:%S"
            time1   = row.TIME_START
            if (time1):                
                try:
                    time1 = datetime.strptime(time1, fomat1)
                except Exception,e:
                    time1 = datetime.strptime(time1, fomat2)
            # collect
            informs.append(inform1)
            times.append(time1)
        
    except Exception,e:
        print_trace(e)     

    return informs, times    


def restore_acs_soap_inform_str(obj_database):
    """
    return [inform1, inform2)], [time1, time2]
    inform is str, not object
    """
    informs             = []
    times               = []
    inform1             = "" 

    db1 = db.Database() 
    db2 = db.Database() 

    sn = obj_database.sn
    try:
        sql = """SELECT SOAP_ID FROM `MONITOR_RESULT` WHERE MONITOR_DESC="%s" """ %(
                obj_database.id_)            
        db1.execute(sql)        
        results = db1.fetchall()        
        for row in results:
            soap_id  = row.SOAP_ID

            sql = """SELECT HEAD_EX, CONTENT_BODY, TIME_START FROM `SOAP`, `SOAP_EX`, `RPC` 
                    WHERE SOAP.SOAP_ID="%s" 
                        AND SOAP.SOAP_ID=SOAP_EX.SOAP_ID 
                        AND SOAP.RPC_ID = RPC.RPC_ID""" %(
                    soap_id)
            db2.execute(sql)            
            row = db2.fetchone()            
            if (not row):
                continue
                                               
            head = row.HEAD_EX
            body = row.CONTENT_BODY            
            inform1 = head
            if (body):
                inform1 = inform1 + body             

            fomat1 = "%Y-%m-%d %H:%M:%S.%f"
            fomat2 = "%Y-%m-%d %H:%M:%S"
            time1   = row.TIME_START
            if (time1):
                try:
                    time1 = datetime.strptime(time1, fomat1)
                except Exception,e:
                    time1 = datetime.strptime(time1, fomat2)
                    
            # collect
            informs.append(inform1)
            times.append(time1)
        
    except Exception,e:
        print_trace(e)     

    return informs, times  


# -------------------------------- assist -----------------------------
def get_soap_inform(body):
    """
    """
    soap_verify = verify.Verify()
    ret_api = soap_verify.check_soap_msg(body)    
    
    return soap_verify
    

def match_inform(obj_database, eventcodes):
    """
    """
    bl_match = False


    s_travel = set(eventcodes)
    s_config_include = set(obj_database.include_eventcodes)
    s_config_exclude = set(obj_database.exclude_eventcodes) 

    if ((s_config_include.issubset(s_travel)) and 
        (s_config_exclude.isdisjoint(s_travel))):
        
        bl_match = True
            

    return bl_match   


def restore_acs_inform_alarm(id_):
    """
    """
    obj_database        = None

    db1 = db.Database() 

    for nwf in [1]:
    
        try:

            sql = """SELECT * FROM `MONITOR_RULES` WHERE MONITOR_DESC="%s" """ %(id_)
            db1.execute(sql)            
            row = db1.fetchone()
            if (not row):
                break

            obj_database                    = MsgAlarmInform()
            obj_database.id_                = id_
            
            obj_database.sn                 = row.SN                
            obj_database.status             = row.STATUS
            obj_database.dict_ret["str_result"] = str(row.STATUS_DESC).decode("utf8")  # for RF
            obj_database.time_start         = row.TIME_START
            obj_database.time_stop          = row.TIME_STOP

            d1 = eval(row.CFG)
            obj_database.parameterlist      = d1.get("PARAMETER_LIST", None)
            obj_database.limit_min          = d1.get("LIMIT_MIN", None)
            obj_database.limit_max          = d1.get("LIMIT_MAX", None)
            obj_database.timelist           = d1.get("TIMELIST", None)
            obj_database.mode               = d1.get("MODE", None)
           
            fomat1 = "%Y-%m-%d %H:%M:%S.%f"
            fomat2 = "%Y-%m-%d %H:%M:%S"
            if (row.TIME_START):  
                try:
                    obj_database.time_start     = datetime.strptime(row.TIME_START, fomat1)
                except Exception,e:
                    obj_database.time_start     = datetime.strptime(row.TIME_START, fomat2)
                    
            if (row.TIME_STOP): 
                try:
                    obj_database.time_stop      = datetime.strptime(row.TIME_STOP, fomat1)
                except Exception,e:
                    obj_database.time_stop      = datetime.strptime(row.TIME_STOP, fomat2)
            
        except Exception,e:
            print_trace(e) 

    return obj_database


def restore_acs_inform_monitor(id_):
    """
    """
    obj_database        = None

    db1 = db.Database() 

    for nwf in [1]:
    
        try:

            sql = """SELECT * FROM `MONITOR_RULES` WHERE MONITOR_DESC="%s" """ %(id_)
            db1.execute(sql)            
            row = db1.fetchone()
            if (not row):
                break

            obj_database                    = MsgMonitorInform()
            obj_database.id_                = id_

            obj_database.sn                 = row.SN                
            obj_database.status             = row.STATUS
            obj_database.dict_ret["str_result"] = str(row.STATUS_DESC).decode("utf8")  # for RF
            obj_database.time_start         = row.TIME_START
            obj_database.time_stop          = row.TIME_STOP

            d1 = eval(row.CFG)
            obj_database.parameterlist      = d1.get("PARAMETER_LIST", None)
            obj_database.timelist           = d1.get("TIMELIST", None)
            obj_database.parameter_values   = d1.get("PARAMETER_VALUES", None)
           
            fomat1 = "%Y-%m-%d %H:%M:%S.%f"
            fomat2 = "%Y-%m-%d %H:%M:%S"
            if (row.TIME_START):    
                try:
                    obj_database.time_start     = datetime.strptime(row.TIME_START, fomat1)
                except Exception,e:
                    obj_database.time_start     = datetime.strptime(row.TIME_START, fomat2)
                
            if (row.TIME_STOP):            
                try:
                    obj_database.time_stop      = datetime.strptime(row.TIME_STOP, fomat1)
                except Exception,e:
                    obj_database.time_stop      = datetime.strptime(row.TIME_STOP, fomat2)
            
        except Exception,e:
            print_trace(e) 

    return obj_database


# ---------------------------- monitor rules/result --------------
def insert_acs_monitor_rules(obj_database):
    """
    
    """      
    
    db1 = db.Database() 

    for nwf in [1]:    
    
        try:                                      

            if (isinstance(obj_database, MsgWaitEventCode)):

                type_ = "WAIT_EVENTCODE"
                
                d1 = {  "INCLUDE":      obj_database.include_eventcodes, 
                        "EXCLUDE":      obj_database.exclude_eventcodes}
                
 
            elif (isinstance(obj_database, MsgAlarmInform)):

                type_ = "ALARM"
                
                d1 = {  "PARAMETER_LIST":   obj_database.parameterlist, 
                        "LIMIT_MIN":        obj_database.limit_min, 
                        "LIMIT_MAX":        obj_database.limit_max, 
                        "TIMELIST":         obj_database.timelist, 
                        "MODE":             obj_database.mode}                
                
            elif (isinstance(obj_database, MsgMonitorInform)):

                type_ = "MONITOR"
                
                d1 = {"PARAMETER_LIST":   obj_database.parameterlist, 
                      "TIMELIST":         obj_database.timelist  }
                      
            else:
                desc    = "obj(%s) is not recognise." %(obj_database)
                log.app_err(desc)
                
                break

            # common
            cfg = str(d1)
            cfg = db1.escape_string(cfg)
                
            sql = """INSERT INTO `MONITOR_RULES`(MONITOR_DESC, TYPE, CFG, SN) VALUES
                        ('%s', '%s', '%s', '%s')""" %(
                        obj_database.id_,
                        type_,
                        cfg,                    
                        obj_database.sn)                        
            db1.execute(sql) 
               
        except Exception,e:
            print_trace(e) 



def update_acs_monitor_rules(obj_database, col_name, col_value):
    """
    """
    
    db1 = db.Database() 
        
    try:
    
        if (isinstance(col_value, unicode)):
            col_value = col_value.encode('utf8') 
            
        col_value2 = db1.escape_string(str(col_value))

        sql = """update `MONITOR_RULES`  SET %s = "%s" WHERE MONITOR_DESC="%s" """ %(
                    col_name,
                    col_value2, 
                    obj_database.id_)
        sql2 = sql.decode("utf8")
        db1.execute(sql2)   

    except Exception,e:
        print_trace(e)

def insert_monitor_result(soap_id, soap_inform, sn):
    """
    """
    
    db1 = db.Database() 

    # 2014-03-06 14:29:04.753000 -> 2014-03-06 14:29:04.800000
    id_objs = find_monitor_result_id(sn)
    for id_, obj_database in id_objs:
            
        try:

            # match?
            bl_match = is_match_monitor_result(obj_database, soap_inform)
            if (not bl_match):
                continue

            sql = """INSERT INTO `MONITOR_RESULT`(MONITOR_DESC, SOAP_ID) VALUES                        
                            ("%s", "%s")""" %(
                        id_,
                        soap_id)         
            db1.execute(sql)   

        except Exception,e:
            print_trace(e)    


def find_monitor_result_id(sn):
    """
    """
    id_objs = []

    db1 = db.Database()
    
    try:        
        time1           = datetime.now()
        
        sql = """ SELECT MONITOR_DESC AS ID, TYPE FROM `MONITOR_RULES` WHERE STATUS="%s" AND 
                    SN="%s" AND 
                    DATEDIFF("%s", `TIME_START`)<="%s" """ %(
                "start_success", 
                sn,
                time1,
                webservercfg.MONITOR_INFORM_LIFETIME)
        db1.execute(sql)        
        results = db1.fetchall()
        for row in results:     

            id_ = row.ID
            type_ = row.TYPE
            if (type_ == "ALARM"):
                obj = restore_acs_inform_alarm(id_)
            elif (type_ == "MONITOR"):
                obj = restore_acs_inform_monitor(id_)
            elif (type_ == "WAIT_EVENTCODE"):
                obj = restore_acs_wait_eventcode(id_)
            
            id_objs.append((id_, obj))

    except Exception,e:
        print_trace(e)  
    
    return id_objs

# add by zsj 2014-6-12
def get_worklist_template(isp='', version='', domain='', method=''):
    """
    获取工单模板中的全部或部分内容
    """ 
    if isp and version and domain and method:
       
        # 获取指定运营商、版本号、设备类型和支持工单的参数
        sql = "SELECT PARAMETERS FROM `WL_TEMPLATE` WHERE ISP='%s' AND VERSION='%s' " % (isp, version)
        sql += "AND DOMAIN='%s' AND METHOD='%s'" % (domain, method)
        
        db1 = db.Database()
        db1.execute(sql)
        results = db1.fetchall()
        if not results:
            return None
        
        str_dict_template = results[0][0]
        return eval(str_dict_template)
    else:
        return None
    
    return list_ret


def is_match_monitor_result(obj_database, soap_inform):
    """
    """
    from cpe import CPE
    
    bl_ret = False

    try:

        if (isinstance(obj_database, MsgWaitEventCode)):
            if ("any_eventcode" in obj_database.include_eventcodes):
                bl_ret = True
            else:
                
                eventcodes = [event.EventCode for event in soap_inform.result.Event]
                bl_ret = match_inform(obj_database, eventcodes)              

        elif (isinstance(obj_database, MsgAlarmInform)):
            bl_ret = CPE.is_inform_x(soap_inform, "X CT-COM ALARM") or CPE.is_inform_x(soap_inform, "M X_CU_ALARM")
            
        elif (isinstance(obj_database, MsgMonitorInform)):
            bl_ret = CPE.is_inform_x(soap_inform, "X CT-COM MONITOR")

    except Exception,e:
        print_trace(e) 
        
    return bl_ret
    

def get_monitor_result_informid(id_):
    """
    """
    ids = []
    
    db1 = db.Database()
    
    try:        

        #sql = """ SELECT SOAP_ID FROM `MONITOR_RESULT` WHERE ID="%s" """ %(
        #            id_)
        sql = """ SELECT SOAP_ID FROM `MONITOR_RESULT` WHERE MONITOR_DESC="%s" """ %(id_)
        # Alter by lizn 2014-03-10
        
        db1.execute(sql)
        results = db1.fetchall()
        for row in results:
            ids.append(row.SOAP_ID)

    except Exception,e:
        print_trace(e)     

    return ids

def check_worklist_status():
    """
    """

    db1 = db.Database()
    db2 = db.Database()
    
    try:        

        # dynamic
        sql = """ SELECT WORKLIST_ID, TIME_INIT FROM  `WORKLIST` WHERE WORKLIST_TYPE="%s" AND 
                    STATUS="%s" """ %(
                        WORK_LIST_TYPE_LOGIC, 
                        "init")
        db1.execute(sql)
        results = db1.fetchall()
        
        fomat2 = "%Y-%m-%d %H:%M:%S.%f"
        fomat1 = "%Y-%m-%d %H:%M:%S"
        dt_now = datetime.now()
        for row in results:
            try:           
                time_init     = datetime.strptime(row.TIME_INIT, fomat1)
            except Exception,e:
                time_init     = datetime.strptime(row.TIME_INIT, fomat2)
            
            if (dt_now - time_init >= timedelta(seconds=webservercfg.CHECK_ACS_LOGIC_WORKLIST_STATUS_TIMEINTERVAL)):
                sql = """UPDATE `WORKLIST` SET STATUS="%s" WHERE WORKLIST_ID=%s """ %(
                            WORK_LIST_STATUS_EXPIRE, 
                            row.WORKLIST_ID)
                db2.execute(sql)            

    except Exception,e:
        print_trace(e)  
    

def get_last_session_soap(sn):
    """
    get last session for rpc
    """
    from cpe import CPE
    
    ret = False
    content = ""
    str_soap_ids = ","
    list_soap_ids = []
    
    db1 = db.Database()
    cpe = CPE.get_cpe(sn)

    for nwf in [1]:
    
        try:        

            # from memory; nwf 2014-02-25
            soap_inform_id_4rpc = cpe.cpe_db_index.get_soap_inform_id_4rpc()

            #  get rpc id (use key)
            sql = """ SELECT RPC_ID FROM `SOAP` WHERE 
                        SOAP_ID="%s" """ %(
                        soap_inform_id_4rpc)
            db1.execute(sql)            
            row = db1.fetchone()
            if (row):
                rpc_id = row.RPC_ID
            else:
                content = "please do rpc first, then you can get last session soap."
                break

            soap_204_id = cpe.cpe_db_index.get_soap_204_id()
            #  get soap ids
            sql = """ SELECT SOAP_ID FROM `SOAP` WHERE 
                        RPC_ID="%s" AND 
                        SOAP_ID>=%s AND  SOAP_ID<=%s """ %(
                        rpc_id,
                        soap_inform_id_4rpc, soap_204_id)
            db1.execute(sql)            
            results = db1.fetchall()
            list_soap_ids =[("%s" %row.SOAP_ID) for row in results]
            str_soap_ids = str_soap_ids.join(list_soap_ids)

            #  get content (use key)
            sql = """ SELECT HEAD_EX, CONTENT_BODY FROM `SOAP_EX` WHERE 
                        SOAP_ID in (%s) """ %(
                        str_soap_ids)
            db1.execute(sql)            
            results = db1.fetchall()
            for row in results:            
                head = row.HEAD_EX
                body = row.CONTENT_BODY
                content = content + head
                if (body):
                    content = content + body

            ret = True
            
        except Exception,e:
            print_trace(e)   

    return ret, content



# global 
__all__ = [
            "operate_db",
            "insert_acs_cpe",
            "update_acs_cpe_new",
            "insert_acs_log", 

            "insert_acs_rpc",
            "update_acs_rpc_time",
            "update_acs_rpc_response",
            "update_inform_rpc",
            "update_acs_rpc_tx", 
            "insert_acs_soap",
            "insert_acs_worklist",
            "update_acs_worklist",
            "update_acs_worklist_by_id",
            "update_acs_worklist_ex_by_id",
            "update_acs_logic_worklists_status", 
            "insert_ex_acs_worklist_log", 
            
            "exit_acs_db",
                        
            "restore_acs_from_mysql", 

            "restore_acs_part_worklist_by_id",
            "restore_acs_part_worklist",
            "restore_acs_worklist",
            "restore_acs_logic_worklists",
            "get_worklist_template",

            "restore_acs_wait_eventcode",
            "restore_acs_soap_inform", 
            "restore_acs_soap_inform_str",

            "restore_acs_inform_alarm", 
            "restore_acs_inform_monitor",  

            "insert_acs_monitor_rules",
            "update_acs_monitor_rules", 

            "insert_monitor_result",
            "get_monitor_result_informid", 

            "check_worklist_status",

            "get_last_session_soap",
          ]
