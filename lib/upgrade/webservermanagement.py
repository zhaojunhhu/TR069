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

LIB_NAME = "TR069WebServer"
RENAME_HEAD = "__disabled__"

def debug_output(message):
    """
    输出打印信息
    """
    cur_path = os.path.dirname(__file__)
    log_path = os.path.join(cur_path, "log")
    if not os.path.exists(log_path):
        os.mkdir(log_path, 0777)
        
    log_file = os.path.join(log_path, "webserver_upgrade_log.txt")
    
    string = time.strftime('%Y-%m-%d %H:%M:%S ') + message + '\n'
    if isinstance(string, unicode):
        string = string.encode('utf-8')
    
    with open(log_file,'a+') as item :
            item.seek(os.SEEK_END )
            item.write(string)
    # 仅在调试时开启
    #print string


class Webservermanagement():
    """
    """
    
    def __init__(self):
        """
        """
        #找到webserver的工作路径
        #即 testlibversion.py 文件所在的路径
        #相对路径.\TR069\lib\upgrade\__file__   4次dirname
        path = os.path.dirname(__file__)
        path = os.path.dirname(path)
        path = os.path.dirname(path)
        path = os.path.dirname(path)
        self.cur_work_path = path
        self.cur_ver = ""
        self.download_path = servermangementcfg.WEB_DOWNLOAD_SAVE_PATH  #默认配置的下载包存放版本
        self.download_unpack_path = os.path.join(self.download_path, "unpack", LIB_NAME)
        
        self.rename_file_list = []
        self.newversion_add_file_list = []
        
        #pythoncom.CoInitialize()
       
    def __del__(self):
        #pythoncom.CoUninitialize()
        pass
            
    def get_cur_ver(self):
        """
        获取当前版本
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
            
        self.cur_ver = ver
        debug_output( u"get_cur_ver: %s."%ver)
        return ver
        
    def restart_apache(self):
        """
        重启apache应用程序
        """        
        try:
            
            #拉一个新的启动apache进程
            path = os.path.dirname(__file__)
            start_file1 = os.path.join(path,"startapache.py")
            if not os.path.isfile(start_file1):
                start_file1 = os.path.join(path,"startapache.pyc")
            if not os.path.isfile(start_file1):
                debug_output( u"startapache.py  文件不存在" )   
                return False
            """
            retcode = subprocess.Popen(start_file1,
                                        shell=True,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
            """
            
            cmd = u'start "%s" "%s" "%s" "%s"' % ("python.exe",
                                                  start_file1,
                                                  self.download_unpack_path,
                                                  self.cur_work_path)
            subprocess.Popen(cmd, shell = True)
            
        except Exception, e:
            #在界面上显示自动重启出现异常，提醒用户手动重启ATT
            return False
        
        #关闭当前ATT进程
        debug_output( u"run %s" % cmd) 
        #os.kill(os.getpid(), 9)
        
        return True
    
    def get_useable_vers(self):
        """
        获取升级服务器上的可用版本
        """
        vers = []
             
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
     
    
    def upgrade(self, new_ver=None):
        """
        isrunning 当前状态
        new_ver 需要升级的版本 默认服务器上的最新版本
        """
        ret = False
        
        debug_output( u"upgrade  start---")
        try:
            if not self.need_upgrade(new_ver):
                return ret
            #下载和解压
            self.download_ver(new_ver)
            
            self.restart_apache()
            
            ret = True
            
        except Exception,e:
            self._print_trace(e)
        debug_output( u"upgrade  end---")
        return ret
            
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
#g_Web_server_control = Webservermanagement()

if __name__ == '__main__':
    path = os.path.basename(__file__)
    w = Webservermanagement()
    w.restart_apache()


