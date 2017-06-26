#coding:utf-8


# -----------------------------doc--------------------------
# 工单 描述
WORKLIST_DOC = """
功能描述：生成一个全球眼取消工单
    
    参数：
    | ExternalPort        | 8006 | 外部端口,默认8006 |    
    | InternalPort        | 80 | 内部端口,默认80 |   
    | PortMappingProtocol | TCP | 端口映射的协议,默认TCP |  
    | InternalClient      | 192.168.1.100 | 设备在网关下的地址,默认192.168.1.100 |
      
       
    
    注意:此工单依赖于有一条PPPoE的INTERNET连接,否则会失败
"""


# -----------------------------args--------------------------
# 工单 参数
WORKLIST_ARGS = {
"ExternalPort":("8006", "1"),
"InternalPort":("80", "2"),
"PortMappingProtocol":("TCP", "3"),
"InternalClient":("192.168.1.100", "4")
}
