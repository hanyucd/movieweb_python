# -*- coding: UTF-8 -*-
from django.shortcuts import render
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, Context
from django.shortcuts import render_to_response

import time
import random
import string
import hashlib
import requests
# 导入缓存
from django.core.cache import cache
# 导入模型
from videoplay.models import Movie
from videoplay.models import User, UserComment, MoviePay
# 导入表单
from .forms import UserForm, UserCommentForm, MoviePayForm

class Sign:
    ''' 实例化初始值 '''
    def __init__(self, appid, appsecret, url):
        self.appid = appid
        # self.access_token = self.get_access_token(appid, appsecret)

        ''' 缓存access_token '''
        self.access_token = cache.get('access_token')
        if self.access_token == None:
            cache.set('access_token', self.get_access_token(appid, appsecret), 7050)
            self.access_token = cache.get('access_token')

        ''' 缓存jsapi_ticket '''
        self.jsapi_ticket = cache.get('jsapi_ticket')
        if self.jsapi_ticket == None:
            cache.set('jsapi_ticket', self.get_ticket(self.access_token), 7100)
            self.jsapi_ticket = cache.get('jsapi_ticket')

        self.ret = {
            'nonceStr': self.__create_nonce_str(),
            'jsapi_ticket': self.jsapi_ticket,
            'timestamp': self.__create_timestamp(),
            'url': url,
         }
        # 缓存signature
        # self.signature = cache.get('signature')
        # if self.signature == None:
        #     cache.set('signature', self.sign(), 7150)
        #     self.signature = cache.get('signature')

    ''' 获取随机字符串 '''
    def __create_nonce_str(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
    ''' 获取时间戳 '''
    def __create_timestamp(self):
        return int(time.time())
    ''' 获取access_token '''
    def get_access_token(self, appid, appsecret):
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(appid,appsecret)
        r = requests.get(url)
        data = r.json()
        access_token = data.get('access_token')
        return access_token
    ''' 获取jsapi_ticket '''
    def get_ticket(self, access_token, type='jsapi'):
        url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={}&type={}'.format(access_token, type)
        r = requests.get(url)
        data = r.json()
        ticket = data.get('ticket')
        return ticket
    ''' 获取signature '''
    def sign(self):
        string = '&'.join(['%s=%s' % (key.lower(), self.ret[key]) for key in sorted(self.ret)])
        self.ret['signature'] = hashlib.sha1(string).hexdigest()
        return self.ret
        # return self.ret.get('signature')

""" 视频播放页面 """
def play(request, id):
    # 通过 session 来获取传过来的数据 (用户名)
    comment_username = request.session.get('comment_username')
    if request.method == "POST":
        print request.POST
        if 'user_comment' in request.POST:
            ''' 用户评论 '''
            # 绑定评论表单
            uf_comment = UserCommentForm(request.POST)
            # 校验提交数据是否合法
            if uf_comment.is_valid():
                # 如合法,获取数据并赋于变量
                user_comment = uf_comment.cleaned_data.get('user_comment')
                # 获取当前时间 (格式化)
                comment_time = time.strftime('%Y/%m/%d | %H:%M:%S', time.localtime())
                # 存入数据库
                UserComment.objects.create(comment_username = comment_username, user_comment = user_comment, comment_time = comment_time)
                print user_comment
                print comment_time
                # 获取当前除域名以外的请求路径
                path = request.path
                print path
                ''' 重定向到当前页面 '''
                return HttpResponseRedirect(path)
        elif 'movie_pay' in request.POST:
            ''' 电影支付 '''
            movie_id = int(id)
            # 绑定支付表单
            uf_payment = MoviePayForm(request.POST)
            # 校验提交数据是否合法
            if uf_payment.is_valid():
                # 获取支付数据
                movie_pay = uf_payment.cleaned_data.get('movie_pay')
                # 存入数据库
                MoviePay.objects.create(pay_username = comment_username, movie_id = movie_id, movie_pay = movie_pay)
                # 获取当前除域名以外的请求路径
                path = request.path
                ''' 重定向到当前页面 '''
                return HttpResponseRedirect(path)

    ''' 微信分享的 code '''
    appid, appsecret = 'wx89d78fda8c962552', '41d433fe0e3194e1aff2d607c585be65'
    # 动态获取当前的url
    url = 'http://' + request.get_host() + request.get_full_path()
    sign = Sign(appid, appsecret, url)
    # 调用签名方法
    sign.sign()
    # 将获取到的字符串类型参数转换为 int
    video_id = int(id)
    # 获取(数据库)模型中对应电影的对象
    video_source = Movie.objects.get(id = video_id)
    # 获取数据库中所有的评论对象 | all() 和 filter()函数返回一个记录集 (列表)
    comments_list = UserComment.objects.all()
    # 获取数据库中已支付的对象
    movie_payment_obj = MoviePay.objects.filter(pay_username = comment_username, movie_id = video_id)
    # 支付 False：未购买 True: 已购买
    pay = False
    if video_id <= 5:
        if len(movie_payment_obj) != 0:
            pay = True
        else:
            pay = False
    # 加载视频播放模板
    t = loader.get_template("video.html")
    c = Context({"user": sign, "video_source": video_source, "video_id": video_id,"movie_payment_obj": len(movie_payment_obj), "pay": pay, "url": url, "comments_list": comments_list})
    return HttpResponse(t.render(c))

""" 用户注册 """
def regist(request):
    if request.method == "POST":
        # 绑定表单
        uf_regist = UserForm(request.POST)
        # 校验提交数据是否合法
        if uf_regist.is_valid():
            # 如合法,获取各自的数据并赋于变量
            username = uf_regist.cleaned_data.get('username')
            password = uf_regist.cleaned_data.get('password')
            # 存入数据库
            User.objects.create(username = username, password = password)
            # 跳转到登录界面
            return HttpResponseRedirect('/')
        else:
            return render(request, "user_regist.html", {"danger": True})
    else:
        uf_regist = UserForm()
    # 加载用户注册模板
    user_regist = loader.get_template("user_regist.html")
    return HttpResponse(user_regist.render())

""" 用户登录 """
def login(request):
    if request.method == 'POST':
        # 绑定表单 | request.Post:获取表单提交的数据 (类字典对象)
        uf_login = UserForm(request.POST)
        # 校验提交数据是否合法
        if uf_login.is_valid():
            # 如合法后,获取各自的数据并赋于变量
            username = uf_login.cleaned_data['username']
            password = uf_login.cleaned_data['password']
            ''' 异常 用户名不存在 '''
            try:
                User.objects.get(username = username)
            except User.DoesNotExist:
                return render_to_response('user_login.html', {"userName_error": True})
            # 获取数据库(模型)中对应的对象
            user = User.objects.filter(username__exact = username, password__exact = password)
            # 如果输入的对象匹配数据库中的对象为 True（存在数据库中）
            if user:
                # 创建 HTTpResponse 对象（跳转至 /movie 页面）
                response = HttpResponseRedirect('/movie/')
                # 设置 cookie 值，有效期 1 小时
                response.set_cookie('username', username)
                # response.set_cookie('username', username, 3600)
                # request.session['username'] = username  /使用 session 来设置 cookie值， 等效同上
                return response
            # 输入的密码不匹配数据库中的密码 执行
            elif password !=  User.objects.get(username = username).password:
                return render_to_response('user_login.html', {"userPassword_error" : True})

        # 如果输入的内容不合法（数据为空）
        else:
            return render_to_response('user_login.html', {'userForm_error': True})
    else:
        uf_login = UserForm()
    # 加载用户登录模板
    user_login = loader.get_template("user_login.html")
    return HttpResponse(user_login.render())
""" 网站首页 """
def index(request):
    username = request.COOKIES.get('username', None)
    # username = request.session.get('username', 'anonymity') /使用 session 来获取传来的 cookie值， 等效同上
    ''' 设置 session 的数据（传到视频播放页面）'''
    request.session['comment_username'] = username
    # 获取用户名成功 执行
    if username != None:
        return render_to_response('index.html', {"username": username})
    #  用户名超时 执行
    else:
        return render_to_response('index.html', {'error': True})

""" 实现swagger code """
from rest_framework import viewsets
from videoplay.models import Movie
from videoplay.serializers import MovieSerializer
# ViewSets定义了View的行为
class SnippetViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
