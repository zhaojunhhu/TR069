#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：开通上网(IPv4/v6路由) + IPTV(IPv4/v6) + 智能电视 业务工单

    参数：
    | PVC_OR_VLAN1           | 2500 | WAN连接的VLAN,LAN\GPON\VDSL用VLAN格式,默认是GPON的VLAN |
    | Username               | tw1 | 拨号上网的帐号,默认tw1 |
    | Password               | tw1 | 拨号上网的密码,默认tw1 |
    | X_CT_COM_LanInterface1 | LAN3,LAN4,WLAN1 | IPv6连接绑定LAN端口,默认LAN3,LAN4,WLAN1 |
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
    | PVC_OR_VLAN2           |  | IPTV的VLAN，默认是GPON的VLAN   |
    | X_CT_COM_MulticastVlan | 166 | 公共组播VLAN(注意:如果此参数值为"null",则表示不下发组播VLAN节点.) |
    
            
"""


# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
    "PVC_OR_VLAN1":("2500", "1"),
    "Username":("tw1", "2"),
    "Password":("tw1", "3"),
    "X_CT_COM_LanInterface1":("LAN3,LAN4,WLAN1", "4"),
    "IPv6IPAddressOrigin":("AutoConfigured", "5"),
    "IPv6PrefixOrigin":("PrefixDelegation", "6"),
    "IPv6PrefixMode":("WANDelegated", "7"),
    "IPv6Prefix":("2001:1:2:3::/64", "8"),
    "IPv6DNSConfigType":("WANConnection", "9"),
    "IPv6DNSServers":("fe80::1", "10"),
    "DHCPv6ServerEnable":("1", "11"),
    "DHCPv6ServerMinAddress":("0:0:0:1", "12"),
    "DHCPv6ServerMaxAddress":("ffff:ffff:ffff:fffe", "13"),
    "RouterAdvEnable":("1", "14"),
    "AdvManagedFlag":("1", "15"),
    "AdvOtherConfigFlag":("1", "16"),
    "PVC_OR_VLAN2":("", "17"),
    "X_CT_COM_MulticastVlan":("166","18")
}
