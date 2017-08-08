#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：开通IPv4桥接上网改IPv4/v6双栈上网 业务工单

    参数：
    | PVC_OR_VLAN1           | 2500 | ADSL上行用PVC格式,LAN\GPON\VDSL则用VLAN格式,默认是ADSL的PVC |
    | X_CT_COM_LanInterface1 | LAN3,LAN4,WLAN1 | 绑定LAN端口,默认LAN3,LAN4,WLAN1 |
    
            
"""


# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
    "PVC_OR_VLAN1":("2500", "1"),
    "X_CT_COM_LanInterface1":("LAN3,LAN4,WLAN1", "2"),    
}
