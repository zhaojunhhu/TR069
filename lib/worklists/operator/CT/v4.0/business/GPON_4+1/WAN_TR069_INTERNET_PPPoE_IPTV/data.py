#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：生成一个TR069混合上网新装工单，在同一VLAN内新建桥接连接开通IPTV业务。

    参数：
    | PVC_OR_VLAN           | PVC:0/65 | ADSL上行用PVC格式,LAN\GPON\VDSL则用VLAN格式,默认是ADSL的PVC |
    | Username              | tw1 | 拨号上网的帐号,默认tw1 |
    | Password              | tw1 | 拨号上网的密码,默认tw1 |
    | X_CT_COM_LanInterface | LAN1 | 绑定LAN端口,默认LAN1,可以为LAN1,LAN2,LAN3,LAN4,WLAN1,WLAN2,WLAN3,WLAN4 |     
    | WANEnable_Switch      | True | WAN连接使能与WAN连接参数是否一起下发,True表示一起下发.默认为True |
    | X_CT_COM_MulticastVlan  | 165 | 公共组播VLAN(注意:如果此参数值为"null",则表示不下发组播VLAN节点.) |
    
            
    
    注意:此工单的脚本中固定是PPPoE的WAN连接,X_CT-COM_ServiceList为"TR069,INTERNET",
    绑定端口则根据不同的CPE设备类型而不同.
"""


# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
    "PVC_OR_VLAN":("PVC:0/65","1"), 
    "Username":("tw1","2"), 
    "Password":("tw1","3"), 
    "X_CT_COM_LanInterface":("LAN1","4"),  
    "WANEnable_Switch":("True","5"),
    "X_CT_COM_MulticastVlan":("165","6")
}
