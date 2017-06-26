#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：生成一个开通静态地址上网的WAN连接工单.
    
    参数：
    | PVC_OR_VLAN           | PVC:0/64 | ADSL上行用PVC格式,LAN\EPON\VDSL则用VLAN格式,默认是ADSL的PVC |
    | ExternalIPAddress     | 10.10.10.64 | IP地址,默认10.10.10.64 |
    | SubnetMask            | 255.255.255.0 | 子网掩码,默认255.255.255.0 |
    | DefaultGateway        | 10.10.10.1 | 网关,默认10.10.10.1 |
    | DNSServers            | 10.10.10.2,10.10.10.3 | DNS服务器,默认10.10.10.2,10.10.10.3 |
    | X_CU_COM_LanInterface | LAN1 | 绑定LAN端口,默认LAN1 |
    | X_CU_COM_ServiceList  | INTERNET | WAN连接的服务模式,即X_CU-COM_ServiceList节点值,默认INTERNET |
    | WANEnable_Switch      | True | WAN连接使能与WAN连接参数是否一起下发,True表示一起下发.默认为True |
    
        
"""



# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
# VLAN
"PVC_OR_VLAN":("PVC:0/64", "1"),
# IP地址
"ExternalIPAddress":("10.10.10.64", "2"),
# 子网掩码
"SubnetMask":("255.255.255.0", "3"),
# 默认网关
"DefaultGateway":("10.10.10.1", "4"),
# DNS服务器,如果有两个,则用逗号分开
"DNSServers":("10.10.10.2,10.10.10.3", "5"),
# 绑定的端口
"X_CU_COM_LanInterface":("LAN1", "6"),
# 绑定的服务,可选OTHER,INTERNET
"X_CU_COM_ServiceList":("INTERNET", "7"),
# 最后的WAN连接使能动作是否单独下发
"WANEnable_Switch":("True", "8")
}

