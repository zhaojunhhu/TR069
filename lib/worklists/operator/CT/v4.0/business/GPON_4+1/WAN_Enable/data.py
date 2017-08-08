#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：生成一个WAN连接启用禁用工单,对于ADSL上行的CPE,根据PVC进行识别,
    对于LAN\GPON\VDSL上行的CPE,则根据VLAN进行识别.
    最多支持三条WAN连接的启用禁用操作,PVC_OR_VLAN为null时表示不对该WAN连接进行操作。
    
    参数：
    | PVC_OR_VLAN_1 | PVC:0/61 | 第一条WAN连接的PVC或VLAN,默认为ADSL的PVC值:PVC:0/61 |
    | Enable1     | 0 | 第一条WAN连接启用或禁用标识,默认为False表示禁用 |
    | PVC_OR_VLAN_2 | PVC:0/62 | 第二条WAN连接的PVC或VLAN,默认为ADSL的PVC值:PVC:0/62 |
    | Enable2     | 1 | 第二条WAN连接启用或禁用标识,默认为True表示启用 |
    | PVC_OR_VLAN_3 | null | 第三条WAN连接的PVC或VLAN,默认为null,表示不进行操作 |
    | Enable3     | 1 | 第三条WAN连接启用或禁用标识,默认为True表示启用 |
                           
            
    
    注意:由于Enable1、Enable2和Enable3值会直接下发给CPE,所以不做合法性判断.
    此工单只对PPPoE和桥的PVC或VLAN有效。
"""


# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
"PVC_OR_VLAN_1":("PVC:0/61", "1"),
"Enable1":("0", "2"),
"PVC_OR_VLAN_2":("PVC:0/62", "3"),
"Enable2":("1", "4"),
"PVC_OR_VLAN_3":("null", "5"),
"Enable3":("1", "6")
}
