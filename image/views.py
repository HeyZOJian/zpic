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
from redis_utils import get_connection
from static_settings import *

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
def like_image(request, pk):
    """
    点赞图片
    :param request:
    :return:
    """
    # 通知图片主人
    # redis 点赞数+1
    try:
        conn = get_connection()
        conn.sadd(REDIS_LIKES+str(pk), request.user.nickname)
        update_hots(conn, pk)
        return Response({"msg": "ok"})
    except Exception:
        return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_image_likes(request, pk):
    """
    返回图片点赞数
    :param request:
    :param pk:
    :return:
    """
    try:
        conn = get_connection()
        like_num = conn.scard(REDIS_LIKES+str(pk))
        like_mem = conn.smembers(REDIS_LIKES+str(pk))
        res = {}
        res['likes'] = like_num
        res['mems'] = like_mem
        return Response(res)

    except Exception:
        return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_image_detail(request, pk):
    """
    返回图片详细信息
    :param request:
    :return:
    """
    try:
        image = Image.objects.get(id=pk)
        serializer = ImageSerializer(image)
        # redis 浏览数+1
        conn = get_connection()
        conn.incr(REDIS_VIEWS_TOTAL+str(pk),1)
        update_redis_hots(conn, pk)
        # TODO: 将图片详细信息缓存到redis
        return Response(serializer.data)
    except Image.DoesNotExist:
        return Response(status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_image_views(request, pk):
    """
    获取图片总浏览数
    :param request:
    :param pk:
    :return:
    """
    conn = get_connection()
    views = conn.get(REDIS_VIEWS_TOTAL+str(pk))
    return Response({"views": views})


@api_view(['GET'])
def get_hots_week(request, page):
    try:
        conn = get_connection()
        result = conn.zrange(REDIS_HOTS_WEEK, page, page+10)
        # TODO: 从redis中取出图片详细信息
        return Response(result)
    except Exception:
        return Response(status.HTTP_400_BAD_REQUEST)


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


def update_redis_hots(conn, pk):
    # 更新热门周榜
    if conn.exists(REDIS_HOTS_WEEK) == 0:
        conn.zincrby(REDIS_HOTS_WEEK, pk, 1)
        conn.expire(REDIS_HOTS_WEEK, WEEK_SECOND)
    else:
        conn.zincrby(REDIS_HOTS_WEEK, pk, 1)
    # 更新热门月榜
    if conn.exists(REDIS_HOTS_MONTH) == 0:
        conn.zincrby(REDIS_HOTS_MONTH, pk, 1)
        conn.expire(REDIS_HOTS_MONTH, WEEK_SECOND)
    else:
        conn.zincrby(REDIS_HOTS_MONTH, pk, 1)
