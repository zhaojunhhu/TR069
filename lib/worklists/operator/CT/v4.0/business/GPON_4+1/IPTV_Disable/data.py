#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：生成一个IPTV取消工单

    参数：
    | PVC_OR_VLAN | PVC:0/65 | ADSL上行用PVC格式,LAN\GPON\VDSL则用VLAN格式,默认是ADSL的PVC |


"""


# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
# PVC_OR_VLAN
"PVC_OR_VLAN":("PVC:0/65", "1")
}
