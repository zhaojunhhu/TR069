#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：开通上网(IPv4路由 + IPv6桥接) + IPTV + VOIP(IMS SIP) + 智能电视业务工单：

    两条WAN连接，一条IPv4路由，采用PPPoE认证，一条IPv6桥接；
    
    IPTV为OTHER桥接，绑定LAN2；
    
    VOIP为VOIP服务模式；
    
    
    参数：
    | PVC_OR_VLAN1           | 2500 | WAN连接的VLAN,LAN\EPON\VDSL用VLAN格式,默认是EPON的VLAN |
    | Username               | tw6@pon.com | IPv4拨号上网的帐号,默认tw6@pon.com |
    | Password               | admin6 | IPv4拨号上网的密码,默认admin6 |
    | X_CT_COM_LanInterface1 | LAN3,LAN4,WLAN1 | IPv6 WAN连接所绑定的LAN端口,默认LAN3,LAN4,WLAN1 |
    | X_CT_COM_LanInterface2 | LAN3,LAN4,WLAN1 | IPv4 WAN连接所绑定的LAN端口,默认LAN3,LAN4,WLAN1 |
    | PVC_OR_VLAN2           | 2 | IPTV的VLAN，默认是EPON的VLAN   |
    | X_CT_COM_MulticastVlan | 166 | 公共组播VLAN(注意:如果此参数值为"null",则表示不下发组播VLAN节点.) |
    | PVC_OR_VLAN3           | 46 | VOIP的VLAN，默认是EPON的VLAN   |
    | ProxyServer                          | 172.24.55.67 | SIP服务器域名或者为IP地址 |
    | ProxyServerPort                      | 5060 | SIP服务器端口号 |
    | RegistrarServer                      | 172.24.55.67 | Registrar服务器域名或者为IP地址 |
    | RegistrarServerPort                  | 5060 | Registrar服务器端口号 |
    | OutboundProxy                        | 0.0.0.0 | Outbound服务器域名或者为IP地址 |
    | OutboundProxyPort                    | 5060 | Outbound服务器端口号 |
    | X_CT_COM_Standby_ProxyServer         | 172.24.55.67 | 备用SIP服务器域名或者为IP地址 |
    | X_CT_COM_Standby_ProxyServerPort     | 5060 | 备用SIP服务器端口号 |
    | X_CT_COM_Standby_RegistrarServer     | 172.24.55.67 | 备用Registrar服务器域名或者为IP地址 |
    | X_CT_COM_Standby_RegistrarServerPort | 5060 | 备用Registrar服务器端口号 |
    | X_CT_COM_Standby_OutboundProxy       | 0.0.0.0 | 备用Outbound服务器域名或者为IP地址 |
    | X_CT_COM_Standby_OutboundProxyPort   | 5060 | 备用Outbound服务器端口号 |
    | AuthUserName1                        | 55511021 | S1口认证用户名 |
    | AuthPassword1                        | 55511021 | S1口认证密码 |
    | AuthUserName2                        | 55511022 | S2口认证用户名 |
    | AuthPassword2                        | 55511022 | S2口认证密码 |
    
    
            
"""


# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
    "PVC_OR_VLAN1":("2500","1"),
    "Username":("tw6@pon.com","2"),
    "Password":("admin6","3"),
    "X_CT_COM_LanInterface1":("LAN3,LAN4,WLAN1","4"),    
    "X_CT_COM_LanInterface2":("LAN3,LAN4,WLAN1","5"),
    "PVC_OR_VLAN2":("2","6"),
    "X_CT_COM_MulticastVlan":("166","7"),
    "PVC_OR_VLAN3":("46","8"),
    "ProxyServer":("172.24.55.67","9"),
    "ProxyServerPort":("5060","10"),
    "RegistrarServer":("172.24.55.67","11"),
    "RegistrarServerPort":("5060","12"),
    "OutboundProxy":("0.0.0.0","13"),
    "OutboundProxyPort":("5060","14"),
    "X_CT_COM_Standby_ProxyServer":("172.24.55.67","15"),
    "X_CT_COM_Standby_ProxyServerPort":("5060","16"),
    "X_CT_COM_Standby_RegistrarServer":("172.24.55.67","17"),
    "X_CT_COM_Standby_RegistrarServerPort":("5060","18"),
    "X_CT_COM_Standby_OutboundProxy":("0.0.0.0","19"),
    "X_CT_COM_Standby_OutboundProxyPort":("5060","20"),
    "AuthUserName1":("55511021","21"),
    "AuthPassword1":("55511021","22"),
    "AuthUserName2":("55511022","23"),
    "AuthPassword2":("55511022","24")
}
