#coding:utf-8


# CPE INFO
BASE_OPERATOR               = "CU"


# 配置 正反向默认密码
ACS2CPE_LOGIN_NAME          = "RMS"
ACS2CPE_LOGIN_PASSWORD      = "RMS"

CPE2ACS_LOGIN_NAME          = "cpe"
CPE2ACS_LOGIN_PASSWORD      = "cpe"


# EVENTCODE MAP
# eventcode 映射  调用的系统工单
EVENTCODE_MAP = {
    
    "0 BOOTSTRAP":                  "BOOTSTRAP",
    
    "X_CU_ADMINPASSWORDCHANGE":       "ACCOUNTCHANGE",        
}



