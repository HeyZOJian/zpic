from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from rest_framework.decorators import api_view
from account.serializers import *
from rest_framework.request import Request
from rest_framework.response import Response
from .models import *
from .serializers import *
import os
import time
from .qiniu_upload import upload_to_qiniu_and_get_url


# TODO: 权限设置
@api_view(['GET', 'POST'])
def upload_photo(request):
    """
    上传图片
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request,'user/upload.html', locals())
    if request.method == 'POST':
        obj = request.FILES.get('image')
        # 上传七牛云并返回外链
        url = upload_to_qiniu_and_get_url(obj)
        user = request.user
        title = request.data.get('title')
        image = Image(author=user,img_url=url,title=title)
        image.save()
        # 增加用户图片数量
        # TODO: 原子性？
        user.image_num += 1
        user.save()
        return Response(ImageSerializer(image).data)


# TODO: 权限设置
@api_view(['GET'])
def moments(request):
    """
    查看朋友圈
    :param request:
    :return:
    """
    # TODO:获取关注好友的图片
    user = request.user
    serializer = LoginSerializer(user)
    return Response(serializer.data)