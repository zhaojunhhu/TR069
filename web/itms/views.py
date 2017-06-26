#coding:utf-8
import re
import sys
import time
from datetime                   import datetime, timedelta

from django.conf                import settings
from django.shortcuts           import render
from django.shortcuts           import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions     import PermissionDenied, ViewDoesNotExist, ObjectDoesNotExist
#from django.utils               import simplejson
import json

# Create your views here.
from django.http                import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.http                import Http404, HttpResponseNotFound, HttpResponseBadRequest
from django.template            import Context, loader
from django.template            import RequestContext
from django.core.urlresolvers   import reverse

from db_handle                  import *
from models                     import CPE, RPC
from models                     import Worklist, WorklistEx
from models                     import SOAP, SoapEx
from django_log                 import ProcessOutLog as log

# tr069
from                            tr069_browser import g_TR069_browser


from upgrade.tr069servermanagement import Tr069servermanagement
from upgrade.webservermanagement   import Webservermanagement

g_TR069_server_control = Tr069servermanagement()
g_Web_server_control = Webservermanagement()


LIST_NO_ARGS_RPC_METHODS = ["GetQueuedTransfers",
                            "FactoryReset",
                            "GetAllQueuedTransfers",
                            "GetRPCMethods"
                            ]

LIST_NOT_NEED_DEAL_ARGS_METHODS = ["GetParameterNames",
                                   "AddObject",
                                   "DeleteObject",
                                   "Reboot",
                                   "Download",
                                   "Upload",
                                   "ScheduleInform",
                                   "GetOptions",
                                   "CancelTransfer",
                                  ]

# creat by zsj
def deco_check_login(func):
    """
    函数功能：添加对访问页面的登录检查装饰器，如未登录先登录在跳转
    函数参数：
        func：要检查登录的函数
    """
    def _deco_check_login(*args, **kwargs):
        request = args[0]
        if not request.user.is_authenticated():
            next_url = request.path
            redirect_url = r'/login/?next=%s' % next_url
            return HttpResponseRedirect(redirect_url)

        return func(*args, **kwargs)

    return _deco_check_login

# creat by zsj
def deco_rpc_process(func):
    """
    函数功能：添加执行rpc方法的装饰器
    函数参数：
        func：要执行的rpc方法函数
    """
    def _rpc_process(*args, **kwargs):

        func_name = func.__name__

        request   = args[0]
        path      = request.path
        revert    = path.split('/')[4]
        worklist_id    = path.split('/')[5]
        cpe_id    = get_cpe_id(path)
        cpe       = CPE.objects.get(cpe_id=cpe_id)

        cpe.rpc_exec_result  = ""
        cpe.rpc_error_code   = ""
        cpe.rpc_error_des    = ""


        return render_to_response('itms/%s.html' % func_name, {'cpe':cpe,'revert': revert,'worklist_id':worklist_id})

    return _rpc_process

def get_cpe_id(url_path):
    """
    函数功能：获取用户提交路径中的数字编号
    参数：
        url_path： 用户提交路径
    """
    temp = re.search("\d+", url_path)
    if temp:
        return temp.group(0)
    else:
        return None

