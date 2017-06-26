#coding:utf-8

"""
    nwf 2012-08-09  V1.0
                    1 evolve from TCL
    nwf 2013-06-13  V1.1
                    1 >64M, split a file to another file

"""


import  sys
import  os
import  codecs
import  warnings
from    datetime    import datetime, date, time


# user
from TR069.lib.common.error import *


#    
LEVEL_USER  = "UserInfo"     # testcase
LEVEL_APP   = "AppInfo"       # module
LEVEL_RUN   = "RunInfo"       #
LEVEL_DEBUG = "DebugWarn"   # develop
LIST_FILTER_LEVEL = [LEVEL_USER, LEVEL_APP, LEVEL_RUN, LEVEL_DEBUG]

#  
LEVEL_DEBUG_WARN    = "DebugWarn"
LEVEL_DEBUG_INFO    = "DebugInfo"
LEVEL_DEBUG_ERR     = "DebugErr"
LEVEL_RUN_INFO      = "RunInfo"
LEVEL_RUN_ERR       = "RunErr"
LEVEL_APP_INFO      = "AppInfo"
LEVEL_APP_ERR       = "AppErr"
LEVEL_USER_INFO     = "UserInfo"
LEVEL_USER_ERR      = "UserErr"


LIST_LOG_LEVEL = ["DebugWarn", "DebugInfo", "DebugErr",
                "RunInfo", "RunErr",
                "AppInfo", "AppErr",
                "UserInfo", "UserErr"]

