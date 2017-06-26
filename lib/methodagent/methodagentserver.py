#coding:utf-8

# /*************************************************************************
#  Copyright (C), 2012-2013, SHENZHEN GONGJIN ELECTRONICS. Co., Ltd.
#  module name: methodagentserver
#  function: MethodAgentServer,AcceptClientConnectControlThread
#            
#  Author: ATT development group
#  version: V1.0
#  date: 2013.8.29
#  change log:
#  wangjun  20130829    create
# ***************************************************************************

import time
import socket
import threading
import string
import datetime

#user denfine interface
from outputcontrol import ClientResponseHandle
from outputcontrol import ClientConnectCount
from methodsequencemanagement import MethodSequenceManagement
from methodnodemanagement import MethodNodeManagement
from dataprocess import MethondData, ParseRecvData

from constantdefinitions import METHOD_AGENT_SERVER_IP,\
                                METHOD_AGENT_SERVER_PORT, \
                                MAX_ONE_RECV_BUF_LENGTH, \
                                MAX_LISTEM_CONNECT_NUMBER, \
                                RECV_TIMEOUT_LENGTH, \
                                MESSAGE_TOTAL_LENGTH_DATA_SPLIT_STRING, \
                                CLIETN2SERVER_KEEPALIVE_DATA, \
                                SERVER2CLIETN_KEEPALIVE_DATA, \
                                CLIETN2SERVER_KEEPALIVE_INVALID_TIME_LENGTH

#import log
from constantdefinitions import DEBUG_FLAG
if DEBUG_FLAG:
    from outlog import OutLog as log
else:
    import TR069.lib.common.logs.log  as log
    

class MethodAgentServer(object):
    """
    TCP SOCKET服务器，处理来自TCL客户端发送的连接请求，同时将请求的处理分发给子进程处理。
    """
    
    def __init__(self, addr='localhost', port=50000):
        """
        初始化
        """
        self.addr = addr          # listen addr
        self.port = port          # listen port
        self.sock = None          # socket server object
        
        
    def start_socket_server(self):
        """
        启动TCP连接服务器，处理来自TCL客户端发送的连接请求，同时将请求的处理分发给子进程处理。
        """
        
        #检查SOCKET连接对象是否存在，如果存在则端口连接，并且重置SOCKET句柄。
        if self.sock:
            self.sock.close()
            self.sock = None
            
        #创建TCP SOCKET 服务器。
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((self.addr, self.port))
            self.sock.listen(MAX_LISTEM_CONNECT_NUMBER)
            
        except Exception, e:
            err_info = "Create socket server occurs exception:%s" % e
            log.debug_err(err_info)
            return
        
        log.debug_info("Socket server is start!")
        
        while 1:
            
            log.debug_info("Socket server:wait for client connection...")
            
            try:
                #阻塞等待客户端触发连接请求
                connection,address = self.sock.accept()
                
                log.debug_info("Socket server:accept client client connection")
                
                #更新连接接句柄总数，接收到一个client连接，接接句柄总数加一
                ClientConnectCount.updata_tcp_client_count_value(True)
                log.debug_info("Client connected handle count number=%d" % ClientConnectCount.get_tcp_client_count())

            except Exception, e:
                err_info = "Socket server accept occurs exception: %s" % e
                log.debug_err(err_info)
                break

            #接受一个连接
            try:
                #创建线程处理Client发送的消息数据
                thread_i = AcceptClientConnectControlThread(connection,address)
                thread_i.start()
                
            except Exception, e:
                #启动处理线程异常
                err_info = "Start accept client connect control thread occurs exception:%s" % e
                log.debug_err(err_info)

                #返回错误消息并继续等待其他客户端的连接
                ClientResponseHandle.send_error_info_data_to_client(connection,err_info)
                continue
            
    
    def stop_socket_server(self):
        """
        停止TCP 服务器
        """
        if self.sock:
            self.sock.close()
            self.sock=None
        


