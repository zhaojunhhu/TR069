#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：开通上网(IPv6路由 + IPv4桥接) + IPTV + VOIP(软交换 SIP) 业务工单：

    两条WAN连接，一条IPv6路由，采用PPPoE认证，一条IPv4桥接；
    
    IPTV为OTHER桥接，绑定LAN2；
    
    VOIP为TR069,VOIP模式；
    
    
    参数：
    | PVC_OR_VLAN1           | 2500 | WAN连接的VLAN,LAN\GPON\VDSL用VLAN格式,默认是GPON的VLAN |
    | Username               | tw6@pon.com | 拨号上网的帐号,默认tw6@pon.com |
    | Password               | admin6 | 拨号上网的密码,默认admin6 |
    | X_CT_COM_LanInterface1 | LAN3,LAN4,WLAN1 | IPv6连接绑定LAN端口,默认LAN3,LAN4,WLAN1 |
    | X_CT_COM_LanInterface2 | LAN3,LAN4,WLAN1 | IPv4连接绑定LAN端口,默认LAN3,LAN4,WLAN1 |
    | IPv6IPAddressOrigin    | AutoConfigured | IPv6地址分配机制,取值范围有：AutoConfigured、DHCPv6、Static、None，默认AutoConfigured |
    | IPv6PrefixOrigin       | PrefixDelegation | IPv6前缀地址分配机制,默认是PrefixDelegation |
    | IPv6PrefixMode         | WANDelegated | 公告前缀的类型，支持两种WANDelegated、Static，默认WANDelegated |
    | IPv6Prefix             | 2001:1:2:3::/64 | IPv6前缀地址，默认为2001:1:2:3::/64 |
    | IPv6DNSConfigType      | WANConnection | IPv6 LAN侧DNSServer来源，可选WANConnection、Static、HGWProxy，默认为WANConnection   |
    | IPv6DNSServers         | fe80::1 | IPv6 DNSServer地址，多个地址以逗号隔开，默认为fe80::1     |
    | DHCPv6ServerEnable     | 1 | 是否使能DHCPv6服务器，默认为1   |
    | DHCPv6ServerMinAddress | 0:0:0:1 | 地址分配起始地址(IP地址的后64位)，默认为 0:0:0:1  |
    | DHCPv6ServerMaxAddress | ffff:ffff:ffff:fffe | 地址分配结束地址(IP地址的后64位)，默认为 ffff:ffff:ffff:fffe  |
    | RouterAdvEnable        | 1 | 是否使能SLAAC，默认为1   |
    | AdvManagedFlag         | 1 | 地址是否通过自动配置机制分配，默认为1         |
    | AdvOtherConfigFlag     | 1 | 地址之外的其他信息是否通过自动配置机制分配，默认为1  |
    | PVC_OR_VLAN2           | 2 | IPTV的VLAN，默认是GPON的VLAN   |
    | X_CT_COM_MulticastVlan | 166 | 公共组播VLAN(注意:如果此参数值为"null",则表示不下发组播VLAN节点.) |
    | PVC_OR_VLAN3           | 46 | VOIP的VLAN，默认是GPON的VLAN   |
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
    "Username":("tw6@pon.com","2"),
    "Password":("admin6","3"),
    "X_CT_COM_LanInterface1":("LAN3,LAN4,WLAN1","4"),
    "X_CT_COM_LanInterface2":("LAN3,LAN4,WLAN1","5"),
    "IPv6IPAddressOrigin":("AutoConfigured","6"),
    "IPv6PrefixOrigin":("PrefixDelegation","7"),
    "IPv6PrefixMode":("WANDelegated","8"),
    "IPv6Prefix":("2001:1:2:3::/64","9"),
    "IPv6DNSConfigType":("WANConnection","10"),
    "IPv6DNSServers":("fe80::1","11"),
    "DHCPv6ServerEnable":("1","12"),
    "DHCPv6ServerMinAddress":("0:0:0:1","13"),
    "DHCPv6ServerMaxAddress":("ffff:ffff:ffff:fffe","14"),
    "RouterAdvEnable":("1","15"),
    "AdvManagedFlag":("1","16"),
    "AdvOtherConfigFlag":("1","17"),
    "PVC_OR_VLAN2":("2","18"),
    "X_CT_COM_MulticastVlan":("166","19"),
    "PVC_OR_VLAN3":("46","20"),
    "ProxyServer":("172.24.55.67","21"),
    "ProxyServerPort":("5060","22"),
    "RegistrarServer":("172.24.55.67","23"),
    "RegistrarServerPort":("5060","24"),
    "OutboundProxy":("0.0.0.0","25"),
    "OutboundProxyPort":("5060","26"),
    "X_CT_COM_Standby_ProxyServer":("172.24.55.67","27"),
    "X_CT_COM_Standby_ProxyServerPort":("5060","28"),
    "X_CT_COM_Standby_RegistrarServer":("172.24.55.67","29"),
    "X_CT_COM_Standby_RegistrarServerPort":("5060","30"),
    "X_CT_COM_Standby_OutboundProxy":("0.0.0.0","31"),
    "X_CT_COM_Standby_OutboundProxyPort":("5060","32"),
    "AuthUserName1":("55511021","33"),
    "AuthPassword1":("55511021","34")
}
