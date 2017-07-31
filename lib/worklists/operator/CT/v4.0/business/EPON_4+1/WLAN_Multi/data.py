#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：生成一个多SSID复杂测试工单.工单对各SSID和WAN连接的操作如下表.
    | SSID1 | 不做任何修改 |
    | SSID2 | 如果没有则新建,强制更改为WEP加密 |
    | SSID3 | 如果没有则新建,强制更改为不加密 |
    | SSID4 | 如果没有则新建,强制更改为不加密 |
    | WAN1 | 强制新建,PPPoE的INTERNET连接 |
    | WAN2 | 强制新建,PPPoE的INTERNET连接 |
    | WAN3 | 强制新建,PPPoE_Bridged的INTERNET连接 |
    | WAN4 | 强制新建,PPPoE_Bridged的INTERNET连接 |
    
    参数：
    | WEPKeyIndex        | 1 | WEP密钥索引号,默认为1 |
    | WEPEncryptionLevel | 40-bit | WEP加密标准,默认40-bit |
    | WEPKey             | 0123456789 | WEP密钥,默认0123456789 |
    | PVC_OR_VLAN1       | PVC:0/71 | 第一条WAN的PVC或VLAN.ADSL上行用PVC格式,LAN\EPON\VDSL则用VLAN格式,默认是ADSL的PVC |
    | Username1          | TW71 | 第一条WAN的拨号上网的帐号,默认TW71 |
    | Password1          | TW71 | 第一条WAN的拨号上网的密码,默认TW71 |
    | PVC_OR_VLAN2       | PVC:0/72 | 第二条WAN的PVC或VLAN.ADSL上行用PVC格式,LAN\EPON\VDSL则用VLAN格式,默认是ADSL的PVC |
    | Username2          | TW72 | 第二条WAN的拨号上网的帐号,默认TW72 |
    | Password2          | TW72 | 第二条WAN的拨号上网的密码,默认TW72 |
    | PVC_OR_VLAN3       | PVC:0/73 | 第三条WAN的PVC或VLAN.ADSL上行用PVC格式,LAN\EPON\VDSL则用VLAN格式,默认是ADSL的PVC |
    | PVC_OR_VLAN4       | PVC:0/74 | 第四条WAN的拨号上网的帐号,默认TW71 |
    | WANEnable_Switch   | True | WAN连接使能与WAN连接参数是否一起下发,True表示一起下发.默认为True |
    
            
    
    注意:WAN连接均是强制新建,即没有查的过程,所以如果原来有WAN连接冲突,则会失败
    已查到有VDSL的CPE,其第一个SSID的X_CT-COM_APModuleEnable值不能设置.无论是下发布尔型还是字符串型的开关使能均回9002.
    这是CPE的问题.贝曼工单抓包是要支持这样操作的.
"""


# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
"WEPKeyIndex":("1", "1"),
"WEPEncryptionLevel":("40-bit", "2"),
"WEPKey":("0123456789", "3"),
# WAN1
"PVC_OR_VLAN1":("PVC:0/71", "4"),
"Username1":("TW71", "5"),
"Password1":("TW71", "6"),
# WAN2
"PVC_OR_VLAN2":("PVC:0/72", "7"),
"Username2":("TW72", "8"),
"Password2":("TW72", "9"),
# WAN3
"PVC_OR_VLAN3":("PVC:0/73", "10"),
# WAN4
"PVC_OR_VLAN4":("PVC:0/74", "11"),
"WANEnable_Switch":("True", "12")
}
