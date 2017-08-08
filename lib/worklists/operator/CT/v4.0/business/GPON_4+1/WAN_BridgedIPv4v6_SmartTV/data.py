#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：IPv4桥接上网改 IPv4/v6双栈 + 智能电视业务工单：

    IPv4/v6为INTERNET模式，桥接方式；
    
    参数：
    | PVC_OR_VLAN1           | 2500 | WAN连接的VLAN,LAN\GPON\VDSL用VLAN格式,默认是GPON的VLAN |
    | X_CT_COM_LanInterface1 | LAN3,LAN4,WLAN1 | 绑定LAN端口,默认LAN3,LAN4,WLAN1 |
    | PVC_OR_VLAN2           | 2 | 智能电视所绑定的VLAN，默认是GPON的VLAN   |
     
    
            
"""


# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
    "PVC_OR_VLAN1":("2500","1"),
    "X_CT_COM_LanInterface1":("LAN3,LAN4,WLAN1","2"),
    "PVC_OR_VLAN2":("2","3")
}
