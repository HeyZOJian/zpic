from django.shortcuts import render
from django.http import HttpResponseRedirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from django.contrib.auth.hashers import make_password,check_password
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import *
from .serializers import *
from image.qiniu_upload import upload_to_qiniu_and_get_url
from utils import redis_utils
from image.models import Image
import account.utils as account_utils
from utils import feed_utils
from asgiref.sync import sync_to_async, async_to_sync
from channels.auth import get_user
from websocket import utils as ws_utils
# User

# ========================================注册登录退出=======================================


@api_view(['POST'])
def check_username(request):
    """
    检查用户名存在性
    :param request:
    :return:
    """
    username = request.data.get('username')
    if len(User.objects.filter(username=username)):
        return Response({"msg": "该用户名已被注册"})
    return Response({"msg": "该用户可用"})


@api_view(['POST'])
def check_nickname(request):
    """
    检查昵称存在性
    :param request:
    :return:
    """
    nickname = request.data.get('nickname')
    if len(User.objects.filter(nickname=nickname)):
        return Response({"msg": "该昵称已被注册"})
    return Response({"msg": "该昵称可用"})


@api_view(['GET', 'POST'])
def user_register(request):
    """
    用户注册
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'user/register.html')
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        nickname = request.data.get('nickname')
        User(username=username,nickname=nickname,password=make_password(password)).save()
        return Response(status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def user_login(request):
    """
    用户登录
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request,'user/login.html')
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        print(username,password)
        try:
            res = Response()
            user = User.objects.get(username=username)
            if check_password(password, user.password):
                login(request, user)
                info = UserIndexSerializer(user).data
                info['sessionid'] = request.session.session_key
                # redis_utils.set_user_info(user.id, info)
                res.data = {"msg": "success", "userInfo": info}
                res.status_code = 200
                return res
            else:
                res.data={"msg": "fail"}
                res.status_code = 400
                return res
        except User.DoesNotExist:
            res.data = {"msg": "fail"}
            res.status_code = 400
            return res


@api_view(['GET'])
def user_logout(request):
    logout(request)
    return Response({"msg":"退出成功"})

# ========================================用户操作=======================================


@login_required
@api_view(['PUT'])
def user_update(request):
    # TODO: 字段验证
    """
    更新个人资料
    :param request:
    :return:
    """
    try:
        user = request.user
        user.nickname = request.data.get('nickname') if request.data.get('nickname') != "" else user.nickname
        user.description = request.data.get('description') if request.data.get('description') != "" else user.description
        user.gender = request.data.get('gender') if request.data.get('gender') != "" else user.gender
        user.phone_num = request.data.get('phone_num') if request.data.get('phoneNum') != "" else user.phone_num
        user.save()
        return Response({"msg": "更新资料成功"})
    except Exception:
        return Response(status.HTTP_400_BAD_REQUEST)


@login_required
@api_view(['POST'])
def change_profile_photo(request):
    """
    更改头像
    :param request:
    :return:
    """
    obj = request.FILES.get('image')
    # 上传七牛云并返回外链
    url = upload_to_qiniu_and_get_url(obj)
    try:
        user = User.objects.get(id=request.user.id)
        user.profile_photo_url=url
        user.save()
        return Response({"msg": "更改头像成功"})
    except Exception:
        return Response(status.HTTP_400_BAD_REQUEST)


@login_required
def user_detail(request, pk):
    user = User.objects.get(pk=pk)
    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(['GET'])
def user_index(request, nickname):
    """
    用户个人主页
    :param request:
    :return:
    """
    # print(">>>>>>>>user:"+get_user())
    page, len = account_utils.get_page_and_len(request, 0, 20)
    try:
        user = User.objects.get(nickname=nickname)
        if user.id != request.user.id and user.status==1:
            return Response({'type':'personal'})
        else:
            info = {}
            info['userInfo'] = UserIndexSerializer(user).data
            info['userInfo']['followers_num'] = redis_utils.get_follower_num(user.id)
            info['userInfo']['followings_num'] = redis_utils.get_following_num(user.id)
            images = Image.objects.filter(author_id=user.id).order_by('-create_time')[page*len: (page+1)*len]
            images_id = []
            for image in images:
                images_id.append(image.id)
                redis_utils.set_image_info(ImageSerializer(image).data, image.create_time)
            info['images_id'] = images_id
            return Response(info)
    except User.DoesNotExist:
        return Response(status.HTTP_404_NOT_FOUND)

