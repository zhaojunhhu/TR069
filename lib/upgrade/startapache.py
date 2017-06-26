#coding:utf-8

# sys
import  os
import  sys
import  inspect
import  shutil
import  time

sys.path.insert(0, "E:\\TR069")
sys.path.insert(0, "E:\\TR069\\TR069\\lib")
sys.path.insert(0, "E:\\TR069\\TR069\\vendor")

import  psutil

RENAME_HEAD = "__disabled__"

def debug_output(message):
    """
    输出打印信息
    """
    cur_path = os.path.dirname(__file__)
    log_path = os.path.join(cur_path, "log")
    if not os.path.exists(log_path):
        os.mkdir(log_path, 0777)
        
    log_file = os.path.join(log_path, "webserver1_upgrade_log.txt")
    
    string = time.strftime('%Y-%m-%d %H:%M:%S ') + message + '\n'
    if isinstance(string, unicode):
        string = string.encode('utf-8')
    
    with open(log_file,'a+') as item :
            item.seek(os.SEEK_END )
            item.write(string)
    # 仅在调试时开启
    #print string


class ApacheM():
    
    def __init__(self, new, loc ):
        
        self.download_unpack_path = new
        self.cur_work_path =loc
        
        self.rename_file_list = []
        self.newversion_add_file_list = []
    
    def start_server(self):
        """
        启动apache2服务，启动时会检查是否有新的版本已经下载下来
        若有新的版本已经下载下来，则替换新文件
        """        
        new_path = self.download_unpack_path
        if os.path.isdir(new_path):
            if os.listdir(new_path): #目录不为空 20140708
                #update data
                self._update_config_data(new_path)
                
                #copy
                self._copy_new_ver(new_path, self.cur_work_path)
                
                self._rm_folder(new_path)        
            
        debug_output( "start_tr069 web server---- " )   
        os.system("net start apache2.2")

    def stop_server(self):
        """
        停止apache2服务
        """  
        debug_output( "stop_tr069 web server--- "  )
        os.system("net stop apache2.2")
    
   
    def _update_config_data(self, unzip_path):
        """
        """
        ret = False
          
        debug_output( u"update_config_data...")
    
        return ret
    
    def _copy_new_ver(self, new_path, local_save):
        """
        """
        ret = False
        
        #copy    
        if not os.path.isdir(new_path):
            return ret        
        if not os.listdir(new_path): #目录不为空 20140708
            return ret
        
        debug_output( u"start copy files  %s to %s" % (new_path, local_save))
        try:
        
            os.chmod(new_path, 0777)
            os.chmod(local_save, 0777)
            
            self._copy_dir(new_path, local_save)
            
            ret =  True
        except Exception,e:            
            self._print_trace(e)
            
        if ret:
            debug_output( u"copy files  %s to %s suc" % (new_path, local_save))
            self._end_copyfiles()
        else:
            debug_output( u"copy files  %s to %s fail" % (new_path, local_save))
            self._reback_copyfiles()
              
        return ret
    
    def _copy_file(self, src, dst):
        """
        dst  为工作目录的文件
        """        
         
        if os.path.isfile(dst):
            #原来存在该文件 重命名
            dirname, filename = os.path.split(dst)
            if (filename.lower()).find(".cfg") != -1:
                #配置文件
                debug_output( u"配置文件 %s 不更新"%filename)                
                #todo  后面需要考虑配置文件局部更新
                return
            tmp_file = os.path.basename(__file__)
            if filename.lower() in [tmp_file]: #"webservermanagement.py","webservermanagement.pyc"
                #用于升级的文件不用更新
                debug_output( u"web升级文件 %s 不更新"%filename)
                return            
            
            tmp_rename_old_file = os.path.join(dirname, RENAME_HEAD+filename)
            os.rename(dst, tmp_rename_old_file)
            
            self.rename_file_list.append(tmp_rename_old_file)
            
        else: 
            #原来不存在  新增文件
            self.newversion_add_file_list.append(dst)
        shutil.copy2(src, dst)
    
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
    
    def _reback_copyfiles(self):
        """
        回滚
        """
        try:
            for file_path in self.rename_file_list:
                dirname, filename = os.path.split(file_path)
                tmp_old_file = os.path.join(dirname, filename[len(RENAME_HEAD):])
                
                try:
                    os.remove(tmp_old_file)
                except Exception:
                    pass
                
                os.rename(file_path, tmp_old_file)            
            self.rename_file_list = []
            
            for add_file_path in self.newversion_add_file_list:
                os.remove(add_file_path)
            self.newversion_add_file_list = []
            time.sleep(1)
        except Exception, e:
            self._print_trace(e)
    
    def _end_copyfiles(self):
        """
        完成copy  删除重命名文件
        """
        try:
            for file_path in self.rename_file_list:
                os.remove(file_path)
                pass
            self.rename_file_list = []
            time.sleep(1)
            
            self.newversion_add_file_list = []
            
        except Exception, e:
            self._print_trace(e)


    def _rm_folder(self, folder_path):
        """
        删除
        """    
        if os.path.isdir(folder_path):       
            debug_output( u"delete old folder_path=%s" %folder_path)
            shutil.rmtree(folder_path)
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
time.sleep(0.1)
a = ""
b = ""
if len(sys.argv) == 3:
    a = sys.argv[1]
    b = sys.argv[2]
am = ApacheM(a, b)
am.stop_server()
time.sleep(1)
am.start_server()
#end

