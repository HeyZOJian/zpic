import re
from utils import redis_utils
from utils import date_utils


def filter_tag(content):
    """
    返回content中的标签
    :param content:
    :return:
    """
    return re.findall(r"#(\S+)", content)


def add_image(tags, image_id, date):
    """
    该标签下添加一张图片id
    :param tag:
    :param image_id:
    :param date:
    :return:
    """
    conn = redis_utils.get_connection()
    pipe = conn.pipeline()
    try:
        for tag in tags:
            key = 'tag:'+tag
            print(key,str(image_id) ,date_utils.Changetime(date))
            pipe.zadd(key, str(image_id), date_utils.Changetime(date))
        pipe.execute()
    except Exception:
        print('添加tag失败')


def get_images(tag):
    conn = redis_utils.get_connection()
    key = 'tag:' + tag
    images_id = [bytes.decode(id) for id in conn.zrange(key, 0, -1)]
    result = []
    for id in images_id:
        result.append(redis_utils.get_image_info(id))
    return {"images":result}
