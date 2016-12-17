# -*- coding: UTF-8 -*-
from rest_framework import serializers
from videoplay.models import Movie

# Serializers(序列化器)定义了如何展示API
class MovieSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Movie
        fields = ('movie',)
