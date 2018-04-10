import redis
import datetime
import time
import json
from account.serializers import UserSimpleSerializer
from account.models import User
from rest_framework.renderers import JSONRenderer
from utils import date_utils
import time

DAY_SECOND = 60 * 60 * 24
WEEK_SECOND = DAY_SECOND * 7
MONTH_SECOND = DAY_SECOND * 30

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
    queryset = conn.zrange(key, page*len, (page + 1)*len)
    result = []
    for user_id in queryset:
        result.append(get_user_info(str(user_id)[2:-1]))
    return result


def get_follower_num(user_id):
    """
    获取关注数
    :param user_id:
    :return:
    """
    conn = get_connection()
    key = 'user:' + str(user_id) + ':followers'
    return conn.zcard(key)


def get_following(user_id, page=0, len=10):
    """
    获取缓存中的粉丝列表
    :param user_id:
    :return:
    """
    conn = get_connection()
    key = 'user:' + str(user_id) + ':followings'
    queryset = conn.zrange(key, page*len, (page + 1) * len)
    result = []
    for user_id in queryset:
        result.append(get_user_info(str(user_id)[2:-1]))
    return result


def get_following_num(user_id):
    """
    获取粉丝数
    :param user_id:
    :return:
    """
    conn = get_connection()
    key = 'user:' + str(user_id) + ':followings'
    return conn.zcard(key)


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


def get_followers_num(user_id):
    conn = get_connection()
    key = 'user:' + str(user_id) + ':followers'
    return conn.zcard(key)


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


def get_followings_num(user_id):
    conn = get_connection()
    key = 'user:' + str(user_id) + ':followings'
    return conn.zcard(key)

def set_image_info(info, date):
    """
    缓存图片信息
    :param info:
    :return:
    """
    user_id = str(info.get('author'))
    image_id = str(info.get('id'))
    conn = get_connection()
    pipe = conn.pipeline()
    image_key = 'image:' + image_id + ":info"
    user_image_set_key = 'user:'+user_id + ':images'
    try:
        pipe.set(image_key, info)
        pipe.zadd(user_image_set_key, image_id, date_utils.Changetime(date))
        pipe.zadd('moments:'+str(user_id), image_id, date_utils.Changetime(date))
        pipe.expire(image_id, MONTH_SECOND)
        pipe.execute()
    except Exception:
        print('缓存图片失败')


def get_image_info(image_id):
    """
    获取缓存中的图片信息
    :param image_id:
    :return:
    """
    conn = get_connection()
    key = 'image:' + str(image_id) + ':info'
    info = conn.get(key)
    if info:
        return eval(info)
    else:
        return None


def add_comments(image_id, comment_info):
    """
    添加图片评论信息
    :param image_id:
    :return:
    """
    conn = get_connection()
    key = 'image:' + str(image_id) + ':comments'
    t = (int(round(time.time() * 1000)))
    conn.zadd(key,comment_info, t)


def get_comments(image_id, page, len):
    """
    获取图片评论信息
    :param image_id:
    :return:
    """
    conn = get_connection()
    key = 'image:' + str(image_id) + ':comments'
    return conn.zcard(key), conn.zrange(key,page*len, (page+1)*len)

def add_view_num(image_id):
    """
    图片浏览数+1
    :param image_id:
    :return:
    """
    conn = get_connection()
    pipe = conn.pipeline()
    view_key = 'views:' + str(image_id)
    hot_key = 'hots:' + str(date_utils.get_today())
    try:
        pipe.incrby(view_key, 1)
        pipe.zincrby(hot_key, image_id, 1)
        pipe.execute()
    except Exception:
        pass
#     TODO:浏览数%100==0持久化到数据库


def get_views_num(image_id):
    """
    获取图片浏览数
    :param image_id:
    :return:
    """
    conn = get_connection()
    key = 'views:' + str(image_id)
    return conn.get(key)


def add_like(user_id, image_id):
    """
    缓存图片的点赞列表
    :param user_id: 点赞的人id
    :param image_id: 图片id
    :return:
    """
    conn = get_connection()
    pipe = conn.pipeline()
    image_key = 'image:' + str(image_id) + ':likes'
    hot_key = 'hots:' + str(date_utils.get_today())
    t = (int(round(time.time() * 1000)))
    try:
        if conn.zrank(image_key, user_id) == None:
            pipe.zadd(image_key, user_id, t)
            pipe.zincrby(hot_key, image_id, 2)
            pipe.execute()
    except Exception:
        print("点赞缓存失败")


def remove_like(user_id, image_id):
    """
    取消点赞
    :param user_id:
    :param image_id:
    :return:
    """
    conn = get_connection()
    key = 'image:' + str(image_id) + ':likes'
    conn.zrem(key, user_id)


def get_image_likes(image_id):
    """
    获取图片的点赞列表
    :param image_id:
    :return:
    """
    conn = get_connection()
    key = 'image:' + str(image_id) + ':likes'
    users = conn.zrevrange(key, 0, -1)
    result = []
    for user_id in users:
        result.append(get_user_info(user_id))
    return result

def have_liked_image(user_id, img_id):
    """
    是否点赞图片
    :param user_id:
    :param img_id:
    :return:
    """
    users = get_image_likes(img_id)
    for user in users:
        if user.get('id') == user_id:
            return True
    return False

def add_score_dayrank(image_id):
    """
    评论后更新日榜积分
    :param image_id:
    :return:
    """
    key = 'hots:' + str(date_utils.get_today())
    conn = get_connection()
    conn.zincrby(key, image_id, 2.5)


def get_hots_day(date, start, end):
    """
    获取当日热门图片
    :param date:
    :param start:
    :param end:
    :return:
    """
    conn = get_connection()
    key = 'hots:' + str(date)
    id_lists = conn.zrevrange(key, start, end)
    results = []
    for id in id_lists:
        results.append(get_image_info(int(id)))
    return results


def get_hots_week(days, start, end):
    conn = get_connection()
    key = 'hots:this_week'
    try:
        # TODO: 事务问题
        weeks = ['hots:'+day for day in days]
        conn.zunionstore(key, weeks)
        id_lists = conn.zrevrange(key, start, end)
        results = []
        for id in id_lists:
            results.append(get_image_info(int(id)))
        return results
    except Exception as e:
        print(e)


def get_hots_month(days, start, end):
    conn = get_connection()
    key = 'hots:this_month'
    try:
        # TODO: 事务问题
        weeks = ['hots:' + day for day in days]
        conn.zunionstore(key, weeks)
        id_lists = conn.zrevrange(key, start, end)
        results = []
        for id in id_lists:
            results.append(get_image_info(int(id)))
        return results
    except Exception as e:
        print(e)
