from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from account.serializers import *
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
import os
import time
from .qiniu_upload import upload_to_qiniu_and_get_url


@login_required
@api_view(['GET', 'POST'])
def upload_image(request):
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


@login_required
@api_view(['POST'])
def like_image(request):
    """
    点赞图片
    :param request:
    :return:
    """
    # 更新redis
    # 通知图片主人
    pass


@api_view(['GET'])
def get_image_detail(request, pk):
    """
    返回图片详细信息
    :param request:
    :return:
    """
    image = Image.objects.get(id=pk)
    serializer = ImageSerializer(image)
    return Response(serializer.data)


@login_required
@api_view(['POST'])
def comment_image(request, pk):
    """
    提交评论
    :param request:
    :param pk: 图片id
    :return:
    """
    try:
        content = request.data.get('content')
        image = Image.objects.get(id=pk)
        comment = Comment(publisher=request.user, content=content, image=image)
        comment.save()
        return Response('评论成功')
    except Exception:
        return Response(status.HTTP_400_BAD_REQUEST)