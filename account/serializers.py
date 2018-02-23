from rest_framework import serializers
from .models import User
from image.serializers import ImageSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','nickname','password','is_active','description','profile_photo_url')


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username', 'nickname','description', 'profile_photo_url')


class UserImagesSerializer(serializers.ModelSerializer):

    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'nickname', 'description', 'profile_photo_url', 'images')


class UserFollowerSerializer(serializers.ModelSerializer):
    """
    序列化单个关注好友
    """
    user_b = LoginSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('user_b',)


class UserFollowersSerializer(serializers.ModelSerializer):
    """
    序列化多个关注好友
    """
    user_b = LoginSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('user_b',)
