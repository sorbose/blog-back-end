import json
import os
import string
import random

from django.contrib.auth.hashers import check_password, make_password
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from django.db import IntegrityError
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import BlogUser
from django.http.request import HttpRequest
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, \
    HttpResponseNotAllowed
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from itertools import islice
from django.core import serializers

# Create your views here.
def get_csrftoken(request):
    token = get_token(request)
    return HttpResponse(json.dumps({'token': token}), content_type="application/json,charset=utf-8",
                        headers={'Access-Control-Allow-Origin': '*'})


# def options(request: HttpRequest, *args, **kwargs):
#     method = request.META.get('Access-Control-Allow-Method')
#     origin = request.META.get('Origin')
#     response = HttpResponse()
#     response['Access-Control-Allow-Method'] = method  # 支持那些请求方法，可以根据实际情况配置如 "POST, GET ,OPTIONS"
#     response['Access-Control-Allow-Origin'] = origin  # 实际操作中本人无法获取请求头中的Origin参数，所以这里我实际上是配置成了 "*",但是不建议这样操作,后续会有问题,可以根据实际情况写成固定的也可以 "完整域名"
#     response["Access-Control-Allow-Headers"] = "X-CSRFToken, Content-Type"  # 如果配置接收的请求头有遗漏，当发送OPTIONS方法成功后，发送正式请求时将会在浏览器报错，可以根据浏览器中consolo的报错内容添加进去即可, 我这里需要配置的就是这两个
#     return response

def JSONCORS(data: dict):
    return JsonResponse(data=data)
    """
    return JsonResponse(data=data,
                        headers={'Access-Control-Allow-Origin': 'http://localhost:8081',
                                 'Access-Control-Allow-Headers': '*',
                                 'Access-Control-Allow-Credentials': 'true'}

                        )
    """


def register(request: HttpRequest):
    print("request.headers:")
    print(request.headers)
    # if request.method == 'OPTIONS':
    #     response = HttpResponse()
    #     response["Access-Control-Allow-Origin"] = "*"
    #     response["Access-Control-Allow-Headers"] = "*"
    #     response["Access-Control-Max-Age"] = "60"
    #     response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    #     return response

    try:
        dic = {}
        print("request.POST:", request.POST)
        print("request.body:", request.body)
        # print('json.loads(request.body):',json.loads(request.body))
        username = request.POST['username']
        dic['username'] = username
        email = request.POST['email']
        password = request.POST['password']
        birthday = request.POST['birthday']
    except MultiValueDictKeyError:
        response = JSONCORS(data={'success': 'False', 'errcode': 1, 'msg': '缺少表单字段'})
        print(response.headers)
        return response
    try:
        BlogUser.objects.create_user(username, email, password=password, birthday=birthday)
    except:
        response = JSONCORS(
            data={'success': 'False', 'errcode': 2, 'msg': 'Failed. 可能是用户名已被注册或数据格式不符合要求'})
        print(response.headers)
        return response
    response = JSONCORS(data={'success': 'True', 'msg': 'registration success', 'username': username})
    print(response.headers)
    return response


# res=c.post('/account/register/',{'username':'test1','email':'test1@aaa.com','password':'123456','birthday':'2001-02-14'})

def user_login(request: HttpRequest):
    if request.method != 'POST':
        return JSONCORS({'success': 'False', 'errcode': -1, 'msg': 'use POST method'})
    try:
        print(request.POST)
        username = request.POST['username']
        password = request.POST['password']
    except MultiValueDictKeyError:
        return JSONCORS({'success': 'False', 'errcode': 1, 'msg': 'Missing parameter'})

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return JSONCORS({'success': 'True', 'msg': 'login success'})
    else:
        return JSONCORS({'success': 'False', 'errcode': 1, 'msg': 'Incorrect user name or password'})


def user_logout(request):
    logout(request)
    return JSONCORS({'success': 'True', 'msg': 'Logout success'})


def verify_password(request: HttpRequest):
    try:
        username = request.POST['username']
        old_password = request.POST['password']
    except MultiValueDictKeyError:
        return (False, JSONCORS({'success': 'False', 'errcode': 1, 'msg': '缺少表单字段'}))
    current_user = request.user
    if username != current_user.username:
        return (False, JSONCORS({'success': 'False', 'errcode': 2, 'msg': '用户不一致'}))
    if not current_user.check_password(old_password):
        return (False, JSONCORS({'success': 'False', 'errcode': 3, 'msg': '原密码错误'}))
    return (True, None)


def change_password(request: HttpRequest):
    verify_res = verify_password(request)
    if not verify_res[0]:
        return verify_res[1]
    current_user = request.user
    new_password = request.POST['new_password']
    current_user.set_password(new_password)
    current_user.save()
    update_session_auth_hash(request, current_user)
    return JSONCORS({'success': 'True', 'msg': 'Password changed successfully'})


