#coding:utf-8

# sys
import  os
import  zipfile

import sys
import time
#import pythoncom

import  servermangementcfg
import  package.downloadclient          as downloadclient
import  package.parsequeryvesioninfo    as parsequeryvesioninfo
import  package.queryinfoclient         as queryinfoclient
import  package.messagehandle           as messagehandle

def debug_output(message):
    """
    输出打印信息
    """
    cur_path = os.path.dirname(__file__)
    log_path = os.path.join(cur_path, "log")
    if not os.path.exists(log_path):
        os.mkdir(log_path, 0777)
        
    log_file = os.path.join(log_path, "Versionmanagement_log.txt")
    
    string = time.strftime('%Y-%m-%d %H:%M:%S ') + message + '\n'
    if isinstance(string, unicode):
        string = string.encode('utf-8')
    
    with open(log_file,'a+') as item :
            item.seek(os.SEEK_END )
            item.write(string)
    # 仅在调试时开启
    #print string


class Versionmanagement():
    """
    下载版本、解压版本
    """
    def __init__(self):       
        
        #pythoncom.CoInitialize()
        
        # server cfg
        messagehandle.Event.UPGRADE_SERVER_HTTP_IP = servermangementcfg.DOWNLOAD_IP
        messagehandle.Event.UPGRADE_SERVER_HTTP_PORT = servermangementcfg.DOWNLOAD_PORT
        
    def __del__(self):
        
        #pythoncom.CoUninitialize()
        pass
        
    def download_pack(self, lib_name, lib_ver, save_path):
        """
        lib_name = TR069
        lib_ver = v.beta131021.svn1772
        save_path = c:/save
        """
        ret = False
        
        download_obj = downloadclient.DownloadClient()        
        rc_request_status = download_obj.handle_download(lib_name, lib_ver, save_path)
        if messagehandle.Event.CLIENT_REQUEST_FAIL==rc_request_status:
            debug_output(u"handle_download fail.")
        else:
            debug_output(u"handle_download suc.")  
            ret = True
    
        return ret
    
    def _query_versions(self):
        """
        """
        vers = None
        
        for nwf in [1]:
        
            query_obj = queryinfoclient.QueryInfoClient()
            
            
            debug_output(u"handle_query_info ....")  
            rc_request_status = query_obj.handle_query_info()
            
            
            if messagehandle.Event.CLIENT_REQUEST_FAIL == rc_request_status:
                debug_output(u"handle_query_info fail.")
                break
            
            debug_output(u"handle_query_info suc." )
            vers = query_obj.query_result_all_version_dict
            
        return vers
    
    def query_usable_versions(self, lib_name, lib_ver=None):
        """
        """
        vers_list = []
        try:
            vers_dict = self._query_versions()
            if not vers_dict:
                debug_output(u"_query_versions fail.")
                return vers_list
            
            
            #根据lib_name, lib_ver取版本列表
            server_vers = vers_dict.get(lib_name, [])
            
            for key in  server_vers.keys():
                lst = server_vers.get(key, [])
                for dit in lst:
                    ver = dit.get("TESTLIB_VERSION", None)
                    if self._ver_type_check(lib_ver, ver):
                        vers_list.append(ver)
                    
            vers_list.sort(reverse=True)
        except Exception, e:
            debug_output(u"query_usable_versions Exception")
            debug_output(str(e))
        return vers_list
    
    def get_last_version(self, lib_name, lib_ver=None):
        """
        """
        vers = self.query_usable_versions(lib_name, lib_ver)
        ver = ""
        #取最新版
        for item in vers:
            if item > ver:
                ver = item
        
        return ver
    
    def _ver_type_check(self, lib_ver, item):
        """
        """
        #当前为空不检查
        if not lib_ver:
            return True
        
        if not item:
            return False
        
        return True  #目前不判断版本
        
        a = (lib_ver.find("beta") != -1)
        b = (item.find("beta") != -1)
        
        return True if a==b else False


    def unzip_pack(self, zip_path, unzip_path):
        """
        """
        #bao 存在
        if not os.path.exists(zip_path):
            pass
        
        #新目录存在
        #遍历创建
        
        #解压
        zipFile = zipfile.ZipFile(zip_path)     
        zipFile.extractall(unzip_path)

if __name__ == '__main__':
            
    a = Versionmanagement()
    
    print a._query_versions()
    print dit
    
    #a.download_pack("TR069Server", "v.beta140624.svn3183", "D:\\5")
    
    a.unzip_pack("D:\\5\\TR069Server_v.beta140624.svn3183.zip", "D:\\5\\unpack")
    
    
    print sys.path
    
    


