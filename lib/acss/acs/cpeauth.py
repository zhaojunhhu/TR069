#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#***********************************************
# 模块名称：HTTPCONTROL::HTTPAuth
# 模块功能：提供服务端和客户端的HTTP认证功能
#***********************************************
import os
from urlparse import urlparse
from hashlib import md5
from base64 import b64encode
import time
import random

import TR069.lib.common.logs.log as log 

ACS_NO_AUTHENTICATION = 0          #没有CPE请求没有authentication头
ACS_AUTHENTICATION_TYPE_ERROR = -1  #CPE请求authentication类型错误
ACS_AUTHENTICATION_NAME_ERROR = -2  #CPE请求头用户名错误
ACS_AUTHENTICATE_FAIL = -3         #ACS对CPE请求证失败
ACS_AUTHENTICATE_PASS = 1          #ACS对CPE请求认证通过
CALL_METHOD_ERROR = -9             #调用函数错误

ACS_AUTH_CFG = "cpeauthmsg.cfg"


def authenticate_baisc_cperequest(dict_acs_option, dict_acs_option2, request_class, sn):
    """
    用于对CPE的HTTP请求进行baisc认证
    """
    
    log.run_info("Begin baisc Auth")
    dict_cperequest_header = request_class.getAllHeaders()
    realm = dict_acs_option.get('realm','tr069 basic realm')
    dict_acs_option['realm'] = realm
    
    #检查CPE认证http头中是否包含authorization字段
    if 'authorization' in dict_cperequest_header:
        #对aauthorization字段中信息解码分别赋值在cpe_auth_type和cpe_message中
        cpe_auth_type = dict_cperequest_header['authorization'].split(' ')[:1][0]
        cpe_message = dict_cperequest_header['authorization'].split(' ')[1:][0]
        #检查CPE认证类型是否为Basic
        if 'Basic' == cpe_auth_type:
            #调用check_baisc_auth()检查CPE认证信息
            if check_basic_auth(dict_acs_option, cpe_message) == ACS_AUTHENTICATE_PASS:
                result = ACS_AUTHENTICATE_PASS
                return result
            else:
                dict_acs_option["username"] = dict_acs_option2["username"]
                dict_acs_option["password"] = dict_acs_option2["password"]                  
                if check_basic_auth(dict_acs_option, cpe_message) == ACS_AUTHENTICATE_PASS:
                    result = ACS_AUTHENTICATE_PASS
                    dict_acs_option2["is_default"] = True
                    return result                
                else:
                    result = ACS_AUTHENTICATE_FAIL
                
        else:
            result = ACS_AUTHENTICATION_TYPE_ERROR
    else:
        result = ACS_NO_AUTHENTICATION
        
    if ACS_NO_AUTHENTICATION == result:
     #没有认证信息，调用baisc_challenge（）给CPE返回401 
        message = baisc_challenge(dict_acs_option,request_class)
        if CALL_METHOD_ERROR == message:
            log.run_info("Call baisc_challenge method error")
            return  CALL_METHOD_ERROR
        else:
            return ACS_NO_AUTHENTICATION
        return baisc_challenge(dict_acs_option,request_class,message)
     
    else:
    #认证失败返回401错误
        request_class.setResponseCode(401,'Unauthorized')
         
        return ACS_AUTHENTICATE_FAIL


def try_username_password(dict_cperequest_authheader, dict_acs_option):
    """
    nwf 2013-05-08
    """
    
    #检查CPE认证用户名是否和ACS选项用户名一致
    if dict_cperequest_authheader['username'] == dict_acs_option['username']:
        
        #检查CPE的认证信息的其他字段（qop,nonce,response）
        try:
            result = check_digest_auth(dict_acs_option,dict_cperequest_authheader)
            #认证通过返回 ACS_AUTHENTICATE_PASS
            if result == ACS_AUTHENTICATE_PASS:
                return result    
        except Exception,e:
            log.run_info('call check_digest_auth error,message:%s'%e)
            return ACS_AUTHENTICATE_FAIL
    else:
        result = ACS_AUTHENTICATION_NAME_ERROR
        
    return result


