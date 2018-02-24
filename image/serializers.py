from rest_framework import serializers
from .models import *


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('id', 'publisher', 'content', 'create_time')


class ImageSerializer(serializers.ModelSerializer):

    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Image
        fields = ('id', 'author', 'title','img_url', 'create_time', 'comments')
