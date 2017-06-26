#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：取消服务类型为Internet的PPPoE接入方式的上网业务工单；
    若不需要检查X_CT_COM_LanInterface，则将其配置为null。
    
    
    参数：
    | PVC_OR_VLAN           | PVC:0/65 | ADSL上行用PVC格式,LAN\EPON\VDSL则用VLAN格式,默认是ADSL的PVC   |
    | X_CT_COM_LanInterface | null | 绑定LAN端口,默认为null,表示不检查X_CT_COM_LanInterface        |
    
    
            
"""


# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
       "PVC_OR_VLAN":("PVC:0/65","1"),
       "X_CT_COM_LanInterface":("null","2")
}
