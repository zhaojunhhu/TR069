# coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：启用禁用无线SSID，最多支持4个SSID的操作；
    若查询不到用户要操作的SSIDNum则失败退出，若用户输入的SSIDNum有重复则提示参数错误退出。
    
    
    参数：
    | SSIDNum1           | 1 | 需要启用禁用的SSID序号 |
    | Enable1            | 1 | 序号为SSIDNum1的SSID启用或禁用标识,默认为1表示启用  |
    | SSIDNum2           | 2 | 需要启用禁用的SSID序号 |
    | Enable2            | 1 | 序号为SSIDNum2的SSID启用或禁用标识,默认为1表示启用  |
    | SSIDNum3           | 3 | 需要启用禁用的SSID序号 |
    | Enable3            | 1 | 序号为SSIDNum3的SSID启用或禁用标识,默认为1表示启用  |
    | SSIDNum4           | 4 | 需要启用禁用的SSID序号 |
    | Enable4            | 1 | 序号为SSIDNum1的SSID启用或禁用标识,默认为1表示启用  |
    
    
    
            
    
    注意:如果SSIDNum为null，则不对该参数对应的SSID序号做任何操作，
    另外，不对Enable1-Enable4的合法性做检查,交由CPE去处理.
"""

# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
    "SSIDNum1": ("1", "1"),
    "Enable1": ("1", "2"),
    "SSIDNum2": ("2", "3"),
    "Enable2": ("1", "4"),
    "SSIDNum3": ("3", "5"),
    "Enable3": ("1", "6"),
    "SSIDNum4": ("4", "7"),
    "Enable4": ("1", "8")
}
