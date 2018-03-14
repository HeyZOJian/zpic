from .models import User, UserRelationship
from .serializers import UserFollowingsSerializer,UserFollowersSerializer


def get_followers(user):
    """
    获取粉丝列表
    :param pk:
    :return:
    """
    queryset = UserRelationship.objects.filter(user_a=user, relation_type=0)
    users = UserFollowersSerializer(queryset, many=True)
    return users


def get_followings(pk):
    """
    获取关注列表
    :param pk:
    :return:
    """
    pass