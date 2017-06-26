#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：生成一个IPTV开通工单

    参数：
    | PVC_OR_VLAN             | PVC:0/65 | ADSL上行用PVC格式,LAN\EPON\VDSL则用VLAN格式,默认是ADSL的PVC |
    | X_CT_COM_MulticastVlan  | 165 | 公共组播VLAN(注意:如果此参数值为"null",则表示不下发组播VLAN节点.) |
    | WANEnable_Switch        | True | WAN连接使能与WAN连接参数是否一起下发,True表示一起下发.默认为True |
    
            
    
    注意：此工单脚本中默认了绑定到LAN2
    
    对于公共组播VLAN,严格来说ADSL上行的CPE均不需支持,但发现部分CPE可以支持.
    所以,当CPE不支持时,可通过将此参数设置为"null"达到不下发的目的.
"""


# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
# PVC_OR_VLAN
"PVC_OR_VLAN":("PVC:0/65", "1"),
"X_CT_COM_MulticastVlan":("165", "2"),
# WANʹܶǷ������·
"WANEnable_Switch":("True", "3")
}

