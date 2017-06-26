#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：生成一个4SSID均修改为WPA加密测试的工单.

    参数：
    | WPAEncryptionModes | TKIPEncryption | WPA加密方式,默认为TKIPEncryption(可选TKIPEncryption和AESEncryption) |
    | PreSharedKey | 12345678 | WPA的PSK码,默认12345678 |
    
            
    
    注意:此工单中的脚本,固定会帮忙开通4个SSID(如果已开通,则不会再新建).
"""


# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
"WPAEncryptionModes":("TKIPEncryption", "1"),
"PreSharedKey":("12345678", "2")
}
