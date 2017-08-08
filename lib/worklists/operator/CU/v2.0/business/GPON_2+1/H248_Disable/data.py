# coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：生成一个H248取消工单

    参数：
    | X_CU_ServiceList | VOIP | WAN连接的服务模式,即X_CT-COM_ServiceList节点值,默认VOIP |
     
      
"""

# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
    "X_CU_ServiceList": ("VOIP", "1"),
}
