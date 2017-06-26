# -*- coding: utf-8 -*-
import os
import datetime
import threading


RL_LOG_DEBUG_FLAG=True #发布正式版本，关闭LOG模块。changed by wangjun 20140225
RK_LOG_FILE      =None
LOCK__LOG        = threading.Lock()
    
def _log_string(log_string):
    """
    将LOG信息写入LOG文件中
    """
    global RK_LOG_FILE
    
    if not RL_LOG_DEBUG_FLAG:
        return
    
    if not RK_LOG_FILE:
        _set_logfile_path() 
        
    try:
        global LOCK__LOG
        LOCK__LOG.acquire()
        
        if isinstance(log_string, unicode):
            log_string=log_string.encode("utf8")
            
        elif not isinstance(log_string, str):
            return
        
        else:
            pass

        #当LOG文件超过30M时，清除旧的LOG。#add by wangjun 20140116
        #----------------------------------------------
        #30M
        max_byte = 1024*1024*30
        
        #以字节为单位
        if RK_LOG_FILE:
            
            #添加判断文件是否存在的检测，只有当文件存在时才获取其大小数据
            if os.path.exists(RK_LOG_FILE):
                
                #获取文件长度
                file_size = int(os.path.getsize(RK_LOG_FILE))
            
                if file_size > max_byte:
                    try:
                        os.remove(RK_LOG_FILE)
                    except Exception,e:
                        pass
        #----------------------------------------------
        
        #print log_string
        with open(RK_LOG_FILE,'a+') as item :
            item.seek(os.SEEK_END )
            
            #在LOG信息前添加时间LOG #add by wangjun 20140110
            #----------------------------------------
            date=datetime.datetime.now()
            now_time_data_string = (('[%s/%s/%s %s:%s:%s %s]  ') % (date.year,date.month,date.day,
                                        date.hour, date.minute, date.second,date.microsecond) )
            log_string = now_time_data_string + log_string
            #----------------------------------------
            
            item.write(log_string)
            item.write('\n')
            
    except Exception, e:
        pass
        
    finally:  
        LOCK__LOG.release()


def _set_logfile_path():
    """
    设置LOG文件存放的路径
    """
    global RK_LOG_FILE

    RK_ROBOTIDE_DIRECTORY = os.path.dirname(os.path.dirname(__file__))

    #更新LOG文件地址
    RK_LOG_DIR = os.path.join(RK_ROBOTIDE_DIRECTORY, 'TR069_BS_log')
    
    dt_obj=datetime.datetime.now()
    log_file_name = "log-%s.txt" % dt_obj.date()

    RK_LOG_FILE = os.path.join(RK_LOG_DIR,log_file_name)
    if not os.path.exists(RK_LOG_DIR):
        os.makedirs(RK_LOG_DIR, 777)
        
        
class ProcessOutLog():
    """
    自定义LOG接口,用于DEBUG模式
    """
    @staticmethod        
    def debug_info(log_string):

        try:
            _log_string(log_string)
            
        except Exception, e:
            pass


    @staticmethod
    def debug_err(log_string):
        try:
            _log_string(log_string)
            
        except Exception, e:
            pass


    @staticmethod
    def user_info(log_string):
        try:
            _log_string(log_string)
            
        except Exception, e:
            pass
    

if __name__ == '__main__':


    ProcessOutLog.debug_info(u"WAJNTUN=TESTE")
    ProcessOutLog.debug_info(u"w危险了点WAJNTUN=TESTE")