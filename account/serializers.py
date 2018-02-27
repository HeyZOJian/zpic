from rest_framework import serializers
from .models import User
from image.serializers import ImageSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','nickname','password','is_active','gender', 'phone_num'
                  'description','profile_photo_url', 'follow_num', 'following_num', 'image_num')


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username', 'nickname','description', 'gender', 'phone_num',
                  'profile_photo_url','follow_num', 'following_num', 'image_num')


class UserImagesSerializer(serializers.ModelSerializer):

    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'nickname', 'description', 'gender', 'phone_num',
                  'profile_photo_url', 'follow_num', 'following_num', 'image_num',  'images')


class UserFollowersSerializer(serializers.ModelSerializer):
    """
    序列化关注好友信息
    """
    user_b = LoginSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('user_b',)


class UserFollowingsSerializer(serializers.ModelSerializer):
    """
    序列化粉丝信息
    """
    user_a = LoginSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('user_a',)
