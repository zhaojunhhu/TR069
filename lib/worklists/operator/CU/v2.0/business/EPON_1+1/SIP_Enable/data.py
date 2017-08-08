# coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：生成一个SIP开通工单

    参数：
    | ProxyServer                          | 172.24.55.67 | SIP服务器域名或者为IP地址 |
    | ProxyServerPort                      | 5060 | SIP服务器端口号 |
    | RegistrarServer                      | 172.24.55.67 | Registrar服务器域名或者为IP地址 |
    | RegistrarServerPort                  | 5060 | Registrar服务器端口号 |
    | OutboundProxy                        | 0.0.0.0 | Outbound服务器域名或者为IP地址 |
    | OutboundProxyPort                    | 5060| Outbound服务器端口号  |
    | X_CU_SecondaryProxyServer            | 172.24.55.67 | 备用SIP服务器域名或者为IP地址 |
    | X_CU_SecondaryProxyServerPort        | 5060 | 备用SIP服务器端口号 |
    | X_CU_SecondaryRegistrarServer        | 172.24.55.67 | 备用Registrar服务器域名或者为IP地址 |
    | X_CU_SecondaryRegistrarServerPort    | 5060 | 备用Registrar服务器端口号 |
    | X_CU_SecondaryOutboundProxyServer    | 0.0.0.0  | 备用Outbound服务器域名或者为IP地址  |
    | X_CU_SecondaryOutboundProxyServerPort| 5060 | 备用Outbound服务器端口号 |   
    | AuthUserName1                        | 55511021 | S1口认证用户名 |
    | AuthPassword1                        | 55511021 | S1口认证密码 |
    | URI1                                 | 55511021 | S1口用戶号码 |
    | PVC_OR_VLAN                          | PVC:0/63 | ADSL上行用PVC格式,LAN\EPON\VDSL则用VLAN格式,默认是ADSL的PVC |
    | X_CU_ServiceList                 | VOIP | WAN连接的服务模式,即X_CU_ServiceList节点值,默认VOIP |
    | WANEnable_Switch                     | True | WAN连接使能与WAN连接参数是否一起下发,True表示一起下发.默认为True |

"""

# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
    "ProxyServer": ("172.24.55.67", "1"),
    "ProxyServerPort": ("5060", "2"),
    "RegistrarServer": ("172.24.55.67", "3"),
    "RegistrarServerPort": ("5060", "4"),
    "OutboundProxy": ("0.0.0.0", "5"),
    "OutboundProxyPort": ("5060", "6"),
    "X_CU_SecondaryProxyServer": ("172.24.55.67", "7"),
    "X_CU_SecondaryProxyServerPort": ("5060", "8"),
    "X_CU_SecondaryRegistrarServer": ("172.24.55.67", "9"),
    "X_CU_SecondaryRegistrarServerPort": ("5060", "10"),
    "X_CU_SecondaryOutboundProxyServer": ("0.0.0.0", "11"),
    "X_CU_SecondaryOutboundProxyServerPort": ("5060", "12"),
    "AuthUserName1": ("55511021", "13"),
    "AuthPassword1": ("55511021", "14"),
    "URI1": ("55511021", "15"),
    "PVC_OR_VLAN": ("PVC:0/63", "16"),
    "X_CU_ServiceList": ("VOIP", "17"),
    "WANEnable_Switch": ("True", "18")
}
