#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：在TR069属性连接的同一PVC内开通桥接上网业务

    参数：
    | PVC_OR_VLAN           | PVC:0/63 | ADSL上行用PVC格式,LAN\GPON\VDSL则用VLAN格式,默认是ADSL的PVC |
    | X_CT_COM_LanInterface | LAN3,LAN4,WLAN1 | 绑定LAN端口,默认LAN3,LAN4,WLAN1 |
    
            
    
    注意：此工单需要依赖于一条TR069 WAN连接，否则会失败
"""


# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
    "PVC_OR_VLAN":("PVC:0/63", "1"),
    "X_CT_COM_LanInterface":("LAN3,LAN4,WLAN1", "2"),    
}