# ========================================好友操作=======================================

@login_required
@api_view(['GET'])
def user_followers(request,nickname):
    """
    用户的关注列表
    :param request:
    :return:
    """
    # TODO:没有筛掉被封的用户
    try:
        # user_id = request.user.id
        user_id = User.objects.get(nickname=nickname).id
        page, len = account_utils.get_page_and_len(request, 0, 10)
        result = redis_utils.get_follower(user_id, page, len)
        if result:
            return Response(result)
        else:
            queryset = UserRelationship.objects.filter(user_a=request.user, relation_type=0).order_by('create_time')
            users = UserFollowersSerializer(queryset, many=True)
            content = eval(JSONRenderer().render(users.data))
            redis_utils.set_followers(request.user.id, content)
            result = redis_utils.get_follower(user_id, page, len)
            return Response(result)
    except UserRelationship.DoesNotExist:
        return Response(status.HTTP_400_BAD_REQUEST)


@login_required
@api_view(['GET'])
def user_followings(request, nickname):
    """
    用户的粉丝列表
    :param request:
    :return:
    """
    # TODO:没有筛掉被封的用户
    try:
        # user_id = request.user.id
        user_id = User.objects.get(nickname=nickname).id
        page, len = account_utils.get_page_and_len(request, 0, 10)
        result = redis_utils.get_following(user_id, page, len)
        if result:
            return Response(result)
        else:
            queryset = UserRelationship.objects.filter(user_b=request.user, relation_type=0)
            users = UserFollowingsSerializer(queryset, many=True)
            content = eval(JSONRenderer().render(users.data))
            redis_utils.set_followings(request.user.id, content)
            result = redis_utils.get_following(user_id, page, len)
            return Response(result)
    except UserRelationship.DoesNotExist:
        return Response(status.HTTP_400_BAD_REQUEST)


@login_required
@api_view(['POST'])
def follow_user(request, pk):
    """
    关注用户
    :param pk: 关注id
    :param request:
    :return:
    """
    user_a = request.user
    # 关注自己
    if user_a.id == pk:
        return Response(status.HTTP_400_BAD_REQUEST)
    try:
        user_b = User.objects.get(id=str(pk))
        relation = UserRelationship(user_a=user_a, user_b=user_b)
        relation.save()
        # 增加关注
        redis_utils.follow_user(user_a.id, user_b.id)
        feed_utils.follow_user(user_a.id, user_b.id)
        async_to_sync(ws_utils.send_notice)(user_b.id, 'friend', user_a.nickname+'关注你了')
        return Response({"msg": "关注成功"})
    except User.DoesNotExist:
        return Response(status.HTTP_400_BAD_REQUEST)



@login_required
@api_view(['POST'])
def unfollow_user(request, pk):
    """
    取消关注用户
    :param request:
    :param pk:
    :return:
    """
    user_a = request.user
    # 取关自己
    if user_a.id == pk:
        return Response(status.HTTP_400_BAD_REQUEST)
    try:
        user_b = User.objects.get(id=str(pk))
        UserRelationship.objects.filter(user_a=user_a,user_b=user_b).delete()
        redis_utils.unfollow_user(user_a.id, user_b.id)
        feed_utils.unfollow_user(user_a.id, user_b.id)
        return Response({"msg": "取消关注成功"})
    except User.DoesNotExist:
        return Response(status.HTTP_400_BAD_REQUEST)


@login_required
@api_view(['GET'])
def moments(request):
    """
    查看朋友圈
    :param request:
    :return:
    """
    page, len = account_utils.get_page_and_len(request, 0, 20)
    return Response(feed_utils.get_moments(request.user.id, page,len))


@api_view(['GET'])
def search_user(request):
    keyword = request.GET.get('keyword')
    user_list = User.objects.filter(nickname__icontains=keyword)
    results = []
    for user in user_list:
        results.append(redis_utils.get_user_info(user.id))
    return Response(results)


@login_required
@api_view(['POST'])
def lock_account(request):
    user = User.objects.get(id=request.user.id)
    user.status=1
    user.save()
    return Response({'msg':'ok'})


@login_required
@api_view(['POST'])
def unlock_account(request):
    user = User.objects.get(id=request.user.id)
    user.status=0
    user.save()
    return Response({'msg':'ok'})
