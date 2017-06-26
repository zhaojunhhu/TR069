# -*- coding: utf-8 -*-

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
# from django.views.decorators.csrf import csrf_protect
from datetime import datetime, timedelta

from django.core.exceptions import PermissionDenied

#from mysite.forms import RegisterForm
#from django.contrib.auth.forms import UserCreationForm

def check_username(request):
    """
    检查当前是否有用户登录
    """

    if not request.user.is_authenticated():
        info = "No login yet!"
    else:
        user = request.user.get_username()
        remote_addr = remote_addr=request.META['REMOTE_ADDR']
        info = "Current login user [%s] at [%s]!" % (user, remote_addr)
        
    result = '<html><body>%s</body></html>' % info
    return HttpResponse(result)

def user_manage(request):
    """
    用户及组的权限管理
    """
    if not request.user.is_authenticated():
        next_url = request.path
        redirect_url = r'/login/?next=%s' % next_url
        return HttpResponseRedirect(redirect_url)
        
    if not request.user.has_module_perms('auth'):    # 没有配置用户的权限
        raise PermissionDenied
        # return HttpResponseForbidden('<h1>403 Forbidden</h1>')
    
    return HttpResponseRedirect(r"/admin/auth/")
    
def server_manage(request):
    """
    服务器权限管理
    """
    if not request.user.is_authenticated():
        next_url = request.path
        redirect_url = r'/login/?next=%s' % next_url
        return HttpResponseRedirect(redirect_url)
        
    if not request.user.has_perm('user_manager.can_config'):    # 没有服务器管理的权限
        raise PermissionDenied
        # return HttpResponseForbidden('<h1>403 Forbidden</h1>')
    
    return HttpResponseRedirect(r"/itms/manageserver/")

def login_view(request, template_name=''):
    """
    处理登录过程，成功则跳转至相应页面
    """
    
    # 获取跳转页面的URL
    # redirect_to = request.REQUEST.get('next', '')
    next_url = request.GET.get('next', '')
    # assert False
    if request.user.is_authenticated():
        #if next_url == '/login/':
        #    return HttpResponseRedirect('/itms/')
        return HttpResponseRedirect('/itms/')   # next_url
    
    errors = []
    username = ''
    if request.method == 'POST':
        
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        if not username:
            errors.append('用户名不能为空')   # Username can not be empty.
            
        if not password:
            errors.append('密码不能为空')   # Password can not be empty.
            
        if not errors:
            user = authenticate(username=username, password=password)
            #assert False
            if user is not None:
                if user.is_active and user.is_staff:
                    login(request, user)
                    return HttpResponseRedirect(next_url)
                else:
                    errors.append('不是有效职员')   # Not a active user.
            else:
                errors.append('用户名或密码不正确')   # Access denied.
    
    user_name = username
    
    return render_to_response('itms/login.html', locals(), context_instance=RequestContext(request))

def logout_view(request):
    """
    退出登录，然后跳转到登录界面，之前是否处于登录状态都不影响
    """
    logout(request)
    return HttpResponseRedirect(r"/login/")
