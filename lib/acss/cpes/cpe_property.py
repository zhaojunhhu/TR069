#coding:utf-8

# ***************************************************************************
#
#  nwf      2012-08-13      V1.0
#  nwf      2013-05-24      refactor(unify)
#  nwf      2013-06-20      cpe split to (property + soap + user)
# ***************************************************************************


# sys lib
import  sys
import  os


# user lib
import  TR069.lib.common.logs.log   as      log 
from    cpe_db                      import  *


class CpeProperty(object):
    """
    """        
    
    def __init__(self, cpe):
        """
        
        """
        self.cpe                    = cpe
        self.lastonlinetime         = None  #  schedule        

        self.cpe_request            = None  # acs may close cpe session
        self.cpe_isauth             = False              
        self.cpe_authtype           = "digest"      # "None"  "digest"(default)
        self.cpe_operator           = "standard"     # CT or CU or "standard"
        self.cpe_domain             = None      # adsl lan epon          
        self.cpe2acs_loginname      = None      # cpe's login name to enter acs's url
        self.cpe2acs_loginpassword  = None   
        self.cpe_timer              = None      # cpe's interaction timer
        self.worklist_timer         = None      # worklist status timer
        self.cpe_worklist_rollback  = False     
        self.cpe_status             = "offline" # online or offline; eg period = 24hour, not real
        
        self.software_version       = ''
        self.hardware_version       = ''
        self.root_node              = ''

        # acs's
        self.acs2cpe_loginname      = None  # acs's login name to enter cpe's url
        self.acs2cpe_loginpassword  = None  
        self.acs2cpe_url            = None  # connection request url  

        # CT-COM_InterfaceVersion
        self.cpe_interface_version  = "AUTO"    # V4 V3 Auto
        self.cpe_worklist_rollback  = "False"
 

    def set_onlinetime(self, lastonlinetime):
        self.lastonlinetime = lastonlinetime                                                              
    def get_onlinetime(self):
        return self.lastonlinetime                                                                      

     
    def set_cpe_request(self, cpe_request):
        self.cpe_request = cpe_request                
    def get_cpe_request(self):
        return self.cpe_request
    
    def show_log(self, field_name, old_value, new_value):
        sn = self.cpe.get_sn()
        cpe_id = self.cpe.get_cpe_id()
        log.app_info("cpe([%s]sn=%s), %s update(%s->%s)" % (cpe_id, sn, field_name, old_value, new_value))
    
    def is_update_acs2cpe_url(self, url):
        if self.acs2cpe_url == url:
            return False
        
        self.show_log('acs2cpe_url', self.acs2cpe_url, url)
        self.acs2cpe_url = url
        return True
    
    def is_update_software_version(self, version):
        if self.software_version == version:
            return False
        
        self.show_log('software_version', self.software_version, version)
        self.software_version = version
        return True
    
    def is_update_hardware_version(self, version):
        if self.hardware_version == version:
            return False
        
        self.show_log('hardware_version', self.hardware_version, version)
        self.hardware_version = version
        return True
    
    def is_update_root_node(self, value):
        if self.root_node == value:
            return False
        
        self.show_log('root_node', self.root_node, value)
        self.root_node = value
        return True
    
    def is_update_acs2cpe_name(self, value):
        if self.acs2cpe_loginname == value:
            return False
        
        self.show_log('acs2cpe_name', self.acs2cpe_loginname, value)
        self.acs2cpe_loginname = value
        return True
    
    def is_update_acs2cpe_password(self, value):
        if self.acs2cpe_loginpassword == value:
            return False
        
        self.show_log('acs2cpe_password', self.acs2cpe_loginpassword, value)
        self.acs2cpe_loginpassword = value
        return True
    
    def is_update_cpe2acs_name(self, value):
        if self.cpe2acs_loginname == value:
            return False
        
        self.show_log('cpe2acs_name', self.cpe2acs_loginname, value)
        self.cpe2acs_loginname = value
        return True
    
    def is_update_cpe2acs_password(self, value):
        if self.cpe2acs_loginpassword == value:
            return False
        
        self.show_log('cpe2acs_password', self.cpe2acs_loginpassword, value)
        self.cpe2acs_loginpassword = value
        return True
    
    def is_update_auth_type(self, value):
        if self.cpe_authtype == value:
            return False
        
        self.show_log('auth_type', self.cpe_authtype, value)
        self.cpe_authtype = value
        return True
    
    def is_update_domain(self, value):
        if self.cpe_domain == value:
            return False
        
        self.show_log('cpe_domain', self.cpe_domain, value)
        self.cpe_domain = value
        return True
    
    def is_update_operator(self, value):
        if self.cpe_operator == value:
            return False
        
        self.show_log('cpe_operator', self.cpe_operator, value)
        self.cpe_operator = value
        return True

    def is_update_worklist_rollback(self, value):
        if self.cpe_worklist_rollback == value:
            return False
        
        self.show_log('cpe_worklist_rollback', self.cpe_worklist_rollback, value)
        self.cpe_worklist_rollback = value
        return True
    
    def is_update_interface_version(self, value):
        if self.cpe_interface_version == value:
            return False
        
        self.show_log('cpe_interface_version', self.cpe_interface_version, value)
        self.cpe_interface_version = value
        return True

    def set_cpe_authtype(self, cpe_authtype):
        old = self.get_cpe_authtype()
        if (cpe_authtype != old):
            sn = self.cpe.get_sn()
            cpe_id = self.cpe.get_cpe_id()
            self.cpe_authtype = cpe_authtype
            log.app_info("cpe([%s]sn=%s),cpe authtype update(%s->%s)" 
                            %(cpe_id, sn, 
                            old, cpe_authtype)) 
            # mysql
            update_acs_cpe_new(cpe_id, "AUTH_TYPE", cpe_authtype)
        
    def get_cpe_authtype(self):
        return self.cpe_authtype 


    def set_cpe_operator(self, cpe_operator):            
        old = self.get_cpe_operator()
        if (cpe_operator != old):    
            sn = self.cpe.get_sn()
            cpe_id = self.cpe.get_cpe_id()
            self.cpe_operator = cpe_operator
            log.app_info("cpe([%s]sn=%s),cpe operator update(%s->%s)" 
                            %(cpe_id, sn, 
                            old, cpe_operator))  
            # mysql
            update_acs_cpe_new(cpe_id, "CPE_OPERATOR", cpe_operator)
                            
    def get_cpe_operator(self):
        return self.cpe_operator 

    def set_cpe_domain(self, cpe_domain):            
        old = self.get_cpe_domain()
        if (cpe_domain != old): 
            sn = self.cpe.get_sn()
            cpe_id = self.cpe.get_cpe_id()
            self.cpe_domain = cpe_domain
            log.app_info("cpe([%s]sn=%s),cpe domain update(%s->%s)" 
                            %(cpe_id, sn, 
                            old, cpe_domain)) 
            # mysql
            update_acs_cpe_new(cpe_id, "CPE_DEVICE_TYPE", cpe_domain)
            
    def get_cpe_domain(self):
        return self.cpe_domain 
    
        
    def set_cpe_isauth(self, cpe_isauth):
        old = self.get_cpe_isauth()
        if (cpe_isauth != old):
            self.cpe_isauth = cpe_isauth
            log.app_info("cpe(sn=%s),cpe isauth update(%s->%s)" 
                            %(self.cpe.get_sn(), 
                            old, cpe_isauth))                 
    def get_cpe_isauth(self):
        return self.cpe_isauth   

    def set_cpe_timer(self, timer):
        old = self.get_cpe_timer()
        self.cpe_timer = timer               
    def get_cpe_timer(self):
        return self.cpe_timer            

    def set_cpe2acs_loginname(self, cpe2acs_loginname):            
        old = self.get_cpe2acs_loginname()
        if (cpe2acs_loginname != old):
            sn = self.cpe.get_sn()
            cpe_id = self.cpe.get_cpe_id()
            self.cpe2acs_loginname = cpe2acs_loginname
            log.app_info("cpe([%s]sn=%s), cpe2acs loginname update(%s->%s)" 
                            %(cpe_id, sn, 
                            old, cpe2acs_loginname))   
            # mysql
            update_acs_cpe_new(cpe_id, "CPE2ACS_NAME", cpe2acs_loginname)
                            
    def get_cpe2acs_loginname(self):
        return self.cpe2acs_loginname   

    def set_cpe2acs_loginpassword(self, cpe2acs_loginpassword):            
        old = self.get_cpe2acs_loginpassword()
        if (cpe2acs_loginpassword != old):
            sn = self.cpe.get_sn()
            cpe_id = self.cpe.get_cpe_id()
            self.cpe2acs_loginpassword = cpe2acs_loginpassword
            log.app_info("cpe([%s]sn=%s), cpe loginpassword update(%s->%s)" 
                            %(cpe_id, sn, 
                            old, cpe2acs_loginpassword)) 
            # mysql
            update_acs_cpe_new(cpe_id, "CPE2ACS_PASSWORD", cpe2acs_loginpassword)
                            
    def get_cpe2acs_loginpassword(self):
        return self.cpe2acs_loginpassword  

    def set_cpe_worklist_rollback(self, cpe_worklist_rollback):            
        old = self.get_cpe_worklist_rollback()
        if (cpe_worklist_rollback != old):
            self.cpe_worklist_rollback = cpe_worklist_rollback
            log.app_info("cpe(sn=%s), cpe worklist_rollback update(%s->%s)" 
                            %(self.cpe.get_sn(), 
                            old, cpe_worklist_rollback))  
            # mysql
            cpe_id = self.cpe.get_cpe_id()
            update_acs_cpe_new(cpe_id, "CPE_WORKLIST_ROLLBACK", cpe_worklist_rollback)
            
    def get_cpe_worklist_rollback(self):
        return self.cpe_worklist_rollback  

    def set_cpe_status(self, cpe_status): 
        old = self.get_cpe_status()
        if (cpe_status != old):        
            self.cpe_status = cpe_status                                                             
    def get_cpe_status(self):
        return self.cpe_status  
   

    def set_cpe_interface_version(self, interface_version):            
        old = self.get_cpe_interface_version()
        if (interface_version != old):    
            sn = self.cpe.get_sn()
            self.cpe_interface_version = interface_version
            log.app_info("cpe(sn=%s),cpe interface_version update(%s->%s)" 
                            %(sn, 
                            old, interface_version))  
            # mysql
            cpe_id = self.cpe.get_cpe_id()
            update_acs_cpe_new(cpe_id, "INTERFACE_VERSION", interface_version)
            
    def get_cpe_interface_version(self):
        return self.cpe_interface_version 



    # ------------------------- acs -----------------------
    def set_acs2cpe_url(self, acs2cpe_url):
        old = self.get_acs2cpe_url()
        if (acs2cpe_url != old):
            sn = self.cpe.get_sn()
            cpe_id = self.cpe.get_cpe_id()
            self.acs2cpe_url = acs2cpe_url
            log.app_info("cpe([%s]sn=%s), acs2cpe_url update(%s->%s)" 
                            %(cpe_id, sn, 
                            old, acs2cpe_url))    
            # mysql
            update_acs_cpe_new(cpe_id, "CONN_RQST_URL", acs2cpe_url)
                            
    def get_acs2cpe_url(self):
        return self.acs2cpe_url  
        
    def set_acs2cpe_loginname(self, acs2cpe_loginname):            
        old = self.get_acs2cpe_loginname()
        if (acs2cpe_loginname != old):
            sn = self.cpe.get_sn()
            cpe_id = self.cpe.get_cpe_id()
            self.acs2cpe_loginname = acs2cpe_loginname
            log.app_info("cpe([%s]sn=%s), acs loginname update(%s->%s)" 
                            %(cpe_id, sn, 
                            old, acs2cpe_loginname))   
            # mysql
            update_acs_cpe_new(cpe_id, "ACS2CPE_NAME", acs2cpe_loginname)
                            
    def get_acs2cpe_loginname(self):
        return self.acs2cpe_loginname   

    def set_acs2cpe_loginpassword(self, acs2cpe_loginpassword):            
        old = self.get_acs2cpe_loginpassword()
        if (acs2cpe_loginpassword != old):
            sn = self.cpe.get_sn()
            cpe_id = self.cpe.get_cpe_id()
            self.acs2cpe_loginpassword = acs2cpe_loginpassword
            log.app_info("cpe([%s]sn=%s), acs loginpassword update(%s->%s)" 
                            %(cpe_id, sn, 
                            old, acs2cpe_loginpassword))  
            # mysql
            update_acs_cpe_new(cpe_id, "ACS2CPE_PASSWORD", acs2cpe_loginpassword)
                            
    def get_acs2cpe_loginpassword(self):
        return self.acs2cpe_loginpassword
        
            
if __name__ == '__main__':
    pass
 
