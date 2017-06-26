#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：生成一个SIP开通工单

    参数：
    | ProxyServer                          | 172.24.55.67 | SIP服务器域名或者为IP地址 |
    | ProxyServerPort                      | 5060 | SIP服务器端口号 |
    | RegistrarServer                      | 172.24.55.67 | Registrar服务器域名或者为IP地址 |
    | RegistrarServerPort                  | 5060 | Registrar服务器端口号 |
    | X_CU_SecondaryProxyServer            | 172.24.55.67 | 备用SIP服务器域名或者为IP地址 |
    | X_CU_SecondaryProxyServerPort        | 5060 | 备用SIP服务器端口号 |
    | X_CU_SecondaryRegistrarServer        | 172.24.55.67 | 备用Registrar服务器域名或者为IP地址 |
    | X_CU_SecondaryRegistrarServerPort    | 5060 | 备用Registrar服务器端口号 |
    | AuthUserName1                        | 55511021 | S1口认证用户名 |
    | AuthPassword1                        | 55511021 | S1口认证密码 |
    | URI1                                 | 55511021 | S1口用戶号码 |
    | AuthUserName2                        | 55511022 | S2口认证用户名 |
    | AuthPassword2                        | 55511022 | S2口认证密码 |
    | URI2                                 | 55511021 | S2口用戶号码 |
    | PVC_OR_VLAN                          | PVC:0/63 | ADSL上行用PVC格式,LAN\EPON\VDSL则用VLAN格式,默认是ADSL的PVC |
    | X_CU_ServiceList                 | VOIP | WAN连接的服务模式,即X_CU_ServiceList节点值,默认VOIP |
    | WANEnable_Switch                     | True | WAN连接使能与WAN连接参数是否一起下发,True表示一起下发.默认为True |



    注意:对于只有一个S口的CPE,即使传参数有设置AuthUserName2和AuthPassword2值,在工单模板中也会删除掉而不下发S2口的信息
"""


# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
"ProxyServer":("172.24.55.67","1"),
"ProxyServerPort":("5060","2"),
"RegistrarServer":("172.24.55.67","3"),
"RegistrarServerPort":("5060","4"),
"X_CU_SecondaryProxyServer":("172.24.55.67","5"),
"X_CU_SecondaryProxyServerPort":("5060","6"),
"X_CU_SecondaryRegistrarServer":("172.24.55.67","7"),
"X_CU_SecondaryRegistrarServerPort":("5060","8"),
"AuthUserName1":("55511021","9"),
"AuthPassword1":("55511021","10"),
"URI1":("55511021","11"),
"AuthUserName2":("55511022","12"),
"AuthPassword2":("55511022","13"),
"URI2":("55511022","14"),
"PVC_OR_VLAN":("PVC:0/63", "15"),
"X_CU_ServiceList":("VOIP", "16"),
"WANEnable_Switch":("True", "17")
}
