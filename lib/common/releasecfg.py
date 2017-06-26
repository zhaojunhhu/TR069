#coding:utf-8

# ***************************************************************************
#
#  nwf      2013-05-24      refactor(unify)
#  nwf      2013-06-07      ini->py
# ***************************************************************************

import  os
import  sys
    
import TR069.lib.common.logs.log as log  # (tr069  RF  both have this)    
    
try:    
    # RF don't have this
    import webservercfg 
    
except Exception,e:
    # 判断是否是Django服务器的log zsj 2014-06-4
    try:
        import attlog as log   
    except Exception,e:
        pass
    

if __name__ == '__main__':
    pass
