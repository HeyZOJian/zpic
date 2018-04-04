from django.shortcuts import render
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .qiniu_upload import upload_to_qiniu_and_get_url
from utils.redis_utils import get_connection
from static_settings import *
from utils import redis_utils
from rest_framework.renderers import JSONRenderer
from image import utils as image_utils
from utils import date_utils
from utils import feed_utils


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
        serializer = ImageSerializer(image)
        # 缓存图片信息
        redis_utils.set_image_info(serializer.data,image.create_time)
        feed_utils.send(user.id, image.id, image.create_time)
        return Response(serializer.data)

# TODO: 未登录时GET 只能获取点赞数
# @login_required
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
        # TODO：通知图片主人
        try:
            redis_utils.add_like(request.user.id, pk)
            return Response({"msg": "点赞成功"})
        except Exception:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        info = image_utils.get_image_info(pk)
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


# TODO: get的登陆权限，delete判断是否为用户自己本身
# @login_required
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
        try:
            reply_id = request.data.get('reply_id')
            reply_nickname = request.data.get('reply_nickname')
            content = request.data.get('comment')
            image_utils.add_image_comment(pk, request.user, content, reply_id, reply_nickname)
            # 更新日榜图片积分
            redis_utils.add_score_dayrank(pk)
            return Response('评论成功')
        except Exception:
            return Response(status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if request.GET.__len__()==1:
            comment_id = request.GET.get('comment_id')
            try:
                comment = Comment.objects.get(id=comment_id)
                print(comment)
                comment.stauts=1
                comment.save()
                return Response({"msg":"删除评论成功"})
            except Comment.DoesNotExist:
                return Response(status.HTTP_400_BAD_REQUEST)
        return Response(status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def hots_day(request):
    """
    每日热门图片榜
    """
    page, len = image_utils.get_page_and_len(request, 0, 12)
    today = date_utils.get_today()
    results = redis_utils.get_hots_day(today, page*len, (page+1)*len-1)
    return Response(results)


@api_view(['GET'])
def hots_week(request):
    """
    每周热门图片榜
    """
    page, len = image_utils.get_page_and_len(request, 0, 12)
    this_weeks = date_utils.get_this_week()
    results = redis_utils.get_hots_week(this_weeks, page*len, (page+1)*len-1)
    return Response(results)


@api_view(['GET'])
def hots_month(request):
    """
    每月热门图片榜
    """
    page, len = image_utils.get_page_and_len(request, 0, 12)
    this_months = date_utils.get_this_month()
    results = redis_utils.get_hots_month(this_months, page*len, (page+1)*len-1)
    return Response(results)


