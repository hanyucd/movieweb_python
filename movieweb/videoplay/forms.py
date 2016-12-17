# -*- coding: UTF-8 -*-
# 导入表单
from django import forms
''' 用户注册/登录数据 '''
class UserForm(forms.Form):
    username = forms.CharField(max_length = 20)
    password = forms.IntegerField()

''' 用户评论数据 '''
class UserCommentForm(forms.Form):
    user_comment = forms.CharField(max_length = 300)
    
''' 电影支付数据 '''
class MoviePayForm(forms.Form):
    movie_pay = forms.IntegerField()
