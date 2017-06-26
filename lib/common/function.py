# -*- coding: utf-8 -*- 

import  traceback
import  os
import  sys
import  inspect
from    datetime                    import  datetime, timedelta
import  random
from    functools                   import  partial
from    threading                   import  Timer
import  uuid



from    TR069.lib.common.releasecfg       import  *   # log for tr069 self or RF?



# ------------------------------------- top level function  ----------
def print_trace(e):
    """
    e[1]=str, module
    e[2]=int, line no        
    e[3]=str, func name
    e[4]=list code
    """
    traces = inspect.trace()
    lasttrace = traces[len(traces)-1]
    e = "Exception:\n\tmodule=%s,\n\tlineno=%s,\n\tfunction=%s,\n\tcode=%s,\n\tdesc=%s" \
        %(lasttrace[1], lasttrace[2], lasttrace[3], lasttrace[4], e)
    log.debug_info(e)


def get_id(tag=""):
    """
    generated id, for message id/worklist id
    """
    id_ = ""

    dt1     = datetime.now()
    random1 = random.randrange(10000000, 100000000)
    id_     = "%s_%s_%s_%s" %(tag, dt1.date(), dt1.time(), random1)

    return id_

def create_id(tag=""):
    """
    generated id, for message id/worklist id
    """
    id_ = ""

    dt1     = datetime.now()
    random1 = random.randrange(10000000, 100000000)
    millisecond = str(dt1.microsecond)[0:3]
    id_     = "%s_%s.%s_%s" %(tag, dt1.strftime('%Y-%m-%d_%H:%M:%S'), millisecond, random1)

    return id_




# ------------------------------------- top level class  ----------


CHECK_ACS_MESSAGE_SEQUENCE_TIMEINTERVAL         = 1200      # 20min  

class UsersMsgSeq(object):
    """
    check user message seq;
    user mean client
    global, only 1
    """        

    m_dict_seq2msg      = dict()    # {seq:(time, str_dict_msg)}
    m_timer             = None

    def __init__(self):
        """
        
        """
        pass        

    @staticmethod
    def save_user_rsp_msg(seq, msg):
        dt1 = datetime.now()
        pair = (dt1, msg)
        
        UsersMsgSeq.m_dict_seq2msg.update({seq:pair})        

    @staticmethod    
    def is_user_message_seq_exist(seq):    
        """              
        """  
        ret = False
        msg = ""

        for nwf in [1]:
            pair = UsersMsgSeq.m_dict_seq2msg.get(seq)            
            if (pair):
                ret = True
                msg = pair[1]
                
                break
        
        return ret,msg        
       
        
    @staticmethod
    def on_check_acs_message_seq(interval=CHECK_ACS_MESSAGE_SEQUENCE_TIMEINTERVAL):
        """
        """
        
        ret = None

        on_check = partial(UsersMsgSeq.on_check_acs_message_seq, interval)
        t = Timer(interval, on_check)
        UsersMsgSeq.m_timer = t   
        
        t.start()  
            
        log.app_info("~~~~~~~~~~%s~~~~~~~~~~" %(interval))

        for seq,pair in UsersMsgSeq.m_dict_seq2msg.items():

            t2 = pair[0]
            msg = pair[1]
            
            if (datetime.now()-t2 >= timedelta(seconds=interval)):

                UsersMsgSeq.m_dict_seq2msg.pop(seq)                    


    @staticmethod
    def set_timer_check(timer):
        """
        """
        UsersMsgSeq.m_timer = timer

    @staticmethod
    def get_timer_check():
        """
        """
        return UsersMsgSeq.m_timer       

    @staticmethod
    def cancel_timer_check():
        """
        """
        timer = UsersMsgSeq.get_timer_check() 
        if (timer):
            try:
                timer.cancel()
            except Exception,e:
                pass
            


