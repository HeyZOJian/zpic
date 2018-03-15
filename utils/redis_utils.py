import redis
import time
import json
from account.serializers import UserSimpleSerializer
from account.models import User
from rest_framework.renderers import JSONRenderer


DAY_SECOND = 60 * 60 * 24
WEEK_SECOND = DAY_SECOND * 7
POOL = redis.ConnectionPool(host='127.0.0.1',port=6379)


def get_connection():
    return redis.Redis(connection_pool=POOL)


def set_user_info(user_id, data):
    """
    将用户简要信息放入redis
    :param user_id:
    :param data:
    :return:
    """
    conn = get_connection()
    key = 'user:' + str(user_id) + ':info'
    conn.set(key, data)
    conn.expire(key, WEEK_SECOND)


def get_user_info(user_id):
    """
    获取缓存中的个人简要信息
    :param user_id:
    :return:
    """
    conn = get_connection()
    key = 'user:' + str(user_id) + ':info'
    queryset = conn.get(key)
    if queryset:
        return eval(conn.get(key))
    else:
        user = User.objects.get(id=user_id)
        serializer = UserSimpleSerializer(user)
        set_user_info(user.id, serializer.data)
        return serializer.data


def follow_user(from_user_id, to_user_id):
    """
    在缓存中添加好友关系
    :param from_user_id:
    :param to_user_id:
    :return:
    """
    conn = get_connection()
    from_user_key_name = 'user:' + str(from_user_id) + ':followers'
    to_user_key_name = 'user:' + str(to_user_id) + ':followings'
    # 毫秒级时间戳
    t = (int(round(time.time() * 1000)))
    try:
        pipe = conn.pipeline()
        pipe.zadd(from_user_key_name, to_user_id, t)
        pipe.zadd(to_user_key_name, from_user_id, t)
        pipe.execute()
    except redis.RedisError:
        print("关注失败")

def unfollow_user(from_user_id, to_user_id):
    """
    在缓存中删除好友关系
    :param from_user_id:
    :param to_user_id:
    :return:
    """
    conn = get_connection()
    pipe = conn.pipeline()
    from_user_key_name = 'user:' + str(from_user_id) + ':followers'
    to_user_key_name = 'user:' + str(to_user_id) + ':followings'
    try:
        pipe.zrem(from_user_key_name, to_user_id)
        pipe.zrem(to_user_key_name, from_user_id)
        pipe.execute()
    except Exception:
        print("取关失败")


def get_follower(user_id, page=0, len=10):
    """
    获取缓存中的关注列表
    :param len:
    :param page:
    :param user_id:
    :return:
    """
    conn = get_connection()
    key = 'user:' + str(user_id) + ':followers'
    queryset = conn.zrange(key, page, (page + 1)*len)
    result = []
    for user_id in queryset:
        result.append(get_user_info(str(user_id)[2:-1]))
    return result


def get_following(user_id, page=0, len=10):
    """
    获取缓存中的粉丝列表
    :param user_id:
    :return:
    """
    conn = get_connection()
    key = 'user:' + str(user_id) + ':followings'
    queryset = conn.zrange(key, page, (page + 1) * len)
    result = []
    for user_id in queryset:
        result.append(get_user_info(str(user_id)[2:-1]))
    return result


def set_followers(from_user_id, contents):
    """
    将关注列表放入缓存
    :param from_user_id:
    :param to_user_ids:
    :return:
    """
    conn = get_connection()
    pipe = conn.pipeline()
    from_user_key_name = 'user:' + str(from_user_id) + ':followers'
    try:
        count = 1
        for info in contents:
            to_user_id = str(info.get('user_b').get('id'))
            pipe.zadd(from_user_key_name, to_user_id, count)
            count += 1
        pipe.execute()
    except Exception:
        pass


def set_followings(from_user_id, contents):
    """
    将粉丝列表放入缓存
    :param from_user_id:
    :param contents:
    :return:
    """
    conn = get_connection()
    pipe = conn.pipeline()
    from_user_key_name = 'user:' + str(from_user_id) + ':followings'
    try:
        count = 1
        for info in contents:
            to_user_id = str(info.get('user_b').get('id'))
            pipe.zadd(from_user_key_name, to_user_id, count)
            count += 1
        pipe.execute()
    except Exception:
        pass


def set_image_info(content):
    image_id = str(content.get('id'))
    conn = get_connection()
    key = 'image:' + image_id + ":info"
    conn.set(key, content)


def get_image_info(image_id):
    pass