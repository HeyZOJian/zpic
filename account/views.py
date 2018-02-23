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

# User


@api_view(['GET', 'POST'])
def user_register(request):
    if request.method == 'GET':
        return render(request, 'user/register.html')
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        nickname = request.data.get('nickname')
        try:
            User.objects.get(username=username)
            res = {"error": "邮箱已被注册"}
            return Response(res)
        except User.DoesNotExist:
            try:
                User.objects.get(nickname=nickname)
                res = {"error": "用户名已被注册"}
                return Response(res)
            except User.DoesNotExist:
                User(username=username,nickname=nickname,password=make_password(password)).save()
                return HttpResponseRedirect('../login')


@api_view(['GET', 'POST'])
def user_login(request):
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
                return Response({"error": "账户或密码错误"})
        except User.DoesNotExist:
            return Response(status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_logout(request):
    logout(request)
    return Response({"msg":"退出成功"})


@login_required
@api_view(['PUT'])
def user_update(request):
    data = JSONParser().parse(request)
    serializer = UserSerializer(User, data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


# TODO: 权限设置
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
# TODO：权限设置


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
        if len(queryset) == 1:
            users = UserFollowerSerializer(queryset, many=True)
        else:
            users = UserFollowersSerializer(queryset, many=True)
        return Response(users.data)
    except UserRelationship.DoesNotExist:
        return Response(status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_followings(request):
    """
    用户的粉丝列表
    :param request:
    :return:
    """
    # TODO:没有筛掉被封的用户
    # try:
    #     queryset = UserRelationship.objects.filter(user_b=request.user, relation_type=0)
    #     if len(queryset) == 1:
    #         users = UserFollowingSerializer(queryset, many=True)
    #     else:
    #         users = UserFollowingsSerializer(queryset, many=True)
    #     return Response(users.data)
    # except UserRelationship.DoesNotExist:
    #     return Response(status.HTTP_400_BAD_REQUEST)
    pass


@api_view(['POST'])
def follow_user(request, pk):
    """
    关注用户
    :param pk: 关注id
    :param request:
    :return:
    """
    user_a = request.user
    try:
        user_b = User.objects.get(id=str(pk))
        relation = UserRelationship(user_a=user_a, user_b=user_b)
        relation.save()
        return Response({"msg": "关注成功"})
    except User.DoesNotExist:
        return Response(status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response(status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def unfollow_user(request, pk):
    """
    取消关注用户
    :param request:
    :param pk:
    :return:
    """
    user_a = request.user
    try:
        user_b = User.objects.get(id=str(pk))
        UserRelationship.objects.filter(user_a=user_a,user_b=user_b).delete()
        return Response({"msg": "取消关注成功"})
    except User.DoesNotExist:
        return Response(status.HTTP_400_BAD_REQUEST)