# -------------------------------------------------------
def _get_stable_ver_nums(ver_name):
    """
    ver_name = v2.3.0
    """
    ret         = False

    for nwf in [1]:
    
        index_v     = ver_name.find("v")
        if (index_v == -1):
            break  
            
        index_dot1  = ver_name.find(".", index_v+1)
        if (index_dot1 == -1):
            break  
            
        index_dot2  = ver_name.find(".", index_dot1+1)
        if (index_dot2 == -1):
            break              

        major = ver_name[index_v+1:index_dot1]
        minor = ver_name[index_dot1+1:index_dot2]
        revision = ver_name[index_dot2+1:]

        ret = True

    return ret, major, minor, revision
    

def find_stable_ver_name_max(ver_names):
    """
    ver_names = ["v2.3.0", "v2.3.1"]
    """
    num_max         = -1
    ver_name_max    = None
    majors          = []
    minors          = []
    revisions       = []

    majors2         = []
    minors2         = []
    revisions2      = []    

    majors3         = []
    minors3         = []
    revisions3      = []

    try:

        for ver_name in ver_names:
            # ver = v2.3.0
            ret, major, minor, revision = _get_stable_ver_nums(ver_name)
            if (not ret):
                continue
                
            majors.append(major)
            minors.append(minor)
            revisions.append(revision)
            
        # find max major
        major_max = max(majors)
        for i in range(len(majors)):
            if (majors[i] == major_max):
                majors2.append(majors[i])
                minors2.append(minors[i])
                revisions2.append(revisions[i])

        # find max minor
        minor_max = max(minors2)
        for i in range(len(minors2)):
            if (minors2[i] == minor_max):
                majors3.append(majors2[i])
                minors3.append(minors2[i])
                revisions3.append(revisions2[i])

        # find max revision
        revision_max = max(revisions3)

        ver_name_max = "v%s.%s.%s" %(majors3[0], minors3[0], revision_max)
        
    except Exception,e:
        print e
        
    return ver_name_max



def find_beta_ver_name_by_max_svn(ver_names):
    """
    ver_value = v.beta131021.svn1766
    """   
    num_max         = -1
    ver_name_max    = None

    for ver_name in ver_names:
        # ver = v.beta131021.svn1766
        index = ver_name.find("svn")
        if (index == -1):
            continue
            
        num = ver_name[index+len("svn"):]
        num = int(num)
        if (num > num_max):
            num_max = num
            ver_name_max = ver_name
        
    return ver_name_max


def beta_server_version_less_than_lib(local_ver, download_ver):
    """
    local_ver = v.beta131021.svn1719
    download_ver = v.beta131021.svn1729
    """
    ret = False

    for nwf in [1]:
        
        index1 = local_ver.find("svn")
        if (index1 == -1):
            break
        num_local = local_ver[index1+len("svn"):]
        num_local = int(num_local)

        index2 = download_ver.find("svn")
        if (index2 == -1):
            break
        num_download = download_ver[index2+len("svn"):]
        num_download = int(num_download)   

        if (num_local < num_download):
            ret = True
            
    return ret


def stable_server_version_less_than_lib(local_ver, download_ver):
    """
    local_ver = v3.2.0
    download_ver = v2.3.1
    """
    ret     = False
    ret_api = False

    for nwf in [1]:
        
        # ver = v2.3.0
        ret_api, major_local, minor_local, revision_local = _get_stable_ver_nums(local_ver)
        if (not ret_api):
            break

        # ver = v2.3.0
        ret_api, major_download, minor_download, revision_download = _get_stable_ver_nums(download_ver)
        if (not ret_api):
            break

        # major first
        if (major_local < major_download ):
            ret = True
            break
        elif (major_local > major_download):
            break

        # minor second
        if (minor_local < minor_download):
            ret = True
            break
        elif (minor_local > minor_download):
            break

        # revision last
        if (revision_local < revision_download):
            ret = True
            break
        elif (revision_local > revision_download):
            break                            
            
    return ret


def is_beta_version(ver_value):
    """
    is beta?
    """
    ret = False
    
    if (ver_value.find("beta") != -1):
        ret = True

    return ret



if __name__ == '__main__':
    pass
