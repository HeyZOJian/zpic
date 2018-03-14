import redis
import time
import json
from account.serializers import UserSimpleSerializer
from rest_framework.renderers import JSONRenderer


DAY_SECOND = 60 * 60 * 24
WEEK_SECOND = DAY_SECOND * 7
POOL = redis.ConnectionPool(host='127.0.0.1',port=6379)


def get_connection():
    return redis.Redis(connection_pool=POOL)


def set_user_info(user_id, data):
    conn = get_connection()
    key = 'user:' + str(user_id) + ':info'
    conn.set(key, data)
    conn.expire(key, WEEK_SECOND)


def get_user_info(user_id):
    conn = get_connection()
    key = 'user:' + str(user_id) + ':info'
    queryset = conn.get(key)
    if queryset:
        return eval(conn.get(key))
    else:
        #TODO: 查数据库
        pass



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
    conn.zadd(from_user_key_name, to_user_id, t)
    conn.zadd(to_user_key_name, from_user_id, t)

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
    result = {}
    count = 1
    for user_id in queryset:
        result[str(count)] = get_user_info(str(user_id)[2:-1])
        count += 1
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
    result = {}
    count = 1
    for user_id in queryset:
        result[str(count)] = get_user_info(str(user_id)[2:-1])
        count += 1
    return result