from utils import redis_utils
import time


def send(user_id, image_id, date):
    """
    给好友的feed集合条件该图片信息
    :param user_id:
    :param image_id:
    :return:
    """
    print(user_id, image_id, date)
    # 所有粉丝列表
    score = time.mktime(date.timetuple())
    conn = redis_utils.get_connection()
    # 添加进自己的朋友圈
    key = 'moments:' + str(user_id)
    conn.zadd(key, image_id, score)
    print('>>>>>>>my-moments:add success...')
    key = 'user:' + str(user_id) + ':followings'
    print('>>>>key:',key)
    followings_list = conn.zrange(key, 0, -1)
    print('>>>>>list:',followings_list)
    # 遍历好友 推图片
    for id in followings_list:
        key = 'moments:'+ bytes.decode(id)
        print(">>>>>key:",key)
        conn.zadd(key, image_id, score)
        print(">>>>>friend-moments:add success...")


def follow_user(from_user_id, to_user_id):
    """
    关注用户， 将对方的图片信息添加进自己的朋友圈
    :param from_user_id:
    :param to_user_id:
    :return:
    """
    conn = redis_utils.get_connection()
    from_user_moments_key = 'moments:' + str(from_user_id)
    to_user_id_images_key = 'user:' + str(to_user_id) + ':images'
    conn.zunionstore(from_user_moments_key, [from_user_moments_key, to_user_id_images_key])


def unfollow_user(from_user_id, to_user_id):
    """
    取消关注，将对方的图片信息从自己的朋友圈中删除
    :param from_user_id:
    :param to_user_id:
    :return:
    """
    conn  = redis_utils.get_connection()
    from_user_moments_key = 'moments:' + str(from_user_id)
    to_user_id_images_key = 'user:' + str(to_user_id) + ':images'
    pipe = conn.pipeline()
    try:
        images_id = [bytes.decode(id) for id in conn.zrange(to_user_id_images_key, 0, -1)]
        for id in images_id:
            pipe.zrem(from_user_moments_key, id)
        pipe.execute()
    except Exception:
        print("朋友圈：取关失败")


def get_moments(user_id, page, len):
    """
    获取朋友圈
    :param user_id:
    :return:
    """
    conn = redis_utils.get_connection()
    key = 'moments:' + str(user_id)
    nums = conn.zcard(key)
    images_id = conn.zrevrange(key, page*len, (page+1)*len-1)
    print('>>>>>images_id:',images_id)
    if not images_id:
        key = 'user:'+str(user_id)+':followings'
        followings_list = conn.zrange(key, 0, -1)
        print('>>>>followings_list',followings_list)
        for id in followings_list:
            key = 'user:'+bytes.decode(id) + ':images'
            print(key)
            images = conn.zrange(key,0,-1,withscores=True)
            print(images)
            key = 'moments:'+str(user_id)
            for image_id,score in images:
                conn.zadd(key, image_id, score)
        key = 'moments:' + str(user_id)
        nums = conn.zcard(key)
        images_id = conn.zrevrange(key, page * len, (page + 1) * len - 1)
        return {"moments_num": nums, "images_id": [int(bytes.decode(id)) for id in images_id]}
    else:
        return {"moments_num": nums, "images_id": [int(bytes.decode(id)) for id in images_id]}
    # result = []
    # for id in images_id:
    #     result.append(redis_utils.get_image_info(bytes.decode(id)))
    # return result
    # return {"moments_num":nums,"images_id":[int(bytes.decode(id)) for id in images_id]}