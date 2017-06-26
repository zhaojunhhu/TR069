#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import  os
import  random
from    hashlib                     import  md5
from    base64                      import  b64encode
from    datetime                    import  datetime


import  httplib2
import  TR069.lib.common.logs.log   as      log
from    cpe_db                      import  *


CALL_METHOND_ERROR = 0         #调用方法失败
AUTHENTICATE_FAIL = -1         #认证失败
AUTHENTICTATE_SUCCEED = 200    #认证成功
NEED_AUTHENTICTAE = '401'           #没有认证

CPE_AUTH = 'acsauthmsg.cfg'       #ACS认证信息

class MyHttp(httplib2.Http):
    """
    继承自httplib2.Http类，主要目的是获取交互过程中request和response字段
    """
    # Add by lizn 2014-05-30
    def __init__(self, sn, cache=None, timeout=None, proxy_info=None,
                 ca_certs=None, disable_ssl_certificate_validation=False):
        httplib2.Http.__init__(self, cache, timeout, proxy_info, ca_certs, disable_ssl_certificate_validation)
        self.sn = sn    # 保存sn号
    
    def _request(self, conn, host, absolute_uri, request_uri, method, body, headers, redirections, cachekey):
        """Do the actual request using the connection object
        and also follow one level of redirects if necessary"""

        auths = [(auth.depth(request_uri), auth) for auth in self.authorizations if auth.inscope(host, request_uri)]
        auth = auths and sorted(auths)[0][1] or None
        if auth:
            auth.request(method, request_uri, headers, body)

        handle_request_head(headers, host, self.sn)     # 1 acs->cpe  out
        (response, content) = self._conn_request(conn, request_uri, method, body, headers)
        handle_response_head(response, self.sn)         # 1 cpe->acs  in

        if auth:
            if auth.response(response, body):
                auth.request(method, request_uri, headers, body)
                (response, content) = self._conn_request(conn, request_uri, method, body, headers )
                response._stale_digest = 1

        if response.status == 401:
            for authorization in self._auth_from_challenge(host, request_uri, headers, response, content):
                authorization.request(method, request_uri, headers, body)
                handle_request_head(headers, host, self.sn)    # 2 acs->cpe  out
                (response, content) = self._conn_request(conn, request_uri, method, body, headers, )
                handle_response_head(response, self.sn)        # 2 cpe->acs  in
                if response.status != 401:
                    self.authorizations.append(authorization)
                    authorization.response(response, body)
                    break

        if (self.follow_all_redirects or (method in ["GET", "HEAD"]) or response.status == 303):
            if self.follow_redirects and response.status in [300, 301, 302, 303, 307]:
                # Pick out the location header and basically start from the beginning
                # remembering first to strip the ETag header and decrement our 'depth'
                if redirections:
                    if not response.has_key('location') and response.status != 300:
                        raise RedirectMissingLocation( _("Redirected but the response is missing a Location: header."), response, content)
                    # Fix-up relative redirects (which violate an RFC 2616 MUST)
                    if response.has_key('location'):
                        location = response['location']
                        (scheme, authority, path, query, fragment) = parse_uri(location)
                        if authority == None:
                            response['location'] = urlparse.urljoin(absolute_uri, location)
                    if response.status == 301 and method in ["GET", "HEAD"]:
                        response['-x-permanent-redirect-url'] = response['location']
                        if not response.has_key('content-location'):
                            response['content-location'] = absolute_uri
                        httplib2._updateCache(headers, response, content, self.cache, cachekey)
                    if headers.has_key('if-none-match'):
                        del headers['if-none-match']
                    if headers.has_key('if-modified-since'):
                        del headers['if-modified-since']
                    if response.has_key('location'):
                        location = response['location']
                        old_response = copy.deepcopy(response)
                        if not old_response.has_key('content-location'):
                            old_response['content-location'] = absolute_uri
                        redirect_method = method
                        if response.status in [302, 303]:
                            redirect_method = "GET"
                            body = None
                        (response, content) = self.request(location, redirect_method, body=body, headers = headers, redirections = redirections - 1)
                        response.previous = old_response
                else:
                    raise RedirectLimit("Redirected more times than rediection_limit allows.", response, content)
            elif response.status in [200, 203] and method in ["GET", "HEAD"]:
                # Don't cache 206's since we aren't going to handle byte range requests
                if not response.has_key('content-location'):
                    response['content-location'] = absolute_uri
                httplib2._updateCache(headers, response, content, self.cache, cachekey)

        return (response, content)