@deco_check_login
def login_success(request):
    """
    用户登录成功页面
    """
    #pic_path = '/static'
    user_name = request.user.get_username()
    utc_time = request.user.last_login
    last_login = (utc_time + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    #last_login = utc_time.replace(hour=utc_time.hour + 8).strftime('%Y-%m-%d %H:%M:%S')
    remote_addr = request.META['REMOTE_ADDR']

    dict_perms = {}
    #if request.user.has_perm('user_manager.can_upload'):
    #    dict_perms['/itms/upload_page/'] = u'上传下载'

    if request.user.has_perm('user_manager.can_testcase'):
        dict_perms['/itms/inquirycpe/'] = u'远程操作'

    if request.user.has_perm('user_manager.can_config'):
        dict_perms['/server/manage/'] = u'服务器管理'

    #if request.user.has_module_perms('auth'):
    #    dict_perms['/user/manage/'] = u'权限管理'

    list_user_perms = dict_perms.items()
    # list_user_perms.sort()

    web_version = g_Web_server_control.get_cur_ver()
    tr069_version = g_TR069_server_control.get_cur_ver()

    #assert False
    return render_to_response('itms/loginsuccess.html', locals(), context_instance=RequestContext(request))

@deco_check_login
def go_to_server_manage(request, message=""):
    """
    函数功能：访问服务器管理界面
    """
    if not request.user.has_perm('user_manager.can_config'):    # 没有服务器管理的权限
        raise PermissionDenied
        # return HttpResponseForbidden('<h1>403 Forbidden</h1>')

    #add by jias 20140626
    #TR069_server状态 True表示启动
    ret = g_TR069_server_control.get_server_state()
    #ret=True(启动状态)butten表示停止功能
    tr069_state = u"当前停止状态，点击启动" if not ret else u"当前启动状态，点击停止"

    #当前状态
    tr069_current_version = g_TR069_server_control.get_cur_ver()
    #可用版本列表
    list_tr069_version = g_TR069_server_control.get_useable_vers()

    #无效， 未被使用
    web_state  = "start(Not Required)"
    #当前状态
    web_current_version = g_Web_server_control.get_cur_ver()
    #可用版本列表
    list_web_version = g_Web_server_control.get_useable_vers()

    info_dict = {"tr069_state":tr069_state,
                "web_state":web_state,
                "tr069_current_version":tr069_current_version,
                "web_current_version":web_current_version,
                "list_tr069_version":list_tr069_version,
                "list_web_version":list_web_version,
                "message":message,
                }

    log.debug_info("go_to_server_manage info_dict:%s" % str(info_dict))

    t = loader.get_template('itms/manageserver.html')
    c = Context(info_dict)
    return HttpResponse(t.render(c))

@deco_check_login
def start_or_stop_server(request, server_name):
    """
    函数功能:对服务器的开启和关闭的请求处理
    """
    log.debug_info("start_or_stop_server: server_name %s" % (server_name))
    #add by jias 20140626
    message = u""
    succ_log = u"成功。"
    fail_log = u"失败:请查看log获取详细信息。"
    if "TR069" in server_name:

        if g_TR069_server_control.get_server_state():

            log.debug_info("stop_server  %s" % server_name)
            ret = g_TR069_server_control.stop_server()

            strstate = succ_log if ret else fail_log
            message = u"停止%s服务%s"%(server_name, strstate)
        else:

            log.debug_info("start_server  %s" % server_name)
            ret = g_TR069_server_control.start_server()

            strstate = succ_log if ret else fail_log
            message = u"启动%s服务%s"%(server_name, strstate)

    elif "WEB" in server_name:

        if g_Web_server_control.get_server_state():

            log.debug_info("stop_server  %s" % server_name)
            g_Web_server_control.stop_server()

            message = u"停止%s服务完成。"%server_name
        else:

            log.debug_info("start_server  %s" % server_name)
            g_Web_server_control.start_server()

            message = u"启动%s服务完成。"%server_name
    else:

        log.debug_info("server_name err: %s  " % server_name)
        pass

    return go_to_server_manage(request, message)

@deco_check_login
def upgrade_server(request, server_version, server_name):
    """
    函数功能：对服务器的升级请求处理
    """
    log.debug_info("upgrade_server:server_name %s, server_version %s" % (server_name, server_version))

    #add by jias 20140626
    message = u""
    if "TR069" in server_name:

        if g_TR069_server_control.need_upgrade(server_version):

            log.debug_info("upgrade  %s" % server_name)
            g_TR069_server_control.upgrade(server_version)  #server_version 可以为None

            message = u"升级%s完成。"%server_name
        else:

            log.debug_info("not need upgrade  %s" % server_name)

    elif "WEB" in server_name:

        if g_Web_server_control.need_upgrade(server_version):

            log.debug_info("not need upgrade  %s" % server_name)
            g_Web_server_control.upgrade(server_version)

            message = u"升级%s完成。"%server_name
        else:

            log.debug_info("not need upgrade  %s" % server_name)
    else:

        log.debug_info("server_name err: %s  " % server_name)
        pass

    return go_to_server_manage(request, message)

@deco_check_login
def upload_page(request):
    """
    """
    if not request.user.has_perm('user_manager.can_upload'):    # 没有上传下载的权限
        raise PermissionDenied
        # return HttpResponseForbidden('<h1>403 Forbidden</h1>')

    list_user_perms = [('/itms/upload_page/', u'上传下载')]
    return render_to_response('itms/upload_page.html', locals(), context_instance=RequestContext(request))

@deco_check_login
def inquiry_cpe(request):
    """
    CPE查询页面
    """

    if not request.user.has_perm('user_manager.can_testcase'):    # 没有测试用例的权限
        raise PermissionDenied
        # return HttpResponseForbidden('<h1>403 Forbidden</h1>')

    inquiry_type = 'all'
    input_sn = ''
    inquiry_page = 1
    list_user_perms = [('/itms/inquirycpe/', u'远程操作')]
    return render_to_response('itms/inquirycpe.html', locals(), context_instance=RequestContext(request))


@deco_check_login
def inquiry_tasklist(request,revert):
    """
    设备任务列表初始页面
    """

    if not request.user.has_perm('user_manager.can_testcase'):    # 没有测试用例的权限
        raise PermissionDenied
        # return HttpResponseForbidden('<h1>403 Forbidden</h1>')
    inquiry_type = 'all'
    input_start_time = ''
    input_finish_time = ''
    inquiry_page = 1
    cpe_id = ''
    revert = revert
    list_user_perms = [('/itms/inquirytasklist/', u'远程操作')]
    return render_to_response('itms/inquirytasklist.html', locals(), context_instance=RequestContext(request))


@deco_check_login
def inquiry_tasklist_result(request, page_num, cpe_id, revert, worklist_id):
    """
    查询设备任务列表结果并返回给页面
    """

    if not request.user.has_perm('user_manager.can_testcase'):    # 没有测试用例的权限
        raise PermissionDenied
        # return HttpResponseForbidden('<h1>403 Forbidden</h1>')

    inquiry_rpc_result_list = []
    sn = CPE.objects.get(cpe_id=cpe_id).sn
    inquiry_type    = request.GET.get('inquirytype', None)
    input_start_time = request.GET.get('textsn1','')
    input_finish_time = request.GET.get('textsn2','')

    # 进行数据库操作，根据相应的条件查询RPC总数
    if (input_start_time =='' and input_finish_time ==''):
        total_rpc = RPC.objects.filter(cpe_id=cpe_id).exclude(rpc_name='Inform').order_by('-rpc_id').count()
    else:
        total_rpc = RPC.objects.filter(cpe_id=cpe_id, time_start__gte=input_start_time, time_start__lte=input_finish_time).exclude(rpc_name='Inform').order_by('-rpc_id').count()

    if ("skippage" in request.GET):
        inquiry_page = request.GET.get('inputpage', None)
    else:
        inquiry_page = page_num

    each_page_show_num = 17   # 为方便调试，每页显示17条
    if (total_rpc % each_page_show_num) == 0:
        total_page = total_rpc/each_page_show_num
    else:
        total_page = total_rpc/each_page_show_num + 1

    # 上一页和下一页
    inquiry_page = int(inquiry_page)
    last_page = inquiry_page - 1
    next_page = inquiry_page + 1

    # 列表起始
    list_start = (inquiry_page - 1)*each_page_show_num
    list_end = inquiry_page*each_page_show_num

    if inquiry_page == total_page:
        end_num = total_rpc
    else:
        end_num = list_end

    # 进行数据库操作，根据相应的条件查询RPC结果列表
    if (input_start_time =='' and input_finish_time ==''):
        inquiry_rpc_result_list = RPC.objects.filter(cpe_id=cpe_id).exclude(rpc_name='Inform').order_by('-rpc_id')[list_start:end_num]
    else:
        inquiry_rpc_result_list = RPC.objects.filter(cpe_id=cpe_id, time_start__gte=input_start_time, time_start__lte=input_finish_time).exclude(rpc_name='Inform').order_by('-rpc_id')[list_start:end_num]

    # 将需要的字段进行转换 Add by lizn 2014-05-21
    for rpc in inquiry_rpc_result_list:
        rpc.result_status = translate_to_target(status=rpc.result_status)

    t = loader.get_template('itms/inquirytasklistresult.html')
    c = Context({
        'inquiry_rpc_result_list':  inquiry_rpc_result_list,
        'inquiry_type':             inquiry_type,
        'inquiry_page':             inquiry_page,
        'total_page':               total_page,
        'total_rpc':                total_rpc,
        'last_page':                last_page,
        'next_page':                next_page,
        'cpe_id':                   cpe_id,
        'worklist_id':              worklist_id,
        'sn':                       sn,
        'input_start_time':         input_start_time,
        'input_finish_time':        input_finish_time,
        'revert':                   revert

    })
    return HttpResponse(t.render(c))


@deco_check_login
def soap_log(request):
    """
    SOAP任务列表初始页面
    """

    if not request.user.has_perm('user_manager.can_testcase'):    # 没有测试用例的权限
        raise PermissionDenied
        # return HttpResponseForbidden('<h1>403 Forbidden</h1>')
    inquiry_type = 'all'
    input_start_time = ''
    input_finish_time = ''
    inquiry_page = 1
    cpe_id = ''
    list_user_perms = [('/itms/soaplog/', u'远程操作')]
    return render_to_response('itms/soaplog.html', locals(), context_instance=RequestContext(request))


@deco_check_login
def soap_log_result(request, page_num, cpe_id, revert,worklist_id):
    """
    查询SOAP任务列表结果并返回给页面
    """

    if not request.user.has_perm('user_manager.can_testcase'):    # 没有测试用例的权限
        raise PermissionDenied
        # return HttpResponseForbidden('<h1>403 Forbidden</h1>')

    inquiry_type    = request.GET.get('inquirytype', None)
    input_start_time = request.GET.get('textsn1','')
    input_finish_time = request.GET.get('textsn2','')

    # 进行数据库操作，查询符合条件的soap包总数
    if (input_start_time =='' and input_finish_time ==''):
        total_soap = SOAP.objects.filter(cpe_id=cpe_id).order_by('-soap_id').count()
    else:
        total_soap = SOAP.objects.filter(cpe_id=cpe_id, time_exec__gte=input_start_time, time_exec__lte=input_finish_time).order_by('-soap_id').count()

    if ("skippage" in request.GET):
        inquiry_page = request.GET.get('inputpage', None)
    else:
        inquiry_page = page_num

    each_page_show_num = 8   # 为方便调试，每页显示8条
    if (total_soap % each_page_show_num) == 0:
        total_page = total_soap/each_page_show_num
    else:
        total_page = total_soap/each_page_show_num + 1

    # 上一页和下一页
    inquiry_page = int(inquiry_page)
    last_page = inquiry_page - 1
    next_page = inquiry_page + 1

    # 列表起始
    list_start = (inquiry_page - 1)*each_page_show_num
    list_end = inquiry_page*each_page_show_num

    # SOAP日志列表，格式为[(操作时间，操作方向，操作描述)......]
    list_result = []
    sn = CPE.objects.get(cpe_id=cpe_id).sn
    #cpe = CPE.objects.get(cpe_id=cpe_id)
    # 进行数据库操作，查询符合条件的soap包结果列表
    if inquiry_page == total_page:
        temp_end = total_soap
    else:
        temp_end = list_end

    if (input_start_time =='' and input_finish_time ==''):
        soaps = SOAP.objects.filter(cpe_id=cpe_id).order_by('-soap_id')[list_start:temp_end]
    else:
        soaps = SOAP.objects.filter(cpe_id=cpe_id, time_exec__gte=input_start_time, time_exec__lte=input_finish_time).order_by('-soap_id')[list_start:temp_end]

    if soaps:      # 查询到记录
        for soap in soaps:
            time = soap.time_exec
            if soap.direction == 'IN':
                direction = 'CPE->ACS'
            else:
                direction = 'ACS->CPE'
            soap_ex = SoapEx.objects.get(soap_id=soap.soap_id)
            list_soap_head = soap_ex.head_ex.splitlines()
            list_soap_body = soap_ex.content_body.splitlines()

            list_result.append((time, direction, list_soap_head, list_soap_body))


    t = loader.get_template('itms/soaplogresult.html')
    c = Context({
        'inquiry_soap_result_list':  list_result,
        'inquiry_type':             inquiry_type,
        'inquiry_page':             inquiry_page,
        'total_page':               total_page,
        'total_soap':               total_soap,
        'last_page':                last_page,
        'next_page':                next_page,
        'cpe_id':                   cpe_id,
        'worklist_id':              worklist_id,
        'sn':                       sn,
        'input_start_time':         input_start_time,
        'input_finish_time':        input_finish_time,
        'revert':                   revert,

    })
    return HttpResponse(t.render(c))


#  查询工单
@deco_check_login
def inquiry_worklist(request):
    """
    工单查询页面
    """

    if not request.user.has_perm('user_manager.can_testcase'):    # 没有测试用例的权限
        raise PermissionDenied
        # return HttpResponseForbidden('<h1>403 Forbidden</h1>')

    inquiry_type = 'all'
    input_worklist = ''
    inquiry_page = 1
    revert = 'no'
    backflag = 'no'
    return render_to_response('itms/inquiryworklist.html', locals(), context_instance=RequestContext(request))


@deco_check_login
def inquiry_worklist_result(request, page_num, revert):
    """
    工单查询结果页面
    """

    if not request.user.has_perm('user_manager.can_testcase'):    # 没有测试用例的权限
        raise PermissionDenied
        # return HttpResponseForbidden('<h1>403 Forbidden</h1>')

    input_worklist = ''
    inquiry_worklist_result_list = []

    if "*" in page_num:

        tmp_list = page_num.split("*")
        page_num = tmp_list[0]
        inquiry_type = tmp_list[1]
        input_worklist = tmp_list[2]
    else:

        inquiry_type    = request.GET.get('inquirytype', None)
        input_worklist = request.GET.get('textworklist','')

    if inquiry_type == 'all':
        total_worklist = Worklist.objects.filter(worklist_group='USER').count()

    elif inquiry_type == 'sn':
        total_worklist = Worklist.objects.filter(sn__contains=input_worklist, worklist_group='USER').count()

    elif inquiry_type == 'logic_userid':

        total_worklist = Worklist.objects.filter(worklist_type='logic', username__contains=input_worklist, worklist_group='USER').count()

    elif inquiry_type == 'logic_userkey':

        total_worklist = Worklist.objects.filter(worklist_type='logic', password__contains=input_worklist, worklist_group='USER').count()

    else:
        total_worklist = Worklist.objects.filter(worklist_desc__contains=input_worklist, worklist_group='USER').count()

    if ("inquiry" in request.GET):
        inquiry_page = 1
    elif ("skippage" in request.GET):
        inquiry_page = request.GET.get('inputpage', None)
    else:
        inquiry_page = page_num

    # 每页显示15条
    if (total_worklist % 15) == 0:
        total_page = total_worklist/15
    else:
        total_page = total_worklist/15 + 1

    # 上一页和下一页
    inquiry_page = int(inquiry_page)
    last_page = inquiry_page - 1
    next_page = inquiry_page + 1

    # 列表起始
    list_start = (inquiry_page - 1)*15
    list_end = inquiry_page*15

    if inquiry_page == total_page:
        end_num = total_worklist
    else:
        end_num = list_end

    if inquiry_type == 'all':
        inquiry_worklist_result_list = Worklist.objects.filter(worklist_group='USER').order_by('-worklist_id')[list_start:end_num]

    elif inquiry_type == 'sn':
        inquiry_worklist_result_list = Worklist.objects.filter(sn__contains=input_worklist, worklist_group='USER').order_by('-worklist_id')[list_start:end_num]

    elif inquiry_type == 'logic_userid':
        inquiry_worklist_result_list = Worklist.objects.filter(worklist_type='logic', username__contains=input_worklist, worklist_group='USER').order_by('-worklist_id')[list_start:end_num]

    elif inquiry_type == 'logic_userkey':
        inquiry_worklist_result_list = Worklist.objects.filter(worklist_type='logic', password__contains=input_worklist, worklist_group='USER').order_by('-worklist_id')[list_start:end_num]

    else:
        inquiry_worklist_result_list = Worklist.objects.filter(worklist_desc__contains=input_worklist, worklist_group='USER').order_by('-worklist_id')[list_start:end_num]

    # 将需要的字段进行转换 Add by lizn 2014-05-15
    for worklist in inquiry_worklist_result_list:
        worklist.worklist_type = translate_to_target(str_type=worklist.worklist_type)
        worklist.status = translate_to_target(status=worklist.status)
        #worklist.sn = translate_to_target(other=worklist.sn)

    t = loader.get_template('itms/inquiryworklistresult.html')
    c = Context({
        'inquiry_worklist_result_list':  inquiry_worklist_result_list,
        'inquiry_type':             inquiry_type,
        'input_worklist':           input_worklist,
        'inquiry_page':             inquiry_page,
        'total_page':               total_page,
        'total_worklist':           total_worklist,
        'last_page':                last_page,
        'next_page':                next_page,
        'revert':                   revert,
    })
    return HttpResponse(t.render(c))

@deco_check_login
def add_worklist(request,revert,cpe_id):
    """
    """
    if not request.user.has_perm('user_manager.can_testcase'):    # 没有测试用例的权限
        raise PermissionDenied

    list_worklist_isp = get_worklist_args()

    return render_to_response("itms/addworklist.html", {"list_worklist_isp":list_worklist_isp,
                                                        "revert":revert,'cpe_id':cpe_id}
                             )
@deco_check_login
def get_worklist_template_data(request):
    """
    函数功能：从数据库获取工单模板信息；
    参数：
        request：request请求，包含了工单信息路径列表
    返回值：
        dict_ret：{"exec_flag"："success"/"fail",
                   "exec_data":  dict_data/err_message,
                   "worklist_doc ": 当参数中包含有工单名时该值为工单描述，否则为空}
    """
    dict_ret     = {}
    dict_data    = {}
    exec_flag    = "success"
    exec_data    = ""
    worklist_doc = ""

    dict_data.update(request.GET)
    ret_worklist_data = []
    log.debug_info(u"收到获取工单模板参数的路径为：%s" %  dict_data)

    try:
        list_worklist_args = dict_data.get("list_data[]")   # 对javascript传入的字典做处理
        if list_worklist_args:
            ret_worklist_data = get_worklist_args(*list_worklist_args)
            log.debug_info(u"从数据库中读到的工单模板为：%s" % ret_worklist_data)

            # 当list_data长度大于3时，表示取的是工单参数，数据返回的是["dict_data"]
            if len(list_worklist_args) > 3:
                temp_dict = eval(ret_worklist_data[0])
                list_data = []
                # 对工单参数做排序结果[[args1_name,args1_default_value], [args1_name,args1_default_value]]
                for i in range(len(temp_dict)):
                    for key,value in temp_dict.items():
                        if value[1] == "%s" % (i+1):
                            list_data.append([key,value[0]])
                exec_data = list_data

                worklist_doc_data = get_worklist_doc(*list_worklist_args)
                worklist_doc      = _parse_worklist_doc(worklist_doc_data[0])

            else:
                exec_data = ret_worklist_data
    except Exception,e:
        exec_flag = "fail"
        exec_data = u"从数据库读取工单模板参数失败，原因:%s" % e
        log.user_info(exec_data)

    dict_ret["exec_flag"]    = exec_flag
    dict_ret["exec_data"]    = exec_data
    dict_ret["worklist_doc"] = worklist_doc

    return _return_user_json_data(dict_ret)

@deco_check_login
def init_worklist(request, worklist_name):
    dict_ret = {}

    if not request.user.has_perm('user_manager.can_testcase'):    # 没有测试用例的权限
        raise PermissionDenied

    dict_worklist_data = {}
    dict_args          = {}

    dict_args.update(request.GET)
    log.debug_info("receive worklistdata:%s" % dict_args)

    # 为了和rf统一，兼容参数为列表，zsj 2014-5-16
    for key,value in dict_args.items():
        if "[]" in key:
            dict_args.pop(key)
            key = key.replace("[]", "")
        dict_args[key] = value

    worklist_type_redio = dict_args.get("worklist_type_redio")

    if worklist_type_redio:
        dict_args.pop("worklist_type_redio")

    if worklist_type_redio[0] == "physic":
        dict_args.pop("username")
        dict_args.pop("userid")
    else:
        dict_args["username"] = dict_args.get("username", [""])[0]
        dict_args["userid"]   = dict_args.get("userid", [""])[0]

    dict_worklist_data["worklist_name"] = worklist_name
    dict_worklist_data["dict_data"] = dict_args

    log.debug_info(u"新增工单参数:%s" % dict_worklist_data)

    ret, ret_data = g_TR069_browser.init_worklist(dict_worklist_data)
    log.user_info("result:%s, ret_data:%s" % (ret, ret_data))

    dict_ret["exec_flag"]  = ret

    if ret == "success":  # 和rf统一使用工单描述
        worklist = Worklist.objects.get(worklist_desc=ret_data)
        ret_data = worklist.worklist_id

    dict_ret["exec_ret"]   = ret_data

    return _return_user_json_data(dict_ret)

@deco_check_login
def exec_worklist(request, worklist_id, revert):
    """
    函数功能：物理执行工单接口（物理工单为工单执行，采用多线程不阻塞）
    函数参数：
        request：request请求
        worklist_id：要执行的工单id
    返回值：无
    """
    if not request.user.has_perm('user_manager.can_testcase'):    # 没有测试用例的权限
        raise PermissionDenied

    worklist = Worklist.objects.get(worklist_id=worklist_id)
    worklist_desc = worklist.worklist_desc
    input_sn = worklist.sn
    old_status = worklist.status
    log.user_info(u"工单执行起始状态:%s" % old_status)


    wait_physic_max_timeout = 240    # 物理工单执行是阻塞的，故使用多线程，该时间为判断物理工单状态改变时间  zsj 2014-5-12

    ret = "success"
    alert_error = ""
    dict_data = {}
    dict_data["id_"]    = worklist_desc

    thread_obj = g_TR069_browser.exec_physic_worklist(dict_data)
    thread_obj.start()

    start_time = time.time()
    while (time.time()- start_time) < wait_physic_max_timeout:
        time.sleep(1)

        worklist = Worklist.objects.get(worklist_id=worklist_id)
        new_status = worklist.status

        if old_status != new_status:

            log.user_info(u"物理工单（%s）已开始执行！" % worklist.worklist_desc)

            break
    else:
        ret = "fail"
        log.user_info("time:%s" % time.time()- start_time)
        alert_error = u"等待工单（%s）状态改变时间超时（%ss）！" % (worklist.worklist_desc,
                                                                    wait_physic_max_timeout)
        log.user_info(alert_error )

    return get_worklist_info(request, worklist_id, revert, alert_error)

@deco_check_login
def get_relative_list(request, cpe_id):
    """
    函数功能：从数据库获取实时关联信息列表
    参数：
        request：request请求，包含了当前待选择的运营商及版本号
    返回值：
        dict_ret：{"exec_flag"："success"/"fail",
                   "exec_data":  dict_data/err_message}
    """
    if not request.user.has_perm('user_manager.can_testcase'):    # 没有测试用例的权限
        raise PermissionDenied

    dict_ret = {}
    exec_flag = 'fail'
    exec_data = ''
    tuple_pwd = ''

    # 取CPE表的实际数据
    try:
        cpe = CPE.objects.get(cpe_id=cpe_id)
    except:
        raise Http404
        # return HttpResponseBadRequest('')

    isp = request.GET.get('isp', '')
    version = request.GET.get('version', '')

    if version:
        # 更新设备类型时处理
        a1 = cpe.cpe2acs_username
        a2 = cpe.cpe2acs_password
        a3 = cpe.acs2cpe_username
        a4 = cpe.acs2cpe_password
        tuple_pwd = (a1, a2, a3, a4)
        cpe_isp = cpe.cpe_operator
        cpe_version = cpe.interface_version

        # 取配置表的原ISP和VERSION的默认值
        tuple_data = get_config_user_pwd(cpe_isp, cpe_version)
        #assert False, [tuple_pwd, tuple_data]
        if tuple_data == tuple_pwd:
            # 再取配置表中当前ISP和VERSION的默认值
            tuple_ret = get_config_user_pwd(isp, version)
            if tuple_ret:
                # 找到记录值，更新待返回的结果
                tuple_pwd = tuple_ret

    list_ret = get_worklist_doc(isp, version)
    if list_ret:
        # 找到记录值，更新待返回的结果
        exec_flag = 'success'
        exec_data = list_ret

    dict_ret['user_pwd']    = tuple_pwd
    dict_ret['exec_flag']   = exec_flag
    dict_ret['exec_data']   = exec_data

    return _return_user_json_data(dict_ret)

def check_worklist_inner(worklist):
    """
    函数功能：检查是否为内置工单
    函数参数：
        worklist：待检查的工单对象
    返回值：无，若为系统内置工单，则提示用户无权限
    """

    # 系统内置工单，不予显示给用户
    if worklist.worklist_group != 'USER':
        raise PermissionDenied

@deco_check_login
def get_worklist_info(request, worklist_id, revert, err_desc=''):
    """
    函数功能：显示工单详细信息
    函数参数：
        request：request请求
        worklist_id：要显示的工单id
    返回值：工单详细信息的html页面
    """
    if not request.user.has_perm('user_manager.can_testcase'):    # 没有测试用例的权限
        raise PermissionDenied
        # return HttpResponseForbidden('<h1>403 Forbidden</h1>')


    worklist = Worklist.objects.get(worklist_id=worklist_id)
    check_worklist_inner(worklist)     # 检查是否为内置工单

    input_sn = ''
    cpe_id = worklist.cpe_id
    # 将需要的字段进行转换 Add by lizn 2014-05-15
    worklist.status = translate_to_target(status=worklist.status)
    worklist.worklist_type = translate_to_target(str_type=worklist.worklist_type)
    #worklist.time_exec_start = translate_to_target(other=worklist.time_exec_start)
    #worklist.time_exec_finish = translate_to_target(other=worklist.time_exec_finish)

    worklist_ex = WorklistEx.objects.get(worklist_id=worklist_id)
    #parameters = {'Max': ('222.66.65.57', '2'), 'DSCPMarkValue': ('2', '3'), 'Min': ('222.66.65.57', '1'), ...}
    dict_paras = eval(worklist_ex.parameters)
    list_paras = []
    for para in dict_paras:
        row_no = int(dict_paras[para][1])   # 转换成int型，再排序
        if para.isdigit():
            list_paras.append((row_no, u'待定', dict_paras[para][0]))
        else:
            list_paras.append((row_no, para, dict_paras[para][0]))
    list_paras.sort()

    return render_to_response('itms/theworklistinfo.html',
                              {'worklist':worklist,
                               'input_sn':input_sn,
                               'cpe_id':cpe_id,
                               'alert_error':err_desc,
                               'list_paras':list_paras,
                               'revert':revert},
                              context_instance=RequestContext(request))

def translate_to_target(status='', str_type='', other=''):
    """
    函数功能：将字符进行合理转换
    函数参数：
        status：待转换的工单状态字段
        str_type：待转换的工单类型字段
        other:  需要将None转为''的其它字段
    返回值：转换后对应的值
    """
    # Add by lizn 2014-05-15
    dict_status = dict(build=u'新建', bind=u'绑定', reserve=u'准备中', abnormal=u'执行异常', running=u'执行中', success=u'执行成功', fail=u'执行失败')
    dict_type = dict(physic=u'物理工单', logic=u'逻辑工单')
    #dict_null = {None:''}
    if status:      # 处理状态转换
        try:
            return dict_status[status]
        except Exception,e:
            return status
    elif str_type:  # 处理类型转换
        try:
            return dict_type[str_type]
        except Exception,e:
            return str_type
    else:       # 处理None的转换
        if other == None:      # or not other
            return u''
        return other
        """
        try:
            return dict_null[ohter]
        except Exception,e:
            return other
        """

@deco_check_login
def check_cpe_status(request, cpe_id):
    """
    函数功能：实时检查CPE的在线状态
    函数参数：
        request：request请求
        cpe_id：要检查的cpe_id
    返回值：CPE的在线状态
    """

    cpe = CPE.objects.get(cpe_id=cpe_id)
    try:
        rpc_name  = "GetRPCMethods"
        dict_args = ""

        list_ret = g_TR069_browser.run_rpc(cpe.sn, rpc_name, dict_args)

        if list_ret[0] == "success":
            desc = u"在线"
        else:
            desc = u"离线"

    except Exception,e:
        err_message = u"查询设备在线失败，失败原因：%s" % (rpc_name, e)
        log.user_info(err_message)
        desc    = u"离线"
    """
    # Add by lizn 2014-04-16
    from TR069.vendor import httplib2
    username = cpe.acs2cpe_username
    password = cpe.acs2cpe_password
    url = cpe.connection_request_url

    result = {}
    conn = httplib2.Http(timeout = 30)
    conn.add_credentials(username, password)
    try:
        ret_response, content = conn.request(url) # 'http://172.123.122.3:30005/'
        conn.close()

        result['status'] = ret_response.status
        if ret_response.status == 200:
            desc = u'设备在线'
        else:
            desc = u'认证失败'
    except Exception, e:
        result['status'] = e.errno
        desc = u'连接超时'
    """
    log.user_info(u"查询设备在线结果：%s" % desc)

    #result['desc'] = desc
    response = HttpResponse()
    response['Content-Type'] = "text/html"
    response.write(desc)
    #response.expires=-1
    return response

@deco_check_login
def show_worklist_log(request, worklist_id, revert):
    """
    函数功能：显示工单日志信息
    函数参数：
        request：request请求
        worklist_id：要显示的工单id
    返回值：工单日志的html页面
    """
    if not request.user.has_perm('user_manager.can_testcase'):    # 没有测试用例的权限
        raise PermissionDenied
        # return HttpResponseForbidden('<h1>403 Forbidden</h1>')

    list_log = []
    worklist = Worklist.objects.get(worklist_id=worklist_id)
    check_worklist_inner(worklist)     # 检查是否为内置工单

    tuple_build = (worklist.time_init, '新建', '新建成功')
    tuple_bind = (worklist.time_bind, '绑定', '绑定成功')
    tuple_reserve = (worklist.time_reserve, '执行', '准备中...')
    tuple_running = (worklist.time_exec_start, '执行', '执行中...')
    tuple_fail = (worklist.time_exec_finish, '执行', '执行失败')
    tuple_success = (worklist.time_exec_finish, '执行', '执行成功')
    tuple_abnormal = ('', '执行', '执行异常')

    str_status = worklist.status

    if str_status == 'build':   # 新建成功
        list_log.append(tuple_build)
    else:
        list_log.append(tuple_build)
        list_log.append(tuple_bind)

        if str_status == 'bind':  # 绑定成功
            pass
        elif str_status == 'reserve':   # 准备中
            list_log.append(tuple_reserve)
        elif str_status == 'running':   # 执行中
            list_log.append(tuple_running)
        elif str_status == 'fail':      # 执行失败
            list_log.append(tuple_fail)
        elif str_status == 'success':   # 执行成功
            list_log.append(tuple_success)

        else:       # abnormal or other  执行异常
            list_log.append(tuple_abnormal)

    worklist_ex = WorklistEx.objects.get(worklist_id=worklist_id)

    #worklist.listlog = [("2014-04-21 05:21:52","新建","新建成功"),("2014-04-22 05:26:23","绑定","绑定成功"),("2014-04-22 05:26:23","执行","执行成功")]
    #worklist.logdetail = "1sfhdfgjdfgjfghdfghdfgh"
    worklist.listlog = list_log
    list_result = worklist_ex.result.splitlines()
    worklist.listdetail = list_result
    return render_to_response('itms/theworklistlog.html',
                              {'worklist':worklist,
                               'worklist_id':worklist_id,
                               'revert':revert},
                              context_instance=RequestContext(request))

@deco_check_login
def bind_device(request, worklist_id, revert):
    """
    通过SN号绑定CPE
    """
    if not request.user.has_perm('user_manager.can_testcase'):    # 没有测试用例的权限
        raise PermissionDenied
        # return HttpResponseForbidden('<h1>403 Forbidden</h1>')

    input_sn    = ''
    inquiry_cpe_result_list = []

    enter_bind_page = "yes"

    #  绑定设备失败标识
    alert_error = ""

    if ("confirm" in request.POST):
        input_sn        = request.POST.get('sn_radio','')
        log.user_info(u"要绑定的sn：%s" % input_sn)

        dict_data           = {}

        worklist  = Worklist.objects.get(worklist_id=worklist_id)
        worklist_desc = worklist.worklist_desc

        dict_data["id_"]    = worklist_desc
        dict_data["sn"]     = input_sn

        ret, ret_data = g_TR069_browser.bind_physic_worklist(dict_data)

        if ret != "success":
            input_sn = ""
            alert_error = ret_data
            log.user_info(u"绑定工单失败：%s" % ret_data)
        else:
            log.user_info(u"绑定工单成功")

        # 同一页面尽量调用相同的页面处理函数 Alter by lizn 2014-05-17
        return get_worklist_info(request, worklist_id, revert, alert_error)

    else:
        if ("inquiry" in request.POST):

            input_sn        = request.POST.get('sn_bind_device','')
            inquiry_cpe_result_list = CPE.objects.filter(sn__contains=input_sn)

            enter_bind_page = 'no'

        return render_to_response('itms/binddevice.html',
                              {'worklist_id':worklist_id,
                               'inquiry_cpe_result_list':  inquiry_cpe_result_list,
                               'input_sn':input_sn,
                               'enter_bind_page':enter_bind_page,
                               'revert':revert},
                              context_instance=RequestContext(request))

@deco_check_login
def cpe_to_worklist(request, cpe_id,revert,worklist_id):
    """
    CPE页面通过“设备工单”跳转至工单页面
    """
    if not request.user.has_perm('user_manager.can_testcase'):    # 没有测试用例的权限
        raise PermissionDenied
        # return HttpResponseForbidden('<h1>403 Forbidden</h1>')

    inquiry_type = 'sn'
    input_worklist = CPE.objects.get(cpe_id=cpe_id).sn
    inquiry_page = 1

    total_worklist = Worklist.objects.filter(cpe_id=cpe_id, worklist_group='USER').count()

    # 包含“返回”按钮
    backflag = "yes"

    # 每页显示12条
    if (total_worklist % 12) == 0:
        total_page = total_worklist/12
    else:
        total_page = total_worklist/12 + 1

    # 上一页和下一页
    inquiry_page = int(inquiry_page)
    last_page = inquiry_page - 1
    next_page = inquiry_page + 1


    list_start = (inquiry_page - 1)*12
    list_end = inquiry_page*12

    if inquiry_page == total_page:
        end_num = total_worklist
    else:
        end_num = list_end

    inquiry_worklist_result_list = Worklist.objects.filter(cpe_id=cpe_id, worklist_group='USER').order_by('-worklist_id')[list_start:end_num]


    # 将需要的字段进行转换 Add by lizn 2014-05-15
    for worklist in inquiry_worklist_result_list:
        worklist.worklist_type = translate_to_target(str_type=worklist.worklist_type)
        worklist.status = translate_to_target(status=worklist.status)
        #worklist.sn = translate_to_target(other=worklist.sn)

    t = loader.get_template('itms/inquiryworklistresult.html')
    c = Context({
        'inquiry_worklist_result_list':  inquiry_worklist_result_list,
        'inquiry_type':             inquiry_type,
        'input_worklist':           input_worklist,
        'inquiry_page':             inquiry_page,
        'total_page':               total_page,
        'total_worklist':           total_worklist,
        'last_page':                last_page,
        'next_page':                next_page,
        'revert':                   revert,
        'cpe_id':                   cpe_id,
        'worklist_id':              worklist_id,
        'backflag':                 backflag,

    })
    return HttpResponse(t.render(c))

@deco_check_login
def soap_operate(request, cpe_id):
    """
    函数功能：处理soap包日志的开始、关闭、删除及刷新
    函数参数：
        request：request请求
        cpe_id：待处理的cpe_id
    返回值：html页面，无实际意义
    """
    # Add by lizn 2014-05-15

    if not request.user.has_perm('user_manager.can_testcase'):    # 没有测试用例的权限
        raise PermissionDenied
        # return HttpResponseForbidden('<h1>403 Forbidden</h1>')

    if request.method == 'GET':
        # 获取操作类型
        ope_type = request.GET.get('type', '')
        list_type = ['start', 'finish', 'delete', 'refresh']
        if ope_type in list_type:
            cpe = CPE.objects.get(cpe_id=cpe_id)
            # status: 0 --> 未开始或已删除，1 --> 已开始， 2 --> 已关闭
            if ope_type == 'start':     # 点击了开始
                if cpe.soap_status == 0 or cpe.soap_status == 2:
                    time_begin = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    CPE.objects.filter(cpe_id=cpe_id).update(time_soap_begin=time_begin, soap_status=1)
                    msg = u'开始成功'
                else:
                    msg = u'已经是开始状态'
            elif ope_type == 'finish':  # 点击了关闭
                if cpe.soap_status == 1:
                    time_end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    CPE.objects.filter(cpe_id=cpe_id).update(time_soap_end=time_end, soap_status=2)
                    msg = u'关闭成功'
                else:
                    msg = u'尚未开始或已经删除，故不能关闭'
            elif ope_type == 'delete':  # 点击了删除
                if cpe.soap_status != 0:
                    CPE.objects.filter(cpe_id=cpe_id).update(soap_status=0) # time_soap_begin='', time_soap_end='',
                msg = u'删除成功'
            elif ope_type == 'refresh': # 点击了刷新
                #redirect_url = '/itms/%s/soaplog/' % cpe_id
                #return HttpResponseRedirect(redirect_url)
                return soap_log(request, cpe_id)
        else:
            msg = u'操作类型有误'
    else:
        msg = u'提交方式有误'

    return HttpResponse(msg)

@deco_check_login
def inquiry_result(request, page_num):
    """
    CPE查询结果页面
    """
    if not request.user.has_perm('user_manager.can_testcase'):    # 没有测试用例的权限
        raise PermissionDenied
        # return HttpResponseForbidden('<h1>403 Forbidden</h1>')

    input_sn = ""
    inquiry_cpe_result_list = []
    revert = 'yes'

    if "*" in page_num:
        tmp_list = page_num.split("*")
        page_num = tmp_list[0]
        inquiry_type = tmp_list[1]
        input_sn = tmp_list[2]
    else:

        inquiry_type    = request.GET.get('inquirytype', None)
        input_sn = request.GET.get('textsn','')

    if inquiry_type == 'all':
        total_cpe = CPE.objects.all().order_by('-time_last_contact').count()
    else:
        total_cpe = CPE.objects.filter(sn__contains=input_sn).order_by('-time_last_contact').count()

    if ("inquiry" in request.GET):
        inquiry_page = 1
    elif ("skippage" in request.GET):
        inquiry_page = request.GET.get('inputpage', None)
    else:
        inquiry_page = page_num

    # 每页显示15条
    if (total_cpe % 15) == 0:
        total_page = total_cpe/15
    else:
        total_page = total_cpe/15 + 1

    # 上一页和下一页
    inquiry_page = int(inquiry_page)
    last_page = inquiry_page - 1
    next_page = inquiry_page + 1

    # 列表起始
    list_start = (inquiry_page - 1)*15
    list_end = inquiry_page*15

    if inquiry_page == total_page:
        end_num = total_cpe
    else:
        end_num = list_end

    if inquiry_type == 'all':
        inquiry_cpe_result_list = CPE.objects.all().order_by('-time_last_contact')[list_start:end_num]
    else:
        inquiry_cpe_result_list = CPE.objects.filter(sn__contains=input_sn).order_by('-time_last_contact')[list_start:end_num]


    t = loader.get_template('itms/inquiryresult.html')
    c = Context({
        'inquiry_cpe_result_list':  inquiry_cpe_result_list,
        'inquiry_type':             inquiry_type,
        'input_sn':                 input_sn,
        'inquiry_page':             inquiry_page,
        'total_page':               total_page,
        'total_cpe':                total_cpe,
        'last_page':                last_page,
        'next_page':                next_page,
        'revert':                   revert,
    })
    return HttpResponse(t.render(c))

@deco_check_login
def get_cpe_info(request, cpe_id, revert, worklist_id):
    """
    CPE详细信息页面
    """
    if not request.user.has_perm('user_manager.can_testcase'):    # 没有测试用例的权限
        raise PermissionDenied
        # return HttpResponseForbidden('<h1>403 Forbidden</h1>')

    list_user_perms = [('/itms/inquirycpe/', u'远程操作')]

    # post form
    if (("refresh" in request.POST)  or
        ("submit" in request.POST)):
        cpe_info_sync(request, cpe_id)

    try:
        cpe = CPE.objects.get(cpe_id=cpe_id)
    except:
        raise Http404

    # 从数据库中获取运营商列表
    # eg. [('CT', 'CT'), ('CU', 'CU')...]
    list_isp = []
    list_ret = get_worklist_doc()
    for isp in list_ret:
        list_isp.append((isp, isp))
    cpe.cpe_operator_list = list_isp

    # CPE是否支持工单回滚选项
    list_rollback = []
    list_rollback.append(('False', 'False'))
    list_rollback.append(('True', 'True'))
    cpe.list_rollback = list_rollback

    # 运营商版本号
    list_isp_version = []
    list_ret = get_worklist_doc(isp=cpe.cpe_operator)
    for version in list_ret:
        list_isp_version.append((version, version))
    cpe.list_isp_version = list_isp_version

    # 认证方式
    list_auth = []
    list_auth.append(('basic', 'basic'))
    list_auth.append(('digest', 'digest'))
    list_auth.append(('None', u'不认证'))
    cpe.cpe_auth_type_list = list_auth

    # 从数据库中获取设备类型列表
    # eg. [('ADSL_2LAN', 'ADSL_2LAN'), ('ADSL_4+1', 'ADSL_4+1')...]
    list_domain = []
    list_ret = get_worklist_doc(isp=cpe.cpe_operator, version=cpe.interface_version)
    if not list_ret:
        list_domain.append(('', 'NULL'))
    else:
        for domain in list_ret:
            list_domain.append((domain, domain))
    cpe.cpe_device_type_list = list_domain

    # TR069版本
    list_cwmp_version = []
    list_cwmp_version.append(('cwmp-1-0', 'cwmp-1-0'))
    list_cwmp_version.append(('cwmp-1-1', 'cwmp-1-1'))
    list_cwmp_version.append(('cwmp-1-2', 'cwmp-1-2'))
    list_cwmp_version.append(('cwmp-1-3', 'cwmp-1-3'))
    cpe.cpe_cwmp_version_list = list_cwmp_version

    return render_to_response('itms/thecpeinfo.html',
                              {'cpe':cpe, 'list_user_perms':list_user_perms,'revert':revert, 'worklist_id':worklist_id},
                              context_instance=RequestContext(request))

def cpe_info_sync(request, cpe_id):
    """
    CPE页面“刷新”、“提交”按钮处理
    """
    cpe1 = CPE.objects.get(cpe_id=cpe_id)
    sn = cpe1.sn

    #raise Exception("nwf debug")
    if (request.POST.get("refresh") == u"刷新"):
        pass

    elif (request.POST.get("submit") == u"提交"):
        dict_item = {}
        dict_item["cpe_auth_acs_username"]  = request.POST.get("acs2cpe_username")
        dict_item["cpe_auth_acs_password"]  = request.POST.get("acs2cpe_password")
        dict_item["acs_auth_cpe_username"]  = request.POST.get("cpe2acs_username")
        dict_item["acs_auth_cpe_password"]  = request.POST.get("cpe2acs_password")
        dict_item["cpe_authtype"]           = request.POST.get("auth_type")
        dict_item["worklist_domain"]        = request.POST.get("cpe_device_type")
        dict_item["cpe_operator"]           = request.POST.get("cpe_operator")
        dict_item["cwmp_version"]           = request.POST.get("cwmp_version")
        dict_item["worklist_rollback"]      = request.POST.get("worklist_rollback")
        dict_item["interface_version"]      = request.POST.get("cpe_isp_version")

        g_TR069_browser.update_1_sn(sn, dict_item)

def enter_the_cpe(request,cpe_id,revert,worklist_id):
    """
    跳转至动态树或基础RPC方法页面
    """
    cpe = CPE.objects.get(cpe_id=cpe_id)
    root_text = "InternetGatewayDevice"

    operate_type    = request.POST.get('remoteoperate', None)

    if (operate_type == "parametersTree"):

        return render_to_response('itms/dyntree.html',{'cpe_id':cpe.cpe_id,"root_text":root_text,'revert':revert,'worklist_id':worklist_id})

    elif (operate_type == "RPCMethods") :
        return render_to_response('itms/enterthecpe.html',{'cpe':cpe,'revert':revert,'worklist_id':worklist_id})




@deco_check_login
@deco_rpc_process
def get_rpc_methods(request,cpe_id):
    pass

@deco_check_login
@deco_rpc_process
def set_parameter_values(request,cpe_id):
    pass

@deco_check_login
@deco_rpc_process
def get_parameter_values(request, cpe_id):
    pass

@deco_check_login
@deco_rpc_process
def get_parameter_names(request, cpe_id):
    pass

@deco_check_login
@deco_rpc_process
def set_parameter_attributes(request,cpe_id):
    pass

@deco_check_login
@deco_rpc_process
def get_parameter_attributes(request,cpe_id):
    pass

@deco_check_login
@deco_rpc_process
def add_object(request,cpe_id):
    pass

@deco_check_login
@deco_rpc_process
def delete_object(request,cpe_id):
    pass

@deco_check_login
@deco_rpc_process
def reboot(request,cpe_id):
    pass

@deco_check_login
@deco_rpc_process
def download(request,cpe_id):
    pass

@deco_check_login
@deco_rpc_process
def upload(request,cpe_id):
    pass

@deco_check_login
@deco_rpc_process
def factory_reset(request,cpe_id):
    pass

@deco_check_login
@deco_rpc_process
def schedule_inform(request,cpe_id):
    pass

@deco_check_login
@deco_rpc_process
def get_queued_transfers(request,cpe_id):
    pass

@deco_check_login
@deco_rpc_process
def set_vouchers(request,cpe_id):
    pass

@deco_check_login
@deco_rpc_process
def get_options(request,cpe_id):
    pass

@deco_check_login
@deco_rpc_process
def get_all_queued_transfers(request,cpe_id):
    pass

@deco_check_login
@deco_rpc_process
def schedule_download(request,cpe_id):
    pass

@deco_check_login
@deco_rpc_process
def cancel_transfer(request,cpe_id):
    pass

@deco_check_login
@deco_rpc_process
def change_du_state(request,cpe_id):
    pass

def _return_user_json_data(dict_data):
    """
    函数功能：对返回给客户端ajax请求做json编码，并返回
    参数：
        data：返回给客户端的dict数据
    返回值：无
    """
    try:
        #dict_data = simplejson.dumps(dict_data, ensure_ascii=False) # by lizn 2014-07-17
        dict_data = json.dumps(dict_data, ensure_ascii=False)
    except Exception,e:
        log.user_info(u"对返回的ajax的数据做jion转换失败:%s" % e)

    return HttpResponse(dict_data)

@deco_check_login
def ajax_rpc_request(request, cpe_id):
    """
    函数功能：接收来自动态树的rpc方法的请求
    参数：
        request：request请求，包含了rpc方法的参数
        cpe_id：要执的cpe id
    返回值：
        dict_ret：{"exec_flag"："success"/"fail",
                   "exec_code"：err_code/None,
                   "exec_ret":  dict_data/err_message}
    """
    dict_ret      = {}
    list_ret_data = []

    cpe = CPE.objects.get(cpe_id=cpe_id)

    dict_data = {}
    dict_data.update(request.GET)

    log.debug_info(u"收到的参数：%s" %  dict_data)

    try:
        rpc_names = dict_data.get("rpc_name", "")

        if rpc_names and isinstance(rpc_names, list):
            rpc_name = rpc_names[0]

            dict_data.pop("rpc_name")

            dict_data = _deal_rpc_args(rpc_name,dict_data)

            log.debug_info(u"要处理的rpc：%s，参数：%s" % (rpc_name, dict_data))
            list_ret = g_TR069_browser.run_rpc(cpe.sn, rpc_name, dict_data)
            dict_ret = _deal_rpc_return(rpc_name, list_ret)

        else:
            dict_ret["exec_flag"]  = "fail"
            dict_ret["exec_code"]  = "8888"
            dict_ret["exec_ret"]   = u"请求的处理错误，服务器无法识别"
    except Exception,e:
        dict_ret["exec_flag"]  = "fail"
        dict_ret["exec_code"]  = "8888"
        dict_ret["exec_ret"]   = u"执行rpc失败，错误信息：%s" % e

    log.debug_info(u"返回rpc ajax请求的结果为:%s" % dict_ret)
    #assert False
    return _return_user_json_data(dict_ret)

def _deal_rpc_args(rpc_name, dict_data):
    """
    函数功能：对动态树传递的参数做转换
    参数：
        rpc_name：rpc方法名字
        dict_ret：客户端传递的参数
    返回值：
        dict_data：rpc的合法参数格式
    """

     # 把值从列表中取出来
    for key,list_data in dict_data.items():
        if isinstance(list_data, list) and len(list_data) == 1:
            dict_data.update({key:list_data[0]})
    if rpc_name =="SetParameterValues":
        tmp_list = []
        tmp_dict = {}
        for key, value in dict_data.items():
            log.user_info("value type:%s, value=%s" % (type(value), value))

            if "SetParameterValuesArgs" in key:
                tmp_list.append({"Name":value[0], "Value":value[1]})

        tmp_dict["ParameterList"] = tmp_list
        dict_data = tmp_dict

    elif rpc_name == "SetParameterAttributes":
        tmp_list = []
        tmp_dict = {}
        dic_data = {}
        list_data = []
        for key, value in dict_data.items():
            list_data.append(value)

        list_data1 = list_data[0]
        if (len(list_data)>1):
            list_data2 = list_data[1]
            if isinstance(list_data2, str) or isinstance(list_data2, unicode):
                list_data2 = [list_data2]
        else:
            list_data2=[]

        dic_data["NotificationChange"]=list_data1[0]
        dic_data["Notification"]=list_data1[1]
        dic_data["AccessListChange"]=list_data1[2]
        dic_data["Name"]=list_data1[3]
        dic_data["AccessList"]=list_data2
        tmp_list.append(dic_data)

        tmp_dict["ParameterList"] = tmp_list
        dict_data = tmp_dict

    elif rpc_name == "GetParameterValues":
        str_name = dict_data.get("ParameterNames", "")
        list_name = str_name.split(',')
        if(list_name[-1] == ""):
            del list_name[-1]
        dict_data["ParameterNames"] = list_name
        log.debug_info(u"要处理的rpc：%s，传入的参数：%s" % (rpc_name, dict_data))

    return dict_data

def _deal_rpc_return(rpc_name, list_ret):
    """
    函数功能：对返回acs返回的rpc方法的结果做转换，适应网页的需求
    参数：
        rpc_name: 执行的rpc名字
        list_ret: 调用g_TR069_browser.run_rpc()返回的三元组
    返回值：
        dict_ret：{"exec_flag"："success"/"fail",
                   "exec_code"：err_code/None,
                   "exec_ret":  dict_data/err_message}
    """
    log.debug_info(u"将要对 %s 方法的返回值做处理(data):%s" % (rpc_name, list_ret))
    dict_ret      = {}

    dict_ret["exec_flag"]  = list_ret[0]
    dict_ret["exec_code"]  = list_ret[1]

    if dict_ret["exec_flag"] == "success":
        if rpc_name == "GetParameterNames":
            list_ret_data = []
            list_data = list_ret[2].get("ParameterList",[])

            for dict_temp_data in list_data:
                name  = dict_temp_data.get("Name","")
                if not name:
                    continue
                elif name[-1] == ".":
                    name = name[:-1]
                    flag = "false"
                else:
                    flag = "true"

                temp_data = name.split(".")[-1]
                list_ret_data.append([temp_data, flag])

            dict_ret["exec_ret"] = list_ret_data

        elif rpc_name =="GetParameterValues":
            list_ret_data = []
            list_data = list_ret[2].get("ParameterList",[])

            for dict_temp_data in list_data:
                name  = dict_temp_data.get("Name", "")
                value = dict_temp_data.get("Value", "")
                if not name:
                    continue
                else:
                    list_ret_data.append([name, value])

            dict_ret["exec_ret"] = list_ret_data

        elif rpc_name == "GetParameterAttributes":
            list_data = list_ret[2].get("ParameterList",[])

            for dict_data in list_data:
                dict_ret["exec_ret"] = dict_data
                break
            else:
                dict_ret["exec_ret"] = {}

        elif rpc_name in ["AddObject",
                          "DeleteObject",
                          "SetParameterValues"
                         ]:
            dict_ret["exec_ret"] = list_ret[2]

        elif rpc_name in ["Reboot",
                          "FactoryReset",
                          "SetParameterAttributes",
                         ]:
            dict_ret["exec_ret"] = "success"

    else:
        dict_ret["exec_ret"]   = list_ret[2]

    log.debug_info(u"转换 %s 方法的结果为:%s" % (rpc_name, list_ret))
    return dict_ret

@deco_check_login
def ajax_static_rpc_request(request, cpe_id):
    """
    函数功能：添加执行rpc方法的装饰器
    函数参数：
        func：要执行的rpc方法函数
    """
    cpe       = CPE.objects.get(cpe_id=cpe_id)

    dict_ret  = {}
    dict_args = {}
    dict_args.update(request.GET)
    log.debug_info(u"收到执行参数为:%s" % dict_args)

    rpc_name = dict_args.get("rpc_name",[])
    if rpc_name and isinstance(rpc_name, list) and len(rpc_name)>0:
        rpc_name = rpc_name[0]
        dict_args.pop("rpc_name")

        try:
            dict_args = deal_rpc_args(rpc_name, dict_args)

            list_ret = g_TR069_browser.run_rpc(cpe.sn, rpc_name, dict_args, False)

            dict_ret["exec_flag"]  = list_ret[0]
            dict_ret["exec_code"]  = list_ret[1]
            dict_ret["exec_ret"]   = list_ret[2]
        except Exception,e:
            err_message = u"执行 %s 失败，失败原因：%s" % (rpc_name, e)
            dict_ret    = _rpc_exception(err_message)
    else:
        err_message = u"发送的rpc方法不支持！"
        dict_ret    = _rpc_exception(err_message)

    log.debug_info(u"返回执行rpc(%s)结果为:%s" % (rpc_name,dict_ret))

    return _return_user_json_data(dict_ret)

def _rpc_exception(err_message):
    """
    """
    log.user_info(err_message)
    dict_ret  = {}
    dict_ret["exec_flag"]  = u"执行失败"
    dict_ret["exec_code"]  = "8888"
    dict_ret["exec_ret"]   = err_message

    return dict_ret


def deal_rpc_args(rpc_name, dict_args):
    """
    函数功能：对页面传递过来的rpc参数做转换
    参数：
        rpc_name： rpc名字
        dict_args：页面专递过来的参数
    返回值：
        dict_args：经过转换后的参数字典
    """
    if rpc_name in dict_args:
        dict_args.pop(rpc_name)  # 删除字典数据结构中的rpc_name字段

        # 把字典的值由列表变为字符串
    for key,list_data in dict_args.items():
        dict_args.update({key:list_data[0]})

    if rpc_name in LIST_NO_ARGS_RPC_METHODS:
        # 参数为空的情况
        dict_args = ""
    elif rpc_name in LIST_NOT_NEED_DEAL_ARGS_METHODS:
        # 参数无需处理的情况
        pass
    elif rpc_name == "SetParameterValues":
        list_tmp = []
        dict_tmp  = {}

        dict_tmp["CommandKey"] = dict_args.get("CommandKey", "")

        int_tmp = 0
        while True:
            int_tmp += 1
            flag      = "_%s" % int_tmp
            list_data = [x for x in dict_args.items() if flag in x[0]]
            if not list_data:
                break

            dict_data ={}
            for key, value in list_data:
                if "Name" in key:
                    dict_data.update({"Name":value})
                if "Value" in key:
                    dict_data.update({"Value":value})

            list_tmp.append(dict_data)

        dict_tmp["ParameterList"] = list_tmp
        dict_args = dict_tmp

    elif rpc_name in ["GetParameterValues",
                      "GetParameterAttributes"
                     ]:
        str_name = dict_args.get("ParameterNames", "")
        list_name = str_name.replace(u"，", ",").split(',')
        dict_args["ParameterNames"] = list_name

    elif rpc_name == "SetParameterAttributes":
        list_tmp = []
        dict_tmp = {}

        int_tmp = 0
        while True:
            int_tmp += 1
            flag      = "_%s" % int_tmp
            list_data = [x for x in dict_args.items() if flag in x[0]]
            if not list_data:
                break

            dict_data ={}
            for key, value in list_data:
                if "Name" in key:
                    dict_data.update({"Name":value})

                if "NotificationChange" in key:
                    dict_data.update({"NotificationChange":value})

                if "Notification_" in key:
                    dict_data.update({"Notification":value})

                if "AccessListChange" in key:
                    dict_data.update({"AccessListChange":value})

                if "AccessList_" in key:
                    if value:
                        list_access =  value.split(",")
                    else:
                        list_access = []

                    dict_data.update({"AccessList":list_access})

            list_tmp.append(dict_data)

        dict_tmp["ParameterList"] = list_tmp
        dict_args = dict_tmp

    elif rpc_name == "SetVouchers":
        str_voucher = dict_args.get("VoucherList", "")
        dict_args["VoucherList"] = [str_voucher]

    elif rpc_name == "ScheduleDownload":
        list_tmp = ["WindowStart",
                    "WindowEnd",
                    "WindowMode",
                    "UserMessage",
                    "MaxRetries"]

        dict_data = {}
        for k,v in dict_args.items():
            if k in list_tmp:
                dict_data.update({k:v})
                dict_args.pop(k)

        dict_args["TimeWindowList"] = [dict_data]

    elif rpc_name == "ChangeDUState":
        list_tmp               = []
        dict_tmp               = {}

        dict_tmp["CommandKey"] = dict_args.get("CommandKey")

        int_tmp                = 0
        while True:
            int_tmp  += 1
            flag      = "_%s" % int_tmp
            list_data = [x for x in dict_args.items() if flag in x[0]]
            if not list_data:
                break

            dict_InstallOpStruct   = {}
            dcit_UpdateOpStruct    = {}
            dcit_UninstallOpStruct = {}

            for key,value in list_data:
                if "_InstallOpStruct" in key:
                    dict_args.pop(key)
                    key = key.replace("_InstallOpStruct%s" % flag , "")
                    dict_InstallOpStruct.update({key:value})
                elif "_UpdateOpStruct" in key:
                    dict_args.pop(key)
                    key = key.replace("_UpdateOpStruct%s" % flag, "")
                    dcit_UpdateOpStruct.update({key:value})
                elif "_UninstallOpStruct" in key:
                    dict_args.pop(key)
                    key = key.replace("_UninstallOpStruct%s" % flag, "")
                    dcit_UninstallOpStruct.update({key:value})

            if dict_InstallOpStruct:
                list_tmp.append({"InstallOpStruct":dict_InstallOpStruct})

            if dcit_UpdateOpStruct:
                list_tmp.append({"UpdateOpStruct":dcit_UpdateOpStruct})

            if dcit_UninstallOpStruct:
                list_tmp.append({"UninstallOpStruct":dcit_UninstallOpStruct})

        dict_tmp["Operations"] = list_tmp

        dict_args = dict_tmp

    return dict_args

def _parse_worklist_doc(str_data):
    """
    函数功能：对数据库中读取到的工单描述做解析
    参数：
        str_data：字符串型的工单描述
    返回值：
        ret_list_data：按空白行把描述分块,组新列表，并把每行中含有"|"分拆为列表
    """
    ret_list_data  = []
    temp_list      = []
    temp_str       = ""

    start_list   = False

    list_data = str_data.splitlines()
    for str_data in list_data:
        str_data = str_data.strip()

        if not str_data:
            if temp_str:
                ret_list_data.append(temp_str)
                temp_str = ""

            if temp_list:
                ret_list_data.append(temp_list)
                temp_list = []

            if start_list:
                start_list = False

            if ret_list_data and ret_list_data[-1] != "</br>":
                ret_list_data.append("</br>")

        elif "|" in str_data:
            if  not start_list:
                start_list = True

            data = str_data.split("|")
            data = [x for x in data if x]
            temp_list.append(data)

        elif str_data:
            temp_str += str_data+"</br>"


    if temp_str:
        ret_list_data.append(temp_str)
        temp_str = ""

    if temp_list:
        ret_list_data.append(temp_list)
        temp_list = []

    return ret_list_data
