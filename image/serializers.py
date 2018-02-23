from rest_framework import serializers
from .models import *


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ('id', 'author', 'title','img_url', 'create_time')
