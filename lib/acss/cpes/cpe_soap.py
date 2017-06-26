#coding:utf-8

# ***************************************************************************
#
#  nwf      2012-08-13      V1.0
#  nwf      2013-05-24      refactor(unify)
#  nwf      2013-06-20      cpe split to (property + soap + user)
#  nwf      2013-06-26      support 2 session one cpe
# ***************************************************************************


# sys lib
import  sys
import  os

# user lib
import  TR069.lib.common.logs.log   as      log 
from    cpe_db                      import  *


class CpeSoap(object):
    """
    """        

    def __init__(self, cpe):
        """
        
        """

        self.cpe                    = cpe
        
        self.cwmp_id                = None          # soap(response) use    
        self.cwmp_version           = "cwmp-1-0"    #(inform , v1);
        self.soap_inform_timeout    = 60        # 240=60(fixed)+180(dynamic); =60

        self.soap_inform            = None
        self.soap_message           = None      # (inform postnull rpc)       
        self.soap_sessionno         = None      # inform  session number    
        self.soap_verify            = None      # soap obj(infrom ;rpc rsp; Fault)

        self.last_faults            = []        # [(code1, desc1), (code2, desc2)]
        
        # Add by lizn 2014-03-10
        self.time_s1_start          = ''
        self.time_s1_finish         = ''
        self.time_s2_start          = ''
        self.time_s2_finish         = ''
        self.time_last_contact      = ''

    #  --------------------------------------------------------------------    
    def set_cwmpid(self, cwmp_id):
        old = self.get_cwmpid()
        self.cwmp_id = cwmp_id  
        
    def get_cwmpid(self):
        return self.cwmp_id
    
    def show_log(self, field_name, old_value, new_value):
        sn = self.cpe.get_sn()
        cpe_id = self.cpe.get_cpe_id()
        log.app_info("cpe([%s]sn=%s), %s update(%s->%s)" % (cpe_id, sn, field_name, old_value, new_value))
    
    def is_update_cwmp_version(self, version):
        if self.cwmp_version == version:
            return False
        
        self.show_log('cwmp_version', self.cwmp_version, version)
        self.cwmp_version = version
        return True
    
    def is_update_contact_time(self, value):
        if self.time_last_contact == value:
            return False
        
        self.show_log('contact_time', self.time_last_contact, value)
        self.time_last_contact = value
        return True
    
    def is_update_inform_timeout(self, value):
        try:
            timeout = int(timeout)
        except Exception,e:
            timeout = 60 # mysql is None
        
        if self.soap_inform_timeout == value:
            return False
        
        self.show_log('inform_timeout', self.soap_inform_timeout, value)
        self.soap_inform_timeout = value
        return True
        
    def set_cwmpversion(self, cwmp_version):            
        old = self.get_cwmpversion()
        if (old != cwmp_version):
            sn = self.cpe.get_sn()
            cpe_id = self.cpe.get_cpe_id()
            self.cwmp_version = cwmp_version
            log.app_info("cpe([%s]sn=%s), cwmp version update(%s->%s)" 
                            %(cpe_id, sn, old, cwmp_version))
            # mysql
            update_acs_cpe_new(cpe_id, "CWMP_VERSION", cwmp_version)
        
    def get_cwmpversion(self):
        return self.cwmp_version  

    
    def set_soap_inform_timeout(self, timeout): 

        try:
            timeout = int(timeout)
        except Exception,e:
            timeout = 60 # mysql is None
            
        old = self.get_soap_inform_timeout()
        if (timeout != old):
            sn = self.cpe.get_sn()
            cpe_id = self.cpe.get_cpe_id()
            self.soap_inform_timeout = timeout
            log.app_info("cpe([%s]sn=%s), max wait cpe inform timeout update(%s->%s)" 
                            %(cpe_id, sn, 
                            old, timeout))    
            # mysql
            update_acs_cpe_new(cpe_id, "SOAP_INFORM_TIMEOUT", timeout)
            
    def get_soap_inform_timeout(self):
        return self.soap_inform_timeout   

                
    def set_soap_sessionno(self, soap_sessionno):
        old = self.get_soap_sessionno()             
        if (soap_sessionno != old):       
            self.soap_sessionno = soap_sessionno   
            log.app_info("cpe(sn=%s), soap sessionno update.(%s->%s)" 
                        %(self.cpe.get_sn(), old, soap_sessionno))         
                        
    def get_soap_sessionno(self):
        return self.soap_sessionno

    def set_soap_msg(self, soap_message):
        old = self.get_soap_msg()           
        if (soap_message != old):
            self.soap_message = soap_message
            log.app_info("cpe(sn=%s), soap message update(%s->%s)" 
                            %(self.cpe.get_sn(), old, soap_message))                              
    def get_soap_msg(self):
        return self.soap_message          


    def set_soap_inform(self, soap_inform):
        self.soap_inform = soap_inform
    def get_soap_inform(self):
        return self.soap_inform        
       
    def set_soap_verify(self, soap_verify):        
        self.soap_verify = soap_verify             
    def get_soap_verify(self):
        return self.soap_verify     
                
    def set_last_faults(self, fault_soap):
        """
        """
        last_faults = []

        try:

            if (fault_soap):
                detail = fault_soap.result.detail
                elem = (detail.FaultCode, detail.FaultString)
                last_faults.append(elem)

                if (hasattr(detail, "SetParameterValuesFaultList")):
                    fault_list = detail.SetParameterValuesFaultList
                    for fault in fault_list:
                        elem = (fault.FaultCode, fault.FaultString)
                        last_faults.append(elem) 
                    
        except Exception,e:        
            log.app_info(str(e))
    
        self.last_faults = last_faults   
        
    def get_last_faults(self):
        return self.last_faults 
        


if __name__ == '__main__':
    pass
 
