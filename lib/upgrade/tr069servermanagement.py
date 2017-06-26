#coding:utf-8

# sys
import  os
import  sys
import  inspect
import  shutil
import  subprocess
import  time
import  re
#import  pythoncom

import  servermangementcfg
from   versionmanagement  import Versionmanagement

import  psutil

LIB_NAME = "TR069Server"
START_TIME = 10  #启动时间 10秒

def debug_output(message):
    """
    输出打印信息
    """
    cur_path = os.path.dirname(__file__)
    log_path = os.path.join(cur_path, "log")
    if not os.path.exists(log_path):
        os.mkdir(log_path, 0777)
        
    log_file = os.path.join(log_path, "tr069server_upgrade_log.txt")
    
    string = time.strftime('%Y-%m-%d %H:%M:%S ') + message + '\n'
    if isinstance(string, unicode):
        string = string.encode('utf-8')
    
    with open(log_file,'a+') as item :
            item.seek(os.SEEK_END )
            item.write(string)
    # 仅在调试时开启
    #print string

class Tr069servermanagement():
    """
    """
    
    def __init__(self):
        """
        """
        self.cur_work_path = servermangementcfg.TR069_WORK_PATH  #默认配置的目录
        self.cur_ver = ""
        self.download_path = servermangementcfg.TR069_DOWNLOAD_SAVE_PATH  #默认配置的下载包存放版本
        self.download_unpack_path = os.path.join(self.download_path, "unpack", LIB_NAME)
        
        #pythoncom.CoInitialize()
       
    def __del__(self):
        #pythoncom.CoUninitialize()
        pass
        
    def get_server_state(self):
        """
        获取当前服务的状态 true 启动 false未 启动
        """
        state = False        
        src = u""
    
        tr069s = [  "start_acs.py",         "start_acs.pyc", 
                    "start_agent.py",       "start_agent.pyc", 
                    "start_worklist.py",    "start_worklist.pyc"]
        
        process_list = psutil.get_process_list()
        for process in process_list:
            
            if (len(process.cmdline) == 2):
                
                # is python.exe?
                if (os.path.basename(process.cmdline[0]) != "python.exe"):
                    continue
                    
                # start_acs.py? 
                file_name = os.path.basename(process.cmdline[1])
                if (file_name in tr069s):
                    #当前工作目录
                    src = os.path.dirname(process.cmdline[1])
                    self._set_work_path(src)
                    #
                    state = True
                    break
                
        if state:
            debug_output( u"get_server_state:server is active" )
        else:
            debug_output( u"get_server_state:server is inactive.")
            
        return state
    
    def _set_work_path(self, src):
        """
        修改配置、修改变量 ？？
        """
        if  src != self.cur_work_path :
            #todo
            self.cur_work_path = src
    
    def get_cur_ver(self, selfcallflg=False):
        """
        获取当前版本
        selfcallflg true 表示是自调用
        """        
        ver = u"不存在版本"
        
        debug_output( u"get_cur_ver: cur_path=%s."%self.cur_work_path)
        
        if os.path.exists(self.cur_work_path):            
        
            try:        
                sys.path.insert(0, self.cur_work_path)
                import testlibversion
                reload(testlibversion)
                
                if self.cur_work_path == os.path.dirname(testlibversion.__file__):
                    ver = testlibversion.VERSION
                else:
                    ver = u"获取版本失败"
        
            except Exception, e:
                self._print_trace(e)
                ver = u"获取版本异常"
        else:
            
            if selfcallflg:
                #自调用（查到启动了服务，但是self.cur_work_path还是不存在）
                debug_output( u"cur_path文件不存在，获取版本失败")
            else:
                #当前目录不存在
                #看是否在其他目录启动
                if self.get_server_state():
                    #若启动了 self.cur_work_path 会被修改为正在运行的TR069Server的目录（get_server_state中）
                    ver = self.get_cur_ver(True)
                else:
                    #未启动
                    debug_output( u"cur_path文件不存在，且在本机也没有发现正在运行的TR069Server服务。")
                
        self.cur_ver = ver
        debug_output( u"get_cur_ver: %s."%ver)
        return ver
    
    
    def start_server(self):
        """
        """
        
        new_path = self.download_unpack_path
        
        if os.path.isdir(new_path):
            if os.listdir(new_path): #目录不为空 20140708        
        
                #update data
                self._update_config_data(new_path)
                
                #copy
                self._copy_new_ver(new_path)
                
                self._rm_folder(new_path)        
            
        debug_output( u"start_tr069 ----------- "    )
    
        path = self.cur_work_path
        
        for nwf in [1]:
    
            # acs ------------------------------------------------
            start_path = os.path.join(path, "start_acs.py")
            if (not os.path.isfile(start_path)):
                start_path = os.path.join(path, "start_acs.pyc")
            if (not os.path.isfile(start_path)):
                debug_output( u"start_tr069 fail, neither find start_acs.py nor start_acs.pyc.")
                break
            
            cmd = u'start "%s" "%s"' % ("python.exe", start_path)
            subprocess.Popen(cmd, shell = True)    
    
            # agent
            start_path = os.path.join(path, "start_agent.py")
            if (not os.path.isfile(start_path)):
                start_path = os.path.join(path, "start_agent.pyc")
            if (not os.path.isfile(start_path)):             
                debug_output( u"start_tr069 fail, neither find start_agent.py nor start_agent.pyc.")
                break
                
            cmd = u'start "%s" "%s"' % ("python.exe", start_path)
            subprocess.Popen(cmd, shell = True)
    
            # worklist
            start_path = os.path.join(path, "start_worklist.py")
            if (not os.path.isfile(start_path)):
                start_path = os.path.join(path, "start_worklist.pyc")
            if (not os.path.isfile(start_path)):                
                debug_output( u"start_tr069 fail, neither find start_worklist.py nor start_worklist.pyc.")
                break
                
            cmd = u'start "%s" "%s"' % ("python.exe", start_path)
            subprocess.Popen(cmd, shell = True)
        
        ret = False            
        for i in range(START_TIME):
            time.sleep(1)
            state = self.get_server_state()
            if state:
                ret = True
                break                
           
        return ret        

    def stop_server(self):
        """
        """
        debug_output( u"stop_tr069 ----------- "  )
        
        tr069s = ["start_acs.py", "start_acs.pyc", 
                   "start_agent.py",  "start_agent.pyc", 
                   "start_worklist.py", "start_worklist.pyc"]
        
        process_list = psutil.get_process_list()
        for process in process_list:
    
            pid = process.pid
            if (len(process.cmdline) == 2):
                
                # is python.exe?
                if (os.path.basename(process.cmdline[0]) != "python.exe"):
                    continue
                    
                # start_acs.py? 
                file_name = os.path.basename(process.cmdline[1])
                if (file_name in  tr069s) :
    
                    cmd = "taskkill /F /pid %s" %pid 
                    os.system(cmd)
                    
        ret = False            
        for i in range(START_TIME):
            time.sleep(1)
            state = self.get_server_state()
            if not state:
                ret = True
                break                
           
        return ret    
        
    def get_useable_vers(self):
        """
        """
        vers = []
        
        #test
        #self.cur_ver = "v.be6ta140102.svn2520"
        
        vmgt = Versionmanagement()
        vers = vmgt.query_usable_versions(LIB_NAME, self.cur_ver)      
        
        debug_output( u"get_useable_vers: %s."%str(vers))
        return vers
    
    def get_last_ver(self):
        """
        """
        ver = ""
        vmgt = Versionmanagement()
        ver = vmgt.get_last_version(LIB_NAME, self.cur_ver)
        
        debug_output( u"get_last_ver: %s."%str(ver))
        return ver
    
        
    def need_upgrade(self, new_ver=None):
        """
        """
        ret = False
        if not new_ver:
            new_ver = self.get_last_ver()
        
        if not new_ver:
            return ret            
        
        ret =  True if (new_ver != self.cur_ver) else False
        
        debug_output( u"need_upgrade: %s."%str(ret))
        
        return ret
       
        
    def download_ver(self, new_ver= None):
        """
        """
        ret = False
        #指定版本 或者最新版本
        if not new_ver:
            new_ver = self.get_last_ver()
            if not new_ver :
                return ret
        
        #清空原来的文件
        try: 
            
            path = self.download_path
            self._recreate_filder(path)
            
            path = self.download_unpack_path
            self._recreate_filder(path)
                
        except Exception,e:
            self._print_trace(e)
            
        #下载        
        debug_output( u"download_pack(%s_%s)." %(LIB_NAME, new_ver))
        vmgt = Versionmanagement()
        vmgt.download_pack(LIB_NAME, new_ver, self.download_path)
        
        #解压
        zip_path = os.path.join(self.download_path, LIB_NAME + "_" + new_ver + ".zip")
        
        unzip_path = self.download_unpack_path
        debug_output( u"unzip_folder(%s)." %zip_path)
        vmgt.unzip_pack(zip_path, unzip_path)
        
        ret = True
        
        return ret         
        
    def _update_config_data(self, unzip_path):
        """
        """
        ret = False
          
        debug_output( u"update_config_data...")
        #old
        local_path = os.path.join(self.cur_work_path, "TR069")
        local_path = os.path.join(local_path, "data")
        
        if not  os.path.isdir(local_path):
            #之前版本没有 不用更新data
            return True
    
        #new
        download_path = os.path.join(unzip_path, "TR069")
        download_path = os.path.join(download_path, "data")
        
        try:
            os.chmod(local_path, 0777)
            os.chmod(download_path, 0777)            
            
            #原data目录local_path下的 .cfg文件，不需要更新
            #需要copy到download_path
            self._copy_dir(local_path, download_path)
            
            ret = True
            
        except Exception, e:
            self._print_trace(e)
            ret = False
            
        return ret
    
    def _copy_new_ver(self, new_path):
        """
        """
        ret = False
           
        local_save = self.cur_work_path        
        
        #copy    
        if os.path.isdir(new_path):
            if os.listdir(new_path): #目录不为空 20140708   
                #clear            
                self._rm_folder(local_save)
                
                debug_output( u"copytree  %s to %s" % (new_path, local_save))
                
                shutil.copytree(new_path, local_save)
                ret = True
              
        return ret
       
    def _copy_file(self, src, dst):
        """
        dst  为下载目录的文件
        """        
         
        if os.path.isfile(dst):
            #新目录存在该文件 
            dirname, filename = os.path.split(dst)
            if (filename.lower()).find(".cfg") != -1:
                #是配置文件
                debug_output( u"配置文件 %s 不更新"%filename)
                os.remove(dst)
                shutil.copy2(src, dst)
                #todo  后面需要考虑配置文件局部更新
    
    def _copy_dir(self, src, dst):
        """
        """
        for filename in os.listdir(src):
            
            file_path = os.path.join(src, filename)
            save_path = os.path.join(dst, filename)
            
            if os.path.isdir(file_path):
                
                self._copy_dir(file_path, save_path)                
            elif os.path.isfile(file_path):
                
                self._copy_file(file_path, save_path)
            else:
                pass
     
    def upgrade(self, new_ver=None):
        """
        isrunning 当前状态
        new_ver 需要升级的版本 默认服务器上的最新版本
        """
        ret = False
        
        debug_output( u"upgrade  start---")
        try:
            isrunning = self.get_server_state()
            
            #try:
            if not self.need_upgrade(new_ver):
                return ret
            #下载和解压
            self.download_ver(new_ver)
            
            #停止
            if isrunning:
                self.stop_server()
            
            #启动            
            if isrunning:
                self.start_server()
                
            ret = True
            
        except Exception,e:
            self._print_trace(e)
        debug_output( u"upgrade  end---")
        return ret

    def _rm_folder(self, folder_path):
        """
        删除
        """    
        if os.path.isdir(folder_path):       
            debug_output( u"delete old folder_path=%s" %folder_path)
            shutil.rmtree(folder_path)
            time.sleep(0.5)
            
    def _recreate_filder(self, folder_path):
        """
        重建
        """
        if os.path.isdir(folder_path):      
            debug_output( u"delete old folder_path=%s" %folder_path)
            shutil.rmtree(folder_path)
            time.sleep(0.5)
            
          
        debug_output( u"make folder_path=%s" %folder_path)
        os.makedirs(folder_path)
        time.sleep(0.5)
            
    
    def _print_trace(self, e):
        """
        e[1]=str, module
        e[2]=int, line no        
        e[3]=str, func name
        e[4]=list code
        """
        traces = inspect.trace()
        lasttrace = traces[len(traces)-1]
        e = u"Exception:\n\tmodule=%s,\n\tlineno=%s,\n\tfunction=%s,\n\tcode=%s,\n\tdesc=%s" \
            %(lasttrace[1], lasttrace[2], lasttrace[3], lasttrace[4], e)
        debug_output(e)


# -------------------------------------
# global
#g_TR069_server_control = Tr069servermanagement()

if __name__ == '__main__':
    
    import time
    a = Tr069servermanagement()
    print a.get_cur_ver()
    
    
    print a.download_ver(ver)
    
    
    """ 
    #a.unzip_pack("D:\\5\\TR069Server_v.beta140624.svn3183.zip", "D:\\5\\unpack")
    
    #state = a.get_server_state()
    
    #a.upgrade(state, "v.beta140624.svn3183")
    a.stop_server()    
    time.sleep(4)    
    a.get_server_state()    
    a.start_server()    
    time.sleep(4)    
    a.get_server_state()
    """


