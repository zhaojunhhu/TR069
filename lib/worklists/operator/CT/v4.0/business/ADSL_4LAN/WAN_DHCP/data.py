#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC ="""
   功能描述：生成一个开通DHCP上网工单.

    参数：
    | PVC_OR_VLAN           | PVC:0/63 | ADSL上行用PVC格式,LAN\EPON\VDSL则用VLAN格式,默认是ADSL的PVC |
    | X_CT_COM_LanInterface | LAN1 | 绑定LAN端口,默认LAN1 |
    | X_CT_COM_ServiceList  | INTERNET | WAN连接的服务模式,即X_CT-COM_ServiceList节点值,默认INTERNET |
    | WANEnable_Switch      | True | WAN连接使能与WAN连接参数是否一起下发,True表示一起下发.默认为True |
    
            
"""


# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
# PVC_OR_VLAN
"PVC_OR_VLAN":("PVC:0/63", "1"),
# 󶨵Ķ˿
"X_CT_COM_LanInterface":("LAN1", "2"),
# 󶨵ķ
"X_CT_COM_ServiceList":("INTERNET", "3"),
# WANʹܶǷ񵥶·
"WANEnable_Switch":("True", "4")
}

