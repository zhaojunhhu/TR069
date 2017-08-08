# coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：生成一个WAN连接修改工单,对于ADSL上行的CPE,根据PVC进行修改,
    对于LAN\EPON\VDSL上行的CPE,则根据VLAN进行修改.
    最多支持三条WAN连接的修改操作,PVC_OR_VLAN为null时表示不对该WAN连接进行操作。
    
    参数：
    | PVC_OR_VLAN_1 | PVC:0/61 | 第一条WAN连接的PVC或VLAN,默认为ADSL的PVC值:PVC:0/61 |
    | ChangeTo1     | PVC:0/71 | 第一条WAN连接修改后的PVC或VLAN ,默认为ADSL的PVC值:PVC:0/71 |
    | PVC_OR_VLAN_2 | PVC:0/62 | 第二条WAN连接的PVC或VLAN,默认为ADSL的PVC值:PVC:0/62 |
    | ChangeTo2     | PVC:0/72 | 第二条WAN连接修改后的PVC或VLAN,默认为ADSL的PVC值:PVC:0/72 |
    | PVC_OR_VLAN_3 | null | 第三条WAN连接的PVC或VLAN,默认为null,表示不进行操作 |
    | ChangeTo3     | PVC:0/73 | 第三条WAN连接启用或禁用标识,默认为ADSL的PVC值:PVC:0/73 |
    
            
    
    注意：此工单只对PPPoE和桥的PVC或VLAN有效。
"""

# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
    "PVC_OR_VLAN_1": ("PVC:0/61", "1"),
    "ChangeTo1": ("PVC:0/71", "2"),
    "PVC_OR_VLAN_2": ("PVC:0/62", "3"),
    "ChangeTo2": ("PVC:0/72", "4"),
    "PVC_OR_VLAN_3": ("null", "5"),
    "ChangeTo3": ("PVC:0/73", "6")
}
