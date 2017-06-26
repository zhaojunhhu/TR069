#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：IPv4路由上网改IPv4路由/IPv6桥接 + 智能电视业务工单：

    两条WAN连接，一条IPv4路由，采用PPPoE认证，一条IPv6桥接；
    
    参数：
    | PVC_OR_VLAN1           | 2500 | WAN连接的VLAN,LAN\EPON\VDSL用VLAN格式,默认是EPON的VLAN |
    | Username               | tw6@pon.com | IPv4拨号上网的帐号,默认tw6@pon.com |
    | Password               | admin6 | IPv4拨号上网的密码,默认admin6 |
    | X_CT_COM_LanInterface1 | LAN3,LAN4,WLAN1 | IPv6 WAN连接所绑定的LAN端口,默认LAN3,LAN4,WLAN1 |
    | X_CT_COM_LanInterface2 | LAN3,LAN4,WLAN1 | IPv4 WAN连接所绑定的LAN端口,默认LAN3,LAN4,WLAN1 |
    | PVC_OR_VLAN2           | 2 | 智能电视所绑定的VLAN，默认是EPON的VLAN   |
    
    
            
"""


# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
    "PVC_OR_VLAN1":("2500","1"),
    "Username":("tw6@pon.com","2"),
    "Password":("admin6","3"),
    "X_CT_COM_LanInterface1":("LAN3,LAN4,WLAN1","4"),
    "X_CT_COM_LanInterface2":("LAN3,LAN4,WLAN1","5"),
    "PVC_OR_VLAN2":("2","6")
}
