# -*- coding: UTF-8 -*-
"""movieweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

from videoplay.views import index, play, regist, login

# 实现swagger code
from videoplay import views
from rest_framework import renderers, response, schemas
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.routers import DefaultRouter
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer

@api_view()
@renderer_classes([SwaggerUIRenderer, OpenAPIRenderer, renderers.CoreJSONRenderer])
def schema_view(request):
    generator = schemas.SchemaGenerator(title='Data API')
    return response.Response(generator.get_schema(request=request))
# Routers（路由）提供了一种简单的方法来自动生成URL配置
router = DefaultRouter()
router.register(r'movie', views.SnippetViewSet)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^regist/$', regist),
    url(r'^$', login),
    url(r'^movie/$', index),
    url(r'^movie/video_(?P<id>\d{1,2}).html$', play),

    url(r'^swagger$', schema_view),
    url(r'^', include(router.urls)),
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
