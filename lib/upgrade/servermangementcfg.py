# -*- coding: utf-8 -*-


# *************************************************************************
# nwf 2013-10-15  create
# jias 20140619  update 服务器管理模块配置信息
#                       1、升级服务器地址信息
#                       2、当前TR069Server的部署信息
# ***************************************************************************



import os
import sys
import common.logs.log as log
import common.config as config

dirname = os.path.dirname
# 2014-06-25; data split
CONFIG_PATH = os.path.join((dirname(dirname(dirname(__file__)))), "data", "servermangement.cfg")

def read_config():
    ret, ret_data = config.read_cfg(path=CONFIG_PATH, keys = "servermangement")
    if ret == config.FAIL:
        err_info = "read config file failed, err info:%s!" % ret_data
        log.debug_err(err_info)
        ret_data = {}
    return ret_data

dict_cfg = read_config()
if (not dict_cfg):
    desc = "read config file=%s fail" %CONFIG_PATH
    log.debug_err(desc)
    raise Exception(desc)

# from cfg file --------------------------------------------------------
try:
    DOWNLOAD_IP                 = str(dict_cfg.get("DOWNLOAD_IP"))
    DOWNLOAD_PORT               = int(dict_cfg.get("DOWNLOAD_PORT"))
    
except Exception,e:    
    desc = "fail:%s" %(e)
    log.debug_err(desc)
    raise Exception(desc)

#  -----------------------------------------------------------   

#版本存放地址
#DOWNLOAD_IP                                 = "172.24.6.7" # "172.24.16.16" "172.16.28.47"
#DOWNLOAD_PORT                               = 8002


SERVICE_NAME_TR069 = "daemon_tr069"                         #守护的
SERVICE_NAME_DOWNLOAD = "daemon_tr069_download"

#tmp_path = "D:\\TR069_WORK_PATH\\TR069WebServer"

#找到webserver的工作路径
#即 testlibversion.py 文件所在的路径
#相对路径.\TR069\lib\upgrade\__file__   4次dirname
path = os.path.dirname(__file__)
path = os.path.dirname(path)
path = os.path.dirname(path)
path = os.path.dirname(path)
#再上一层 使 TR069Server 与TR069WebServer目录平级
tmp_path = os.path.dirname(path)  #D:\TR069_WORK_PATH
TR069_WORK_PATH = os.path.join(tmp_path, "TR069Server")
TR069_DOWNLOAD_SAVE_PATH = os.path.join(tmp_path, "TR069Server_Package")
WEB_DOWNLOAD_SAVE_PATH = os.path.join(tmp_path, "TR069WebServer_Package")

    
    
