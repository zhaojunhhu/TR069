#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：开通上网(IPv4桥接) + IPTV 业务工单

    参数：
    | PVC_OR_VLAN1           | 2500 | ADSL上行用PVC格式,LAN\EPON\VDSL则用VLAN格式,默认是ADSL的PVC |
    | X_CT_COM_LanInterface1 | LAN3,LAN4,WLAN1 | 绑定LAN端口,默认LAN1,可以为LAN1,LAN2,LAN3,LAN4,WLAN1,WLAN2,WLAN3,WLAN4 |     
    | PVC_OR_VLAN2           |  | IPTV的VLAN，默认是EPON的VLAN   |
    | X_CT_COM_MulticastVlan  | 166 | 公共组播VLAN(注意:如果此参数值为"null",则表示不下发组播VLAN节点.) |
    
            
"""


# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
    "PVC_OR_VLAN1":("2500", "1"),
    "X_CT_COM_LanInterface1":("LAN3,LAN4,WLAN1", "2"),
    "PVC_OR_VLAN2":("", "3"),
    "X_CT_COM_MulticastVlan":("166","4")
}
