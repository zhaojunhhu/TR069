#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
    功能描述：生成一个SIP取消工单
    
    参数：
        | X_CT_COM_ServiceList | VOIP | WAN连接的服务模式,即X_CT-COM_ServiceList节点值,默认VOIP |
                           
            
    
    注意:如果X_CT-COM_ServiceList值找不到匹配的,则认为没有VOIP开通,所以不会执行取消工单,正常返回成功.
"""


# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
# X_CT_COM_ServiceList
"X_CT_COM_ServiceList":("VOIP", "1"),
}

