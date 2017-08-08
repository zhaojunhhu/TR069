# coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：生成一个开通PPPoE上网工单.
    
    参数：
    | PVC_OR_VLAN           | PVC:0/61 | ADSL上行用PVC格式,LAN\GPON\VDSL则用VLAN格式,默认是ADSL的PVC |
    | Username              | TW61 | 拨号上网的帐号,默认TW61 |
    | Password              | TW61 | 拨号上网的密码,默认TW61 |
    | X_CU_LanInterface | LAN1 | 绑定LAN端口,默认LAN1 |
    | X_CU_ServiceList  | INTERNET | WAN连接的服务模式,即X_CU_ServiceList节点值,默认INTERNET |
    | WANEnable_Switch      | True | WAN连接使能与WAN连接参数是否一起下发,True表示一起下发.默认为True |
    
    注意：参数为null时，表示不下发该配置，用在走修改流程时。
    
"""

# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
    "PVC_OR_VLAN": ("PVC:0/61", "1"),
    "Username": ("TW61", "2"),
    "Password": ("TW61", "3"),
    "X_CU_LanInterface": ("LAN1", "4"),
    "X_CU_ServiceList": ("INTERNET", "5"),
    "WANEnable_Switch": ("True", "6")
}
