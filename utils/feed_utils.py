from utils import redis_utils
import time

def send(user_id, image_id, date):
    """
    给好友的feed集合条件该图片信息
    :param user_id:
    :param image_id:
    :return:
    """
    # 所有粉丝列表
    score = time.mktime(date.timetuple())
    conn = redis_utils.get_connection()
    pipe = conn.pipeline()
    try:
        # 添加进自己的朋友圈
        key = 'moments:' + str(user_id)
        pipe.zadd(key, image_id, score)
        key = 'user:' + str(user_id) + ':followings'
        followings_list = pipe.zrange(key, 0, -1)
        # 遍历好友 推图片
        for id in followings_list:
            key = 'moments:'+ bytes.decode(id)
            pipe.zadd(key, image_id, score)
        pipe.execute()
    except Exception:
        print('send error')


def follow(from_user_id, to_user_id):
    """
    关注用户， 将对方的图片信息添加进自己的朋友圈
    :param from_user_id:
    :param to_user_id:
    :return:
    """
    conn = redis_utils.get_connection()
    from_user_moments_key = 'moments:' + str(from_user_id)
    to_user_id_images_key = 'user:' + str(to_user_id) + ':images'
    print(from_user_moments_key, to_user_id_images_key)
    conn.zunionstore(from_user_moments_key, [from_user_moments_key, to_user_id_images_key])
    print("merge")


def get_moments(user_id, page, len):
    """
    获取朋友圈
    :param user_id:
    :return:
    """
    conn = redis_utils.get_connection()
    key = 'moments:' + str(user_id)
    images_id = conn.zrange(key, page*len, (page+1)*len)
    # result = []
    # for id in images_id:
    #     result.append(redis_utils.get_image_info(bytes.decode(id)))
    # return result
    return [int(bytes.decode(id)) for id in images_id]