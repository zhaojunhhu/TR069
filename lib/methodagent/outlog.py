#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: outlog
#  function: OutLog
#            
#  Author: ATT development group
#  version: V1.0
#  date: 2013.8.29
#  change log:
#  wangjun  20130829    create
# ***************************************************************************

class OutLog():
    """
    自定义LOG接口,用于DEBUG模式
    """
    @staticmethod        
    def debug_info(log_string):
        print log_string
        
    @staticmethod    
    def debug_err(log_string):
        print log_string