def delete_user(request: HttpRequest):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    verify_res = verify_password(request)
    if not verify_res[0]:
        return verify_res[1]
    username = request.user.username
    if str(request.POST['delete']) != '1':
        return JSONCORS(
            {'success': 'False', 'errcode': 1, 'msg': 'Are you sure to delete your account?', 'username': username})
    user = BlogUser.objects.get(username=username)
    logout(request)
    user.delete()
    return JSONCORS({'success': 'True', 'msg': 'Delete user successfully'})

def change_account_inf(req:HttpRequest):
    update_fields= {}
    account=req.user
    update_fields['email']=req.POST.get('email',account.email)
    update_fields['birthday'] = req.POST.get('birthday',account.birthday)
    update_fields['avatar'] = req.POST.get('avatar',account.avatar)
    BlogUser.objects.filter(pk=account.pk).update(**update_fields)
    return JSONCORS({'success':'True'})

def upload_avatar(request:HttpRequest):
    if request.method == "POST":
        avatar = request.FILES.get("image", None)
        path = os.path.join("static/media/avatar", request.user.username+".jpg")
        destination = open(path, 'wb+')  # 打开特定的文件进行二进制的写操作
        for chunk in avatar.chunks():
            destination.write(chunk)
        destination.close()
        BlogUser.objects.filter(pk=request.user.id).update(**{'avatar':path})
        return JSONCORS({'success':'True','path':path})

def query_user(request: HttpRequest):
    if not request.user.is_authenticated:
        return JSONCORS({'success': 'False', 'errcode': 1, 'msg': 'Please log in first'})
    data = {}
    user = request.user
    data['username'] = user.username
    data['birthday'] = user.birthday
    data['email'] = user.email
    data['avatar']=user.avatar.url
    return JSONCORS({'success': 'True', 'data': data, })

def query_username_by_id(req:HttpRequest):
    id=req.GET.get('id')
    username=BlogUser.objects.filter(id=id).values('username').first()
    return JSONCORS({'success': 'True', 'data': username })


@ensure_csrf_cookie
def is_login(request: HttpRequest):
    fields = ('username','avatar','email','birthday','date_joined','last_login','is_superuser')
    data = serializers.serialize('json',BlogUser.objects.filter(id=request.user.id),fields=fields)
    return JSONCORS({'success':'True','is_login': request.user.is_authenticated,'data':json.loads(data)})


def is_username_registered(request: HttpRequest):
    username = request.GET.get('q')
    try:
        BlogUser.objects.get(username=username)
    except BlogUser.DoesNotExist:
        return JSONCORS({'success':'True','username': username, 'is_registered': 'False'})
    return JSONCORS({'success':'True','username': username, 'is_registered': 'True'})


def is_superuser(request: HttpRequest):
    return request.user.is_superuser


def create_users(request: HttpRequest):
    if not is_superuser(request):
        return HttpResponseForbidden("<h1>403 Forbidden.</h1>You are not an administrator."
                                     , headers={'Access-Control-Allow-Origin': '*'}, content_type="text/html")
    prefix = request.POST.get('prefix')
    size = int(request.POST.get('size',default=10))
    default_password = request.POST.get('default_password', default=123456)
    def random_strings(size=8, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
        return ''.join(random.choice(chars) for _ in range(size))
    json_data = []
    for i in range(size):
        obj = {}
        obj['username'] = prefix+'_'+random_strings()
        obj['password'] = default_password
        json_data.append(obj)

    objs = (BlogUser(username=a.get("username"), password=make_password(a.get("password")),
                     email=a.get("email") if a.get("email") is not None else 'null',
                     is_staff=a.get("is_staff") if a.get("is_staff") is not None else False,
                     is_superuser=a.get("is_superuser") if a.get("is_superuser") is not None else False,
                     birthday=a.get("birthday") if a.get("birthday") is not None else '1900-01-01') for a in json_data)
    batch_size = 100
    success = []
    while True:
        batch = list(islice(objs, batch_size))
        if not batch:
            break
        try:
            success += BlogUser.objects.bulk_create(batch, batch_size)
        except IntegrityError:
            return JSONCORS({'success': 'False', 'errcode': 1, 'msg': 'IntegrityError'})
    res = []
    for bu in success:
        res.append(bu.username)
    return JSONCORS({'success': 'True', 'created_usernames': res})

from rest_framework import generics
from .models import BlogUser
from .serializers import ChangeInfoSerializer

class ChangeUserInfo(generics.UpdateAPIView):

    queryset = BlogUser.objects.all()
    serializer_class = ChangeInfoSerializer

    def perform_update(self, serializer):
        serializer.save()