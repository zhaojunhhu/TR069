#coding:utf-8

"""
    nwf 2012-08-13  V1.0
                    1、define error code
                     


"""

# general
_ERR_START = 0x0000
ERR_SUCCESS = (_ERR_START + 0)      # success code
ERR_FAIL = (_ERR_START + 1)         # fail code
ERR_FATAL = (_ERR_START + 2)        # fatal code, break flow


# global
__all__ = [ "ERR_SUCCESS",
           "ERR_FAIL",
           "ERR_FATAL",
            
          ]
