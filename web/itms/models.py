from django.db import models
from django.utils import timezone
import datetime

# Create your models here.
class CPE(models.Model):
    cpe_id                  = models.IntegerField(db_column='CPE_ID', primary_key=True) # Field name made lowercase.
    sn                      = models.CharField(db_column='SN', unique=True, max_length=70) # Field name made lowercase.
    auth_type               = models.CharField(db_column='AUTH_TYPE', max_length=10, blank=True) # Field name made lowercase.
    cpe2acs_username        = models.CharField(db_column='CPE2ACS_NAME', max_length=50, blank=True) # Field name made lowercase.
    cpe2acs_password        = models.CharField(db_column='CPE2ACS_PASSWORD', max_length=50, blank=True) # Field name made lowercase.
    acs2cpe_username        = models.CharField(db_column='ACS2CPE_NAME', max_length=50, blank=True) # Field name made lowercase.
    acs2cpe_password        = models.CharField(db_column='ACS2CPE_PASSWORD', max_length=50, blank=True) # Field name made lowercase.
    connection_request_url  = models.CharField(db_column='CONN_RQST_URL', max_length=50, blank=True) # Field name made lowercase.
    cwmp_version            = models.CharField(db_column='CWMP_VERSION', max_length=10, blank=True) # Field name made lowercase.
    soap_inform_timeout     = models.IntegerField(db_column='SOAP_INFORM_TIMEOUT', blank=True, null=True) # Field name made lowercase.
    cpe_operator            = models.CharField(db_column='CPE_OPERATOR', max_length=50, blank=True) # Field name made lowercase.
    cpe_device_type         = models.CharField(db_column='CPE_DEVICE_TYPE', max_length=50, blank=True) # Field name made lowercase.
    software_version        = models.CharField(db_column='SOFTWARE_VERSION', max_length=50, blank=True)
    hardware_version        = models.CharField(db_column='HARDWARE_VERSION', max_length=50, blank=True)
    root_node               = models.CharField(db_column='ROOT_NODE', max_length=50, blank=True)
    time_last_contact       = models.CharField(db_column='TIME_LAST_CONTACT', max_length=30, blank=True)
    is_refresh              = models.CharField(db_column='IS_REFRESH', max_length=10, blank=True) # Field name made lowercase.
    time_soap_begin         = models.CharField(db_column='TIME_SOAP_BEGIN', max_length=30, blank=True) # Field name made lowercase.
    time_soap_end           = models.CharField(db_column='TIME_SOAP_END', max_length=30, blank=True) # Field name made lowercase.
    soap_status             = models.IntegerField(db_column='SOAP_STATUS', blank=True, null=True) # Field name made lowercase.
    interface_version       = models.CharField(db_column='INTERFACE_VERSION', max_length=50, blank=True) # Field name made lowercase.
    cpe_worklist_rollback   = models.CharField(db_column='CPE_WORKLIST_ROLLBACK', max_length=10, blank=True) # Field name made lowercase.
    
    def __unicode__(self):
        return self.sn
    
    class Meta:
        managed = False
        db_table = 'CPE'
        
class RPC(models.Model):
    rpc_id = models.IntegerField(db_column='RPC_ID', primary_key=True) # Field name made lowercase.
    rpc_name = models.CharField(db_column='RPC_NAME', max_length=50, blank=True) # Field name made lowercase.
    worklist_id = models.IntegerField(db_column='WORKLIST_ID', blank=True, null=True) # Field name made lowercase.
    cpe_id = models.IntegerField(db_column='CPE_ID', blank=True, null=True) # Field name made lowercase.
    sn = models.CharField(db_column='SN', max_length=70, blank=True) # Field name made lowercase.
    time_start = models.CharField(db_column='TIME_START', max_length=30, blank=True) # Field name made lowercase.
    time_finish = models.CharField(db_column='TIME_FINISH', max_length=30, blank=True) # Field name made lowercase.
    time_s1_start = models.CharField(db_column='TIME_S1_START', max_length=30, blank=True) # Field name made lowercase.
    time_s1_finish = models.CharField(db_column='TIME_S1_FINISH', max_length=30, blank=True) # Field name made lowercase.
    time_s2_start = models.CharField(db_column='TIME_S2_START', max_length=30, blank=True) # Field name made lowercase.
    time_s2_finish = models.CharField(db_column='TIME_S2_FINISH', max_length=30, blank=True) # Field name made lowercase.
    result_status = models.CharField(db_column='RESULT_STATUS', max_length=20, blank=True) # Field name made lowercase.
    
    def __unicode__(self):
        return self.rpc_name
    
    class Meta:
        managed = False
        db_table = 'RPC'
        
