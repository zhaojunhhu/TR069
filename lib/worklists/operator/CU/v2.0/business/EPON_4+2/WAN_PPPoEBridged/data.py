# coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：生成一个开通Other桥连接工单.

    参数：
    | PVC_OR_VLAN           | PVC:0/62 | ADSL上行用PVC格式,LAN\EPON\VDSL则用VLAN格式,默认是ADSL的PVC |
    | X_CU_LanInterface | LAN2 | 绑定LAN端口,默认LAN2 |
    | X_CU_ServiceList  | OTHER | WAN连接的服务模式,即X_CU_ServiceList节点值,默认OTHER |
    | WANEnable_Switch      | True | WAN连接使能与WAN连接参数是否一起下发,True表示一起下发.默认为True |
    
            
"""

# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
    "PVC_OR_VLAN": ("PVC:0/62", "1"),
    "X_CU_LanInterface": ("LAN2", "2"),
    "X_CU_ServiceList": ("OTHER", "3"),
    "WANEnable_Switch": ("True", "4")
}