def authenticate_digest_cperequest(dict_acs_option, dict_acs_option2, request_class,sn):
    """
    用于对CPE的HTTP请求进行digest认证
    """
    log.run_info("Begin digest Auth")
    dict_cperequest_header = request_class.getAllHeaders()
    realm = dict_acs_option.get('realm','tr069')
    dict_acs_option['realm'] = realm
    
    #检查CPE的http头信息是否包含Authorization字段
    if 'authorization' in dict_cperequest_header:
    
        #对CPE的消息头进行解析，保存相关数据到dict_cperequest_authheader
        dict_cperequest_authheader = get_data(dict_cperequest_header['authorization'])
        dict_cperequest_authheader['method'] = request_class.method
        
        #检查CPE认证信息类型是否为Digest
        if 'Digest' == dict_cperequest_authheader['digest_type']:
            
            result = try_username_password(dict_cperequest_authheader, dict_acs_option)
            if result == ACS_AUTHENTICATE_PASS:
                return result             
            else:
                dict_acs_option["username"] = dict_acs_option2["username"]
                dict_acs_option["password"] = dict_acs_option2["password"]             
                result = try_username_password(dict_cperequest_authheader, dict_acs_option)
                if result == ACS_AUTHENTICATE_PASS:
                    dict_acs_option2["is_default"] = True
                    return result  
                
        else:
            result = ACS_AUTHENTICATION_TYPE_ERROR
    else:
        result = ACS_NO_AUTHENTICATION
       
    if ACS_NO_AUTHENTICATION == result:
        #没有认证信息调用digest_challenge
        message = digest_challenge(dict_acs_option,request_class,sn)
        if message == CALL_METHOD_ERROR:
            log.run_info("Call digest_challenge method error")
            result = CALL_METHOD_ERROR
        else:
            return ACS_NO_AUTHENTICATION 
    else:
        #认证失败返回cpe 401错误信息
        request_class.setResponseCode(401,'Unauthorized')
        return result
      
def authenticate_acs_cperequest(request_class, sn, dict_acs_option, dict_acs_option2):
    """
    根据CPE sn号判断当前读取当前CPE的配置信息
    """
    
    #判断是否需要认证
    if dict_acs_option.get("auth_type") == "None":   # acs rf tr069gui 统一为不认证为str的"None" zsj 2013/11/20
        return ACS_AUTHENTICATE_PASS
    auth_type = dict_acs_option.get('auth_type', None)
    
    #判断ACS认证类型是否为digest或者baisc，不是设置为digest
    if auth_type != 'digest' and auth_type != 'basic':  
        dict_acs_option['auth_type'] = 'digest'
            
    #ACS认证类型为digest则调用authenticate_digest_cperequest()进行认证
    if dict_acs_option['auth_type'] == 'digest':
        message = authenticate_digest_cperequest(dict_acs_option, dict_acs_option2, request_class, sn)
 
    #ACS认证类型为baisc则调用authenticate_baisc_cperequest()进行认证        
    else:                              
        message = authenticate_baisc_cperequest(dict_acs_option, dict_acs_option2, request_class, sn)
        
    if message == ACS_AUTHENTICATE_PASS:
        log.run_info('*********Authention Succeed!*********')
        return ACS_AUTHENTICATE_PASS
    elif message == ACS_NO_AUTHENTICATION:
        log.run_info("Cpe soap not have authentication")
        return ACS_NO_AUTHENTICATION
    else:
        log.run_info('*********Authention FAIL**********')
        return ACS_AUTHENTICATE_FAIL

def check_basic_auth(dict_acs_option,message):
    """
    对CPE请求信息进行Baisc认证
    """
    username = dict_acs_option['username']
    password = dict_acs_option['password']
    
    string = username+':'+password
    auth = b64encode(string)
    
    if auth == message:
        return ACS_AUTHENTICATE_PASS
    else:
        return ACS_AUTHENTICATE_FAIL
    
def create_baisc_header(dict_acs_option):
    """
    构造baiscr认证的WWW-Authenticate字段值
    """
    username = dict_acs_option['username']
    password = dict_acs_option['password']
    
    string = username+':'+password
    auth = "Basic" + " "+ 'realm="%s"' % dict_acs_option["realm"]
    
    return auth

def baisc_challenge(dict_acs_option,request_class):
    """
    构建baisc认证返回信息
    """
    header = 'WWW-Authenticate'
    message = 'Unauthorized'
    header_value = create_baisc_header(dict_acs_option)
    
    try:
        request_class.setResponseCode(401,message)
        request_class.setHeader(header,header_value)
        
        log.run_info('send WWW-Authenticate response succeed')
    
    except Exception:
        log.run_info('send WWW-Authenticate response error')
        return CALL_METHOD_ERROR
        
def create_nonce(realm):
    """
       根据realm创建nonce
    """
    return md5("%d:%s" % (time.time(), realm)).hexdigest()
    
def create_opaque(realm):
    """
       根据realm创建opaque
    """
    return md5("%d%s" % (time.time(), realm)).hexdigest()