class SOAP(models.Model):
    soap_id = models.IntegerField(db_column='SOAP_ID', primary_key=True) # Field name made lowercase.
    rpc_id = models.IntegerField(db_column='RPC_ID', blank=True, null=True) # Field name made lowercase.
    msg_type = models.CharField(db_column='MSG_TYPE', max_length=50, blank=True) # Field name made lowercase.
    time_exec = models.CharField(db_column='TIME_EXEC', max_length=30, blank=True) # Field name made lowercase.
    direction = models.CharField(db_column='DIRECTION', max_length=4, blank=True) # Field name made lowercase.
    cpe_id = models.IntegerField(db_column='CPE_ID', blank=True, null=True) # Field name made lowercase.
    sn = models.CharField(db_column='SN', max_length=70, blank=True) # Field name made lowercase.
    event_code = models.CharField(db_column='EVENT_CODE', max_length=50, blank=True) # Field name made lowercase.
    
    def __unicode__(self):
        return self.msg_type
    
    class Meta:
        managed = False
        db_table = 'SOAP'

class SoapEx(models.Model):
    soap_id = models.IntegerField(db_column='SOAP_ID', primary_key=True) # Field name made lowercase.
    content_head = models.TextField(db_column='CONTENT_HEAD', blank=True) # Field name made lowercase.
    head_ex = models.TextField(db_column='HEAD_EX', blank=True) # Field name made lowercase.
    content_body = models.TextField(db_column='CONTENT_BODY', blank=True) # Field name made lowercase.
    
    def __unicode__(self):
        return self.soap_id
    
    class Meta:
        managed = False
        db_table = 'SOAP_EX'
        
class Worklist(models.Model):
    worklist_id = models.IntegerField(db_column='WORKLIST_ID', primary_key=True) # Field name made lowercase.
    worklist_desc = models.CharField(db_column='WORKLIST_DESC', unique=True, max_length=50, blank=True) # Field name made lowercase.
    worklist_type = models.CharField(db_column='WORKLIST_TYPE', max_length=10, blank=True) # Field name made lowercase.
    worklist_name = models.CharField(db_column='WORKLIST_NAME', max_length=50, blank=True) # Field name made lowercase.
    #args = models.TextField(db_column='ARGS', blank=True) # Field name made lowercase.
    status = models.CharField(db_column='STATUS', max_length=20, blank=True) # Field name made lowercase.
    cpe_id = models.IntegerField(db_column='CPE_ID', blank=True, null=True) # Field name made lowercase.
    operator = models.CharField(db_column='OPERATOR', max_length=50, blank=True) # Field name made lowercase.
    operator_version = models.CharField(db_column='OPERATOR_VERSION', max_length=50, blank=True) # Field name made lowercase.
    domain = models.CharField(db_column='DOMAIN', max_length=50, blank=True) # Field name made lowercase.
    sn = models.CharField(db_column='SN', max_length=70, blank=True) # Field name made lowercase.
    username = models.CharField(db_column='USER_NAME', max_length=30, blank=True) # Field name made lowercase.
    password = models.CharField(db_column='USER_ID', max_length=30, blank=True) # Field name made lowercase.
    rollback = models.CharField(db_column='ROLLBACK', max_length=10, blank=True) # Field name made lowercase.
    time_init = models.CharField(db_column='TIME_INIT', max_length=30, blank=True) # Field name made lowercase.
    time_bind = models.CharField(db_column='TIME_BIND', max_length=30, blank=True) # Field name made lowercase.
    time_reserve = models.CharField(db_column='TIME_RESERVE', max_length=30, blank=True) # Field name made lowercase.
    time_exec_start = models.CharField(db_column='TIME_EXEC_START', max_length=30, blank=True) # Field name made lowercase.
    time_exec_finish = models.CharField(db_column='TIME_EXEC_FINISH', max_length=30, blank=True) # Field name made lowercase.
    worklist_group = models.CharField(db_column='WORKLIST_GROUP', max_length=10, blank=True) # Field name made lowercase.
    
    def __unicode__(self):
        return '%s, %s, %s' % (self.worklist_id, self.worklist_name, self.sn)
    
    class Meta:
        managed = False
        db_table = 'WORKLIST'
        
class WorklistEx(models.Model):
    worklist_id = models.IntegerField(db_column='WORKLIST_ID', primary_key=True) # Field name made lowercase.
    parameters = models.TextField(db_column='PARAMETERS', blank=True) # Field name made lowercase.
    result = models.TextField(db_column='RESULT', blank=True) # Field name made lowercase.
    
    def __unicode__(self):
        return self.worklist_id
    
    class Meta:
        managed = False
        db_table = 'WORKLIST_EX'

