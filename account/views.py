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
        return HttpResponseRedirect('../login')


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
        try:
            user = User.objects.get(username=username)
            if check_password(password, user.password):
                login(request, user)
                return HttpResponseRedirect('../../moments')
            else:
                return Response({"msg": "账户或密码错误"})
        except User.DoesNotExist:
            return Response(status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_logout(request):
    logout(request)
    return Response({"msg":"退出成功"})

# ========================================用户操作=======================================


@login_required
@api_view(['PUT'])
def user_update(request):
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
        user.phone_num = request.data.get('phone_num') if request.data.get('phone_num') != "" else user.phone_num
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
    try:
        user = User.objects.get(nickname=nickname)
        serializer = UserImagesSerializer(user)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response(status.HTTP_400_BAD_REQUEST)

# ========================================好友操作=======================================

@login_required
@api_view(['GET'])
def user_followers(request):
    """
    用户的关注列表
    :param request:
    :return:
    """
    # TODO:没有筛掉被封的用户
    try:
        queryset = UserRelationship.objects.filter(user_a=request.user, relation_type=0)
        users = UserFollowersSerializer(queryset, many=True)
        return Response(users.data)
    except UserRelationship.DoesNotExist:
        return Response(status.HTTP_400_BAD_REQUEST)

@login_required
@api_view(['GET'])
def user_followings(request):
    """
    用户的粉丝列表
    :param request:
    :return:
    """
    # TODO:没有筛掉被封的用户
    try:
        queryset = UserRelationship.objects.filter(user_b=request.user, relation_type=0)
        users = UserFollowingsSerializer(queryset, many=True)
        return Response(users.data)
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
        # 增加关注，粉丝数量
        # TODO: 原子性？
        user_a.following_num += 1
        user_b.follow_num += 1
        user_a.save()
        user_b.save()

        return Response({"msg": "关注成功"})
    except User.DoesNotExist:
        return Response(status.HTTP_400_BAD_REQUEST)
    except Exception:
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
        result, row = UserRelationship.objects.filter(user_a=user_a,user_b=user_b).delete()
        # 减少关注，粉丝数量
        if result:
            user_a.following_num -= 1
            user_b.follow_num -= 1
            user_a.save()
            user_b.save()
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
    # TODO:获取关注好友的图片
    user = request.user
    serializer = LoginSerializer(user)
    return Response(serializer.data)