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
        redis_utils.set_image_info(serializer.data)
        return Response(serializer.data)


@login_required
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
            page = 0
            len = 5
            if request.GET.__len__() == 2:
                page = int(request.GET.get('page')) - 1
                len = int(request.GET.get('len'))
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


@login_required
@api_view(['GET', 'POST', 'DELETE'])
def comment_image(request, pk):
    """
    提交评论
    :param request:
    :param pk: 图片id
    :return:
    """
    if request.method == 'GET':
        page = 0
        len = 5
        if request.GET.__len__() == 2:
            page = int(request.GET.get('page')) - 1
            len = int(request.GET.get('len'))
        info = image_utils.get_image_comments(pk, page, len)
        return Response(info)

    elif request.method == 'POST':
        try:
            content = request.data.get('comment')
            image = Image.objects.get(id=pk)
            comment = Comment(publisher=request.user, content=content, image=image)
            comment.save()
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