def handle_request_head(headers, host, sn):
    #log.app_info(str(headers))
    headers_ex = 'Host: %s\r\n' % host
    if headers:
        for k, v in headers.iteritems():
            header = '%s: %s\r\n' % (k.title(), v)
            headers_ex += header
        headers_ex += '\r\n'
    #log.app_info(headers_ex)
    
    insert_acs_soap("connection request", "OUT", sn, str(headers), headers_ex)
        
def handle_response_head(response, sn):
    #log.app_info(str(response))
    headers_ex = ''
    list_headers = []
    if response:
        if response.version == 11:
            http_ver = 'HTTP/1.1'
        else:
            http_ver = 'HTTP/1.0'
        header = '%s %s %s' % (http_ver, response.status, response.reason)
        list_headers.append(header)
        for k, v in response.iteritems():
            if k == 'status':
                continue
            header = '%s: %s' % (k.title(), v)
            list_headers.append(header)
        headers_ex = '\r\n'.join(list_headers) + '\r\n\r\n'
    #log.app_info(headers_ex)
    
    insert_acs_soap("connection request", "IN", sn, str(response), headers_ex)

def get_url(sn, url, username, password):
    """
    """
    from cpe import CPE
    
    ret             = AUTHENTICATE_FAIL
    ret_api         = None
    err_messsage    = ""
    soap_id         = 0

    desc = "begin get url(url=%s, username=%s, password=%s)." %(url, username, password)
    log.app_info(desc)
    if (not sn):
        err_messsage = "The sn is not exist"
        log.app_info(err_messsage)
        
        return AUTHENTICATE_FAIL, err_messsage

    if (not url):
        err_messsage = "The url is not exist(need inform?)"
        log.app_info(err_messsage)
        
        return AUTHENTICATE_FAIL, err_messsage


    # nwf 2013-06-09; retry 3times if error(10060 or 10065)
    for i in [1, 2]:
        
        try:
            #conn = httplib2.Http(timeout = 60)
            conn = MyHttp(sn, timeout=60)   # Alter by lizn 2014-05-30
            conn.add_credentials(username, password)

            # mysql ; first
            cpe = CPE.get_cpe(sn)
            
            time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cpe.cpe_soap.time_s1_start = time
            # Alter by lizn 2014-03-11
            
            # mysql ------------- out
            content = "username=%s; password=%s; url=%s" %(username, password, url)
            #insert_acs_soap("connection request", "OUT", sn, content)   by lizn 2014-05-30
                        
            ret_api, data = conn.request(url)

            # mysql -------------- in
            content = str(ret_api) + "\n\n" + data
            #soap_id = insert_acs_soap("connection request", "IN", sn, content)  by lizn 2014-05-30
          

            # mysql ; first end
            time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cpe.cpe_soap.time_s1_finish = time
            # Alter by lizn 2014-03-11
            
            status = ret_api.status
            conn.close()
            if status == AUTHENTICTATE_SUCCEED:
                err_messsage = "Get cpe url(url=%s, username=%s, password=%s) success." %(url, username, password)
                log.app_info(err_messsage)

                ret = AUTHENTICTATE_SUCCEED
                break
            else:
                err_messsage = "Get cpe url(url=%s, username=%s, password=%s) not pass." %(url, username, password)
                log.app_info(err_messsage)

                ret = AUTHENTICATE_FAIL
                break
            
        except Exception, e:
            err_messsage = "Get cpe url(url=%s, username=%s, password=%s) fail:%s." %(url, username, password, e)
            log.app_err(err_messsage)

            # friendly tip
            err_messsage = "Get cpe url(url=%s, username=%s, password=%s) fail:connect to cpe fail." %(url, username, password)

            try:
                # retry 
                if ((e.errno == 10060) or (e.errno == 10065)):
                    continue
            except Exception:
                pass

            # other error, fail
            ret = AUTHENTICATE_FAIL
            break
            
    return ret, err_messsage
    

if __name__ == '__main__':
    url = 'http://192.168.1.1:30005'
    sn = 'admin'
    #url = 'http://127.0.0.1:8800'
    print get_url(url, sn)
    