class ATTLog:
    """
    Class for singleton log message 
    """    
    
    def __init__(self):
        """
        @param name: name of the file
        @param directory: directory holding the file        
        """        
        self.path           = ""        # 1 test entry path
        
        self.file_user      = None      # log file handle
        self.file_app       = None
        self.file_run       = None
        self.file_debug     = None
        self.file_log       = None      # all level logs content
        self.file_log_path  = ""        
        

    def start(self, name="att", directory=".",
                    level=LEVEL_APP, is_print=True):
        """
        init
        log entry
        """
        
        self.name = name # test dir name, eg 20120401175852_nwf
        # test dir, eg D:\___TCL\TestCenter\BCM4.12_Log\Log
        self.directory = directory  
        self.level = level        
        self.is_print = is_print      
        
        # nwf 20130911
        self.create_log_entry(directory)
        
        return self.create_testset_path()


    def start_only_1path_1file(self, name="att", file_name="all_SN", 
                                directory=".",
                                level=LEVEL_APP, is_print=True):
        """
        init
        log entry
        """
        
        self.name = name # test dir name, eg 20120401175852_nwf
        self.file_name = file_name
        # test dir, eg D:\___TCL\TestCenter\BCM4.12_Log\Log
        self.directory = directory  
        self.level = level        
        self.is_print = is_print      
        
        # nwf 20130911
        self.create_log_entry(directory)
        
        return self.create_testset_path_1file()  
        

    def start_only_1file(self, name="att", file_name="all_SN", 
                                directory=".",
                                level=LEVEL_APP, is_print=True):
        """
        init
        log entry
        """
        
        self.name = name # test dir name, eg 20120401175852_nwf
        self.file_name = file_name
        # test dir, eg D:\___TCL\TestCenter\BCM4.12_Log\Log
        self.directory = directory  
        self.level = level        
        self.is_print = is_print      
        
        # nwf 20130911
        self.create_log_entry(directory)
        
        return self.create_testset_1file() 


    def create_log_entry(self, dir_entry):
        """
        tr069v3_twisted\TR069\log missing?
        """
        try:
            if (not os.path.isdir(dir_entry)):                
                os.mkdir(dir_entry) 
        
        except Exception,e:
            print e
            

    def create_testset_path(self):
        """
        1 run 1 test path
        """
        n_ret = ERR_SUCCESS
        
        dt1 = datetime.now()
        # + time
        dir1 = "%d-%d-%d_%d-%d-%d" %(dt1.year, dt1.month, dt1.day,
                                    dt1.hour, dt1.minute, dt1.second)
        # + test name
        dir2 = "%s_%s" % (dir1, self.name)
        # 1 run 1 test path (level 1 dir)
        self.path = os.path.join(self.directory, dir2)        
        
        # 2 level dir
        try:
            os.mkdir(self.path)
            print "create log directory(%s) success." %self.path
            
            for level in LIST_FILTER_LEVEL:                
                os.mkdir(os.path.join(self.path, level))

        except Exception,e:
            print "create log directory fail, reason=%s.", e
            return ERR_FAIL
            
        # log.txt
        try:
            path                = os.path.join(self.path, "log.txt")            
            self.file_log       = open(path, "a+b")
            self.file_log_path  = path
        except Exception, e:
            print e
            return ERR_FAIL            
            
        return n_ret


    def create_testset_1file(self):
        """
        1 run 1 test path
        """
        n_ret = ERR_SUCCESS

        # E:\____python\tr069\TR069_BS2_nwf\TR069\log\2014-7-8_19-58-5_worklist
        self.path = self.directory
        
        # log.txt
        try:
            file_name = "%s.txt" %self.file_name
            path                = os.path.join(self.path, file_name)            
            self.file_log       = open(path, "a+b")
            self.file_log_path  = path
        except Exception, e:
            print e
            return ERR_FAIL            
            
        return n_ret


    def create_testset_path_1file(self):
        """
        1 run 1 test path
        """
        n_ret = ERR_SUCCESS
        
        dt1 = datetime.now()
        # + time
        dir1 = "%d-%d-%d_%d-%d-%d" %(dt1.year, dt1.month, dt1.day,
                                    dt1.hour, dt1.minute, dt1.second)
        # + test name
        dir2 = "%s_%s" % (dir1, self.name)
        # 1 run 1 test path (level 1 dir)
        self.path = os.path.join(self.directory, dir2)        
        
        # 2 level dir
        try:
            os.mkdir(self.path)
            print "create log directory(%s) success." %self.path            

        except Exception,e:
            print "create log directory fail, reason=%s.", e
            return ERR_FAIL
            
        # log.txt
        try:
            file_name = "%s.txt" %self.file_name
            path                = os.path.join(self.path, file_name)            
            self.file_log       = open(path, "a+b")
            self.file_log_path  = path
        except Exception, e:
            print e
            return ERR_FAIL            
            
        return n_ret        
        
    
    #  api -----------------------------------------------------------    
    def get_log_level(self):
        return self.level
    
    def set_log_level(self, level):
        """
        level={"UserInfo"  "AppInfo" "RunInfo" "DebugWarn"}
        """
        self.level = level
        
    def get_log_path(self):
        return self.path
    
    def set_log_path(self, path):
        self.path = path
        
    def get_print_screen(self):
        return self.is_print
    
    def set_print_screen(self, option):
        """
        option = {True False}
        """
        self.is_print = option           
    
    
    #  api ----------------------------------------------------------- 
    def need_log(self, filter_level, message_level):
        """
        @filter_level   file id level
        @message_level  current msg level
        可以这么理解 log级别设置得越低 表示越底层 越需要打印更多信息
        return = {True False}
        """
        n_ret = False    # default
        
        try:
            filter_level_index = LIST_LOG_LEVEL.index(filter_level)
            message_level_index = LIST_LOG_LEVEL.index(message_level)
            n_ret = (filter_level_index <= message_level_index)
        except Exception,e:            
            n_ret = True

        return n_ret
    
    
    def _get_head(self, message_level):
        """
        stacklevel =3 default
        """
        
        stacklevel = 3
        head = ""
                
        # copy warnings ; nwf 2012-08-14
        try:
            caller = sys._getframe(stacklevel)
        except ValueError:
            globals = sys.__dict__
            lineno = 1
        else:
            globals = caller.f_globals
            lineno = caller.f_lineno
            # nwf 2012-08-14
            f_code = caller.f_code
        if '__name__' in globals:
            module = globals['__name__']
        else:
            module = "<string>"
        filename = globals.get('__file__')
        if filename:
            fnl = filename.lower()
            if fnl.endswith((".pyc", ".pyo")):
                filename = filename[:-1]
        else:
            if module == "__main__":
                try:
                    filename = sys.argv[0]
                except AttributeError:
                    # embedded interpreters don't have sys.argv
                    filename = '__main__'
            if not filename:
                filename = module
        
        #
        filename = os.path.basename(filename)            
        
        dt1 = datetime.now()
        
        format = "[%d-%d-%d %d:%d:%d:%d] \
[%s] \
[%s] [%s:%d] [%s]:"
        # + time
        head = format %(dt1.year, dt1.month, dt1.day,
                        dt1.hour, dt1.minute, dt1.second, dt1.microsecond/1000,
                        message_level,
                        module, filename, lineno, f_code.co_name)                
        
        return head
    
    def get_file_id(self, level):
    
        file_id = self.file_debug  # default
        
        if (level == LEVEL_USER):
            file_id = self.file_user
        elif (level == LEVEL_APP):
            file_id = self.file_app
        elif(level == LEVEL_RUN):
            file_id = self.file_run
        
        return file_id
    
    def set_file_id(self, testcase_name="att"):    
        """
        rely on test case name, before start 1 testcase
        @testcase_name, next testcase    
        """        
        for filter_level in LIST_FILTER_LEVEL:
            file_name = os.path.join(self.get_log_path(), filter_level,
                                     ("%s.txt" %testcase_name))
            
            # nwf 2014-07-08; if not exist, no need(support 1 file)
            if (not os.path.exists(file_name)):
                continue

            f = open(file_name, "a+b")
            
            if (filter_level == LEVEL_USER):                    
                try:
                    self.file_user.close()
                except Exception, e:
                    pass                                       
                self.file_user = f                                
            elif (filter_level == LEVEL_APP):
                try:
                    self.file_app.close()
                except Exception, e:
                    pass                
                self.file_app = f                
            elif (filter_level == LEVEL_RUN):
                try:
                    self.file_run.close()
                except Exception, e:
                    pass                 
                self.file_run = f                
            elif (filter_level == LEVEL_DEBUG):
                try:
                    self.file_debug.close()
                except Exception, e:
                    pass                
                self.file_debug = f                     

       
    # api -----------------------------------------------------------
    def debug_warn(self, *args):
        """
        stacklevel=1  default
        """
        self._log(LEVEL_DEBUG_WARN, args)
        
    def debug_info(self, *args):
        self._log(LEVEL_DEBUG_INFO, args)
        
    def debug_err(self, *args):
        self._log(LEVEL_DEBUG_ERR, args)
        
    def run_info(self, *args):
        self._log(LEVEL_RUN_INFO, args)
        
    def run_err(self, *args):
        self._log(LEVEL_RUN_ERR, args)
        
    def app_info(self, *args):
        self._log(LEVEL_APP_INFO, args)
        
    def app_err(self, *args):
        self._log(LEVEL_APP_ERR, args)        
        
    def user_info(self, *args):
        self._log(LEVEL_USER_INFO, args)
        
    def user_err(self, *args):
        self._log(LEVEL_USER_ERR, args)        
        
    
    def _log(self, message_level, tuple_args):
        """
        stacklevel =2 default
        args
        """
        
        head = self._get_head(message_level)
        self.log_2_file(message_level, head, tuple_args)
        

    def _code(self, s):
        """
        get unicode ,s in [unicode, utf-8]
        """
        if isinstance(s, unicode): 
            s2 = s.encode("utf-8")  
        else: 
            s2 = s  # default utf-8

        return s2
    
    def _write_tuple(self, tuple_args, file):
        
        file.write("\r\n\t") # head \r\n\t body
        
        for arg in tuple_args:
            
            if (isinstance(arg, unicode)):
                arg2= self._code(arg)
            else :
                arg2 =str(arg)
            
            file.write(arg2)
            
            # blank
            file.write(" ")        
    
        file.write("\r\n")  # last line \r\n
        file.write("\r\n")  # current message \r\n
        file.flush()
            

    def log_2_file(self, message_level, head, tuple_args):
        """
        print to local file
        rely on set_file_id
        """
        try:
            # log.txt
            self.file_log.write(head)
            self._write_tuple(tuple_args, self.file_log)


            # nwf 2013-06-13; strategy, >64M, split
            len1 = os.path.getsize(self.file_log_path)
            # 67108864 = 64*1024*1024
            if (len1 > 67108864):
            
                dt1 = datetime.now()
                dir1 = "%d-%d-%d_%d-%d-%d" %(dt1.year, dt1.month, dt1.day,
                                            dt1.hour, dt1.minute, dt1.second)
                dir2 = "%s_%s" % (dir1, "log.txt")                                    
                path                = os.path.join(self.path, dir2)            
                self.file_log       = open(path, "a+b")
                self.file_log_path  = path                
            
                        
            # print to stdout?;  nwf 2012-03-06 
            if (self.get_print_screen()):
                if (self.need_log(self.level, message_level)):
                    print head
                    self._write_tuple(tuple_args, sys.stdout)

            # nwf 2013-06-13; acs log is big   
            if (0):
                for filter_level in LIST_FILTER_LEVEL:
                    file_id = self.get_file_id(filter_level)
                    if (self.need_log(filter_level, message_level)):
                        file_id.write(head)
                        self._write_tuple(tuple_args, file_id)
            
        except Exception, e:
            print e
        
        return


# singleton
try:
    g_att_log
except NameError:
    g_att_log       = ATTLog()
    # import api
    start           = g_att_log.start
    set_file_id     = g_att_log.set_file_id
    set_log_level   = g_att_log.set_log_level
    
    debug_warn  = g_att_log.debug_warn
    debug_info  = g_att_log.debug_info
    debug_err   = g_att_log.debug_err
    run_info    = g_att_log.run_info
    run_err     = g_att_log.run_err
    app_info    = g_att_log.app_info
    app_err     = g_att_log.app_err
    user_info   = g_att_log.user_info
    user_err    = g_att_log.user_err
    
    get_log_path = g_att_log.get_log_path
    start_only_1file = g_att_log.start_only_1file    
    start_only_1path_1file = g_att_log.start_only_1path_1file