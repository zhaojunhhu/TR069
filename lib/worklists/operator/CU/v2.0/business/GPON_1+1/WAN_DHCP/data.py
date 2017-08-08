#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
   功能描述：生成一个开通DHCP上网工单.

    参数：
    | PVC_OR_VLAN           | PVC:0/63 | ADSL上行用PVC格式,LAN\GPON\VDSL则用VLAN格式,默认是ADSL的PVC |
    | X_CU_LanInterface | LAN1 | 绑定LAN端口,默认LAN1 |
    | X_CU_ServiceList  | INTERNET | WAN连接的服务模式,即X_CU_ServiceList节点值,默认INTERNET |
    | WANEnable_Switch      | True | WAN连接使能与WAN连接参数是否一起下发,True表示一起下发.默认为True |
    
            
"""

# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
    "PVC_OR_VLAN": ("PVC:0/63", "1"),
    "X_CU_LanInterface": ("LAN1", "2"),
    "X_CU_ServiceList": ("INTERNET", "3"),
    "WANEnable_Switch": ("True", "4")
}
