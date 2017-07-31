#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：开通上网(IPv4/v6桥接) + IPTV + VOIP(软交换 SIP)业务工单：

    IPv4/v6为INTERNET模式，桥接方式；
    
    IPTV为OTHER桥接，绑定LAN2；
    
    VOIP为TR069,VOIP模式；
    
    
    参数：
    | PVC_OR_VLAN1           | 2500 | WAN连接的VLAN,LAN\EPON\VDSL用VLAN格式,默认是EPON的VLAN |
    | X_CT_COM_LanInterface1 | LAN3,LAN4,WLAN1 | 绑定LAN端口,默认LAN3,LAN4,WLAN1 |
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
    
    
            
"""


# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
    "PVC_OR_VLAN1":("2500","1"),
    "X_CT_COM_LanInterface1":("LAN3,LAN4,WLAN1","2"),
    "PVC_OR_VLAN2":("2","3"),
    "X_CT_COM_MulticastVlan":("166","4"),
    "PVC_OR_VLAN3":("46","5"),
    "ProxyServer":("172.24.55.67","6"),
    "ProxyServerPort":("5060","7"),
    "RegistrarServer":("172.24.55.67","8"),
    "RegistrarServerPort":("5060","9"),
    "OutboundProxy":("0.0.0.0","10"),
    "OutboundProxyPort":("5060","11"),
    "X_CT_COM_Standby_ProxyServer":("172.24.55.67","12"),
    "X_CT_COM_Standby_ProxyServerPort":("5060","13"),
    "X_CT_COM_Standby_RegistrarServer":("172.24.55.67","14"),
    "X_CT_COM_Standby_RegistrarServerPort":("5060","15"),
    "X_CT_COM_Standby_OutboundProxy":("0.0.0.0","16"),
    "X_CT_COM_Standby_OutboundProxyPort":("5060","17"),
    "AuthUserName1":("55511021","18"),
    "AuthPassword1":("55511021","19")
}
