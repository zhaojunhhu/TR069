#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：生成一个开通PPPoE上网和IPTV的Other桥工单.

    参数：
    | PVC_OR_VLAN1           | PVC:0/65 | ADSL上行用PVC格式,LAN\EPON\VDSL则用VLAN格式,默认是ADSL的PVC |
    | Username               | TW65 | 拨号上网的帐号,默认TW65 |
    | Password               | TW65 | 拨号上网的密码,默认TW65 |
    | X_CU_COM_LanInterface1 | LAN1 | 绑定LAN端口,默认LAN1 |
    | X_CU_COM_ServiceList1  | INTERNET | WAN连接的服务模式,即X_CU-COM_ServiceList节点值,默认INTERNET |
    | PVC_OR_VLAN2           | PVC:0/66 | Other桥的PVC或VLAN,ADSL上行用PVC格式,LAN\EPON\VDSL则用VLAN格式,默认是ADSL的PVC |
    | X_CU_COM_MulticastVlan | 166 | 公共组播VLAN(注意:如果此参数值为"null",则表示不下发组播VLAN节点.) |
    | WANEnable_Switch       | True | WAN连接使能与WAN连接参数是否一起下发,True表示一起下发.默认为True |
    
            
    
    注意:此工单中的Other桥,在脚本中已固定绑定到LAN2
    
    对于公共组播VLAN,严格来说ADSL上行的CPE均不需支持,但发现部分CPE可以支持.
    所以,当CPE不支持时,可通过将此参数设置为"null"达到不下发的目的.
"""



# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
# PVC_OR_VLAN1
"PVC_OR_VLAN1":("PVC:0/65", "1"),
"Username":("TW65", "2"),
"Password":("TW65", "3"),
# 󶨵Ķ˿
"X_CU_COM_LanInterface1":("LAN1", "4"),
# 󶨵ķ
"X_CU_COM_ServiceList1":("INTERNET", "5"),
# PVC_OR_VLAN2
"PVC_OR_VLAN2":("PVC:0/66", "6"),
"X_CU_COM_MulticastVlan":("166", "7"),
# WANʹܶǷ񵥶·
"WANEnable_Switch":("True", "8")
}