def create_header(dict_acs_option,sn):
    """
       创建认证错误信息头
    """
    realm = dict_acs_option['realm']
    nonce = create_nonce(realm)
    opaque = create_opaque(realm)
    qop = 'auth'
    auth_type = 'Digest'
    
    return '%s realm="%s", nonce="%s", opaque="%s", qop="%s"' % (auth_type,realm,nonce,opaque,qop)
    
def digest_challenge(dict_acs_option,request_class,sn):
    """
       Digest认证错误或没有认证信息，返回401信息
    """
    header = 'WWW-Authenticate'
    header_value = create_header(dict_acs_option,sn)

    #调用http模块的setResponseCod和sendHttpHeader发送错误信息
    if header_value == CALL_METHOD_ERROR:
        log.run_info('create WWW-Authenticate header error')
        return CALL_METHOD_ERROR
    
    try:
        request_class.setResponseCode(401,'Unauthorized')
        request_class.setHeader(header,header_value)
        log.run_info('send WWW-Authenticate response succeed')
        return  
    except Exception:
        log.run_info('send WWW-Authenticate response error')
        return  CALL_METHOD_ERROR
      
    
def get_data(request_message):
    """
    解析authentication头信息，保存在dict_request_message中并返回
    """
    #认证类型在第一字段解析第一字段保存在dict_request_message中
    index = request_message.find(' ')
    dict_request_message = {}
    dict_request_message['digest_type'] = request_message[:index]
    
    #认证类型在第二字段解析第一字段保存在dict_request_message中
    list_data = request_message[index:].split(',')
    for x in list_data:
        x = x.strip()
        index_bagin = x.find('=')+2
        index_end = x.find('=')
        
        #对不同类型采取不同保存方式，主要针对nc=00000001
        if x.find('"') >= 0:    
            dict_request_message[x[:index_end]]=x[index_bagin:-1]
        else:
            index_bagin = x.find('=')+1
            dict_request_message[x[:index_end]]=x[index_bagin:]
    #返回authentication头信息为dict数据类型
    return dict_request_message
    
def check_digest_auth(dict_acs_option,request_data):
    """
    检查CPE digest认证的各字段
    """
    
    #检查CPE认证信息中的realm和ACS Options是否一致
    if dict_acs_option['realm'] == request_data['realm']:
        if request_data['response'] == create_response(dict_acs_option,
                                                       request_data):
            return ACS_AUTHENTICATE_PASS
    #认证失败返回-1
    else:
        return ACS_AUTHENTICATE_FAIL
    
def create_response(dict_acs_option,message):
    """
    根据ACS OPtion和CPE认证信息，构造CPE response字段的检查信息
    """
    data = dict_acs_option
    if 'qop' not in message:
        A11 = A1(message,data)
        A21 = A2(message,data)
        response = KD(H(A11),message['nonce']+H(A21))
        return response
    
    elif message['qop'] == 'auth' or message['qop'] == 'auth-int':
        A11 = A1(message,data)
        A21 = A2(message,data)
        response = KD(H(A11),message['nonce']+':'+message['nc']+':'+message['cnonce']+
                      ':'+message['qop']+':'+H(A21))
        return response

def H(s):
    return md5(s).hexdigest()

def KD(secret, data):
    return H(secret + ':' + data)

def A1(message,data):
    """
    如果CPE回复的信息中algorithm的值为MD5或者没有提供
        则A1返回就为username:realm:password
    如果algorithm的值为MD5-sess
        则A1返回就为H(username:realm:password):nonce:cnonce
    """  
    #message为CPE认证信息，data为ACS Optionx信息
    username = data['username']
    password = data['password']
    realm = data['realm']
    nonce = message['nonce']
    cnonce = message['cnonce']
    algorithm = message.get('algorithm', None)
    #检查CPE认证信息中是否包含algorithm字段，fg根据algorithm返回不同的结果
    if algorithm == 'MD5' or algorithm == None:
        return "%s:%s:%s" % (username, realm, password)
        
    elif algorithm == 'MD5-sess':
        str_1 = username+':'+realm+':'+password
        return H(str_1)+':'+nonce+':'+cnonce
    else:
        return "%s:%s:%s" % (username, realm, password)
        

def A2(message,data):
    """
    如果CPE回复信息中有qop值为'auth'h或不c存在
        则A2返回结果为method：digest_uri
    如果qop值为'auth_int'
        则A2发回method:digest_uri_H(enting_body)
    """ 
    #message为CPE认证信息，data为ACS Optionx信息
    method = message['method']
    uri = message['uri']
    qop = message.get('qop', None)
    if qop == 'auth' or qop == None:
        return method + ':' + uri
    else:
        return method+':'+uri+':'+H(body)

    
if __name__ == '__main__':
    pass