class AcceptClientConnectControlThread(threading.Thread):
    """
    对Client发送的消息数据处理
    """
    
    def __init__(self, conn, addr):
        """
        初始化
        """
        threading.Thread.__init__(self)
        
        self.conn = conn            # 保存Client的连接句柄
        self.addr = addr            # 保存Client的连接地址
        
        
    def run(self):
        """
        接收Client发送的消息数据，并且做初步解析，将消息请求分发到具体的消息处理模块
        """
        
        log.debug_info("\nClient connection request from address=%s,client port=%d" % (self.addr[0],self.addr[1]))
        
        data_all=None
        time_out_try_count=3
                
        log.debug_info("Begin recv data.")
        
        #接收第一个BUG MAX_ONE_RECV_BUF_LENGTH长度的数据
        data = self.conn.recv(MAX_ONE_RECV_BUF_LENGTH)
        log.debug_info( "\nRecv data buffer length=%d\n" % len(data) )
            
            
        #从第一个BUG中读取消息的有效数据长度
        message_total_length, split_data_pos=self.get_message_total_length(data)
        if (message_total_length>0 and split_data_pos<len(data)):
            
            #保存接收到的数据
            data_all = data[split_data_pos:]

            #检查是否有更多的数据需要接收
            self.conn.settimeout(RECV_TIMEOUT_LENGTH)

            while 1:
                
                #检查消息是否接收完成
                if (len(data_all)) >= message_total_length:
                    log.debug_info("Recv data complete.")
                    log.debug_info("Recv total data:%s\n" % data_all)
                    break
                
                try:
                    data = self.conn.recv(MAX_ONE_RECV_BUF_LENGTH)
                    
                    # 检查数据长度
                    if len(data):
                        log.debug_info( "\nRecv data buffer length=%d\n" % len(data) )

                        #保存接收到的数据
                        data_all += data
                        
                    else:
                        continue
                    
                except socket.timeout, e:
                    if time_out_try_count>0:
                        
                        time_out_try_count = time_out_try_count-1
                        log.debug_info("Reset recv data timeout length")
                        self.conn.settimeout(RECV_TIMEOUT_LENGTH)
                        
                        continue
                    
                    else:
                        log.debug_err("Recv data timeout")
                        break
                
                except Exception, e:
                    err_info = "Recv data occurs exception:%s" % e
                    log.debug_err(err_info)
                    break
            
            self.conn.settimeout(None)
            
            log.debug_info( "\nmessage total length=%d, split_data_pos=%d, data_all=%d\n" % (message_total_length, split_data_pos, len(data_all)) )
            
            #检查消息是否接收完成
            if (len(data_all)) != message_total_length:

                #接收消息数据不完整，丢弃此消息
                err_info = "Recv message occurs error, drop this message!"
                #返回错误消息       
                ClientResponseHandle.send_error_info_data_to_client(self.conn,err_info)
            else:
                
                #下发消息到消息处理流程
                message=data_all
                self.handle_message(message)
                
                #心跳包数据处理
                #3个心跳时间长度没有收到心跳，表示客户端连接断开，不在发送数据结果
                self.handle_listen_keepalive()
            
        else:
            #获取消息头消息总长度数据失败，丢弃此消息
            err_info = "Read message data total length occurs error, drop this message!"
            #返回错误消息       
            ClientResponseHandle.send_error_info_data_to_client(self.conn,err_info)
                
                
    def get_message_total_length(self,in_message_head):
        """
        取消息体有效数据长度
        """
        message_total_length=0
        split_data_pos=0
        
        #取消息体有效数据长度
        split_pos=in_message_head.find(MESSAGE_TOTAL_LENGTH_DATA_SPLIT_STRING)

        if split_pos:
            message_len_str=in_message_head[0:split_pos]
            
            try:
                message_total_length = string.atoi(message_len_str)
                log.debug_info("Client send message data total length=%d" % message_total_length)
                
            except Exception, e:
                err_info = "get_message_total_length occurs expection: %s" % e
                log.debug_err(err_info)
                message_total_length=0
        
        if message_total_length>0:
            split_data_pos = split_pos+len(MESSAGE_TOTAL_LENGTH_DATA_SPLIT_STRING)
        
        return message_total_length, split_data_pos
        
        
        
    def handle_message(self, message):
        """
        处理消息
        """
        #log.debug_info("Recv total data:%s\n" % message)
        
        try:
            #解析消息体数据
            tmp_sequence, \
            tmp_method_name, \
            tmp_cpe_id, \
            tmp_method_parameters_list=ParseRecvData.parse_recv_data(message)
            
        except Exception, e:
            #解析消息体数据异常
            err_info = "Parse recv message data occurs expection: %s" % e
            log.debug_err(err_info)
            
            #返回错误消息       
            ClientResponseHandle.send_error_info_data_to_client(self.conn,err_info)
            return False
        
        if None == tmp_sequence or None == tmp_method_name:
            
            #解析消息体数据异常
            err_info = "Parse recv message data fail"
            log.debug_err(err_info)
            
            #返回错误消息       
            ClientResponseHandle.send_error_info_data_to_client(self.conn,err_info)
            return False
        
        try:
            #保存addr,conn数据
            tmp_client_addr=self.addr[0]
            tmp_client_port=self.addr[1]
            tmp_client_conn_handle=self.conn
        
            #创建MethondData数据节点
            client_method_node_data_object=MethondData()
            client_method_node_data_object.set_method_data(tmp_client_addr,
                                                           tmp_client_port,
                                                           tmp_client_conn_handle,
                                                           tmp_sequence,
                                                           tmp_method_name,
                                                           tmp_cpe_id,
                                                           tmp_method_parameters_list)
            
            #管理消息处理状态
            insert_method_suc_flag=MethodSequenceManagement.\
                                 insert_method_sequence_obj(tmp_sequence,tmp_client_conn_handle)
            
            #当消息没有执行记录时，直接下放消息到消息节点管理模块
            if insert_method_suc_flag:
                #管理消息节点
                MethodNodeManagement.\
                        push_client_request_node_to_wait_run_buffer_list(client_method_node_data_object)
                
                return True
            
            else:
                log.debug_info("Sequence object(%s) is exist, waiting methond run result" % tmp_sequence)

        except Exception, e:
            err_info = "Push client request node to run buffer list occurs expection: %s" % e
            log.debug_err(err_info)
            
            #返回错误消息
            ClientResponseHandle.send_error_info_data_to_client(self.conn,err_info)
            return False
            
        return False


    def handle_listen_keepalive(self):
        
        time.sleep(3)
        log.debug_info( "Recv client keepalive data Begin")
        
        #心跳包数据处理
        #3分钟没有收到心跳，表示客户端连接断开，退出循环接收心跳数据包循环

        error_keepalive_count=0
        
        #初始化等待第一个心跳包的开始时间
        wait_recv_keepalive_time_object=datetime.datetime.now()   
                    
        #循环接收心跳数据包
        while 1:
            
            #获取当前系统时间
            temp_current_time_object=datetime.datetime.now()
            
            #检查心跳包间隔时间是否超出
            time_difference_seconds=(temp_current_time_object - wait_recv_keepalive_time_object).seconds
            #3分钟没有收到心跳，表示客户端连接断开，退出循环接收心跳数据包循环
            if time_difference_seconds >= (int)(CLIETN2SERVER_KEEPALIVE_INVALID_TIME_LENGTH):
                log.debug_info( "Client keepalive invalid, connection lost" )
                break
            
            try:
                #开始接收心跳包数据
                data = self.conn.recv(MAX_ONE_RECV_BUF_LENGTH)
                #log.debug_info( "Recv keepalive data=%s\n" % data )
                
            except Exception, e:
                #主动断开客户端连接或者客户端强制断开连接
                log.debug_info( "Recv keepalive data occurs error:%s\n" % e )
                break

            #通过数据分隔符分隔心跳包数据
            data_item_list=data.split(MESSAGE_TOTAL_LENGTH_DATA_SPLIT_STRING)
            print data_item_list
            if len(data_item_list) >= 2:
                data_keepalive_length= data_item_list[0]
                data_keepalive_string= data_item_list[1]
                
                if (int(data_keepalive_length) == len(data_keepalive_string) and
                    data_keepalive_string == CLIETN2SERVER_KEEPALIVE_DATA):

                    log.debug_info( "Read keepalive data SUC")
                    
                    #更新最后一次接收到心跳的时间
                    wait_recv_keepalive_time_object=datetime.datetime.now()
                    
                    #发送心跳响应到客户端
                    ClientResponseHandle.write_keepalive_data_to_client(self.conn,SERVER2CLIETN_KEEPALIVE_DATA)
                    
                else:
                    #解析消息失败，不匹配数据规则，丢弃此消息
                    log.debug_info( "Read keepalive data total length occurs error, drop this message!")

            else:
                #解析消息失败，不匹配数据规则，丢弃此消息
                log.debug_info( "Read keepalive data total length occurs error, drop this message!")
            
            time.sleep(20)
            
        log.debug_info( "Recv client keepalive data End")



def StartMethodAgentServer(in_ip,in_port):
    
    log.debug_info("Start method agent service...")
    
    #启动MethodAgentServer监听来自TCL客户端的消息请求
    try:
        log.debug_info ("Method Agent (ip=%s, port=%s) start." %(in_ip, in_port))
        
        ss_obj =MethodAgentServer(in_ip, in_port)
        ss_obj.start_socket_server()
        
    except Exception, e:
        err_info = "Method agent service occurs expection: %s" % e
        log.debug_err(err_info)
        
    finally:
        ss_obj.stop_socket_server()
        log.debug_info("Stop method agent service")
    
    nID = raw_input("Press any key to end...")



if __name__ == '__main__':
    StartMethodAgentServer(METHOD_AGENT_SERVER_IP, METHOD_AGENT_SERVER_PORT)
    
    
