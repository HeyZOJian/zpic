from django.shortcuts import render
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .qiniu_upload import upload_to_qiniu_and_get_url
from image import utils as image_utils
from utils import date_utils, feed_utils, redis_utils, tag_utils
from django.contrib.auth.models import AnonymousUser
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync
from websocket import utils as ws_utils
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
        user.image_num += 1
        user.save()
        serializer = ImageSerializer(image)
        # 缓存图片信息
        redis_utils.set_image_info(serializer.data,image.create_time)
        feed_utils.send(user.id, image.id, image.create_time)
        tag_utils.add_image(tag_utils.filter_tag(title), image.id,image.create_time)
        return Response(serializer.data)


@api_view(['GET', 'POST'])
def like_image(request, pk):
    """
    点赞图片
    :param request:
    :return:
    """
    if request.method == 'POST':

        """
        点赞图片
        """
        image = Image.objects.get(id=pk)
        if type(request.user) != AnonymousUser:
            try:
                redis_utils.add_like(request.user.id, pk)
                print("author_id:",image.author.id)
                async_to_sync(ws_utils.send_notice)(image.author.id, 'like', request.user.nickname+'赞了你图片')
                return Response({"msg": "点赞成功"})
            except Exception:
                return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(status.HTTP_401_UNAUTHORIZED)
    elif request.method == 'GET':
        """
        返回图片点赞数和点赞用户列表
        """
        try:
            page, len = image_utils.get_page_and_len(request, 0, 5)
            info={}
            info['like_nums'], info['users'] = image_utils.get_image_likes(pk, page, len)
            return Response(info)
        except Exception:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)


@login_required
@api_view(['POST'])
def unlike_image(request, pk):
    """
    取消点赞
    :param request:
    :param pk:
    :return:
    """
    try:
        redis_utils.remove_like(request.user.id, pk)
        return Response({'msg':'取消点赞成功'})
    except Exception:
        return Response(status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_image_detail(request, pk):
    """
    返回图片详细信息
    :param request:
    :return:
    """
    try:
        info = image_utils.get_image_info(request.user.id, pk)
        return Response(info)
    except Image.DoesNotExist:
        return Response(status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def view_image(request, pk):
    """
    获取图片总浏览数
    :param request:
    :param pk:
    :return:
    """
    if request.method == 'GET':
        return Response(redis_utils.get_views_num(pk))


@api_view(['GET', 'POST', 'DELETE'])
def image_comment(request, pk):
    """
    提交评论
    :param request:
    :param pk: 图片id
    :return:
    """
    if request.method == 'GET':
        page, len = image_utils.get_page_and_len(request, 0, 20)
        info = image_utils.get_image_comments(pk, page, len)
        return Response(info)

    elif request.method == 'POST':
        if type(request.user)!=AnonymousUser:
            try:
                image = Image.objects.get(id=pk)
                # reply_id = request.data.get('reply_id') or 0
                # reply_nickname = request.data.get('reply_nickname') or ""
                content = request.data.get('content')
                # image_utils.add_image_comment(pk, request.user, content, reply_id, reply_nickname)
                # # 更新日榜图片积分
                # redis_utils.add_score_dayrank(pk)
                users_dic = image_utils.get_nickname_from_content(request.data.get('content'))
                image_utils.add_image_comment(pk, request.user, content, users_dic)
                async_to_sync(ws_utils.send_notice)(image.author.id,'comment',request.user.nickname+':'+content)
                return Response({"msg":"评论成功"})
            except Exception:
                return Response(status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status.HTTP_401_UNAUTHORIZED)

    elif request.method == 'DELETE':
        if request.GET.__len__()==1:
            comment_id = request.GET.get('comment_id')
            try:
                comment = Comment.objects.get(id=comment_id)
                print(comment)
                comment.stauts=1
                comment.save()
                return Response({"msg": "删除评论成功"})
            except Comment.DoesNotExist:
                return Response(status.HTTP_400_BAD_REQUEST)
        return Response(status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_tag_images(request, tag):
    # tag = request.GET.get('tag')
    return Response(tag_utils.get_images(tag))


@api_view(['GET'])
def hots_day(request):
    """
    每日热门图片榜
    """
    page, len = image_utils.get_page_and_len(request, 0, 9)
    today = date_utils.get_today()
    results = redis_utils.get_hots_day(today, page*len, (page+1)*len-1)
    return Response(results)


@api_view(['GET'])
def hots_week(request):
    """
    每周热门图片榜
    """
    page, len = image_utils.get_page_and_len(request, 0, 9)
    this_weeks = date_utils.get_this_week()
    results = redis_utils.get_hots_week(this_weeks, page*len, (page+1)*len-1)
    return Response(results)


@api_view(['GET'])
def hots_month(request):
    """
    每月热门图片榜
    """
    page, len = image_utils.get_page_and_len(request, 0, 9)
    this_months = date_utils.get_this_month()
    results = redis_utils.get_hots_month(this_months, page*len, (page+1)*len-1)
    return Response(results)


