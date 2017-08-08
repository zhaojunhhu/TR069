# coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：生成一个4SSID均修改为WEP加密测试的工单.

    参数：
    | WEPKeyIndex | 1 | WEP密钥索引号,默认为1 |
    | WEPEncryptionLevel | 40-bit | WEP加密标准,默认40-bit |
    | WEPKey | 0123456789 | WEP密钥,默认0123456789 |
    
            
    
    注意:此工单中的脚本,固定会帮忙开通4个SSID(如果已开通,则不会再新建).
"""

# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
    "WEPKeyIndex": ("1", "1"),
    "WEPEncryptionLevel": ("40-bit", "2"),
    "WEPKey": ("0123456789", "3")
}
