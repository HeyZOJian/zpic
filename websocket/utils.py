from channels.layers import get_channel_layer
import time
import uuid
from utils import redis_utils
user_channels = {}


def channels_add(channels_name, user_id):
    user_channels[str(user_id)] = channels_name


def channels_remove(channels_name):
    user_channels.pop(channels_name)


def get_channel_name(user_id):
    channel_name = user_channels.get(str(user_id))
    if channel_name:
        return channel_name
    else:
        return ""


def is_online(user_id):
    return bool(user_channels.get(str(user_id)))


async def send_notice(user_id, notice_type, message):
    # 在线实时推，离线存redis
    print(">>>>>>>>>notice:")
    if is_online(user_id):
        channel_name = get_channel_name(str(user_id))
        channels_layout = get_channel_layer()
        await channels_layout.send(channel_name, {
            "type": "notice.message",
            "message": message,
            "notice_type": notice_type
        })
    notice = {
        "type": "notice.message",
        "message": message,
        "notice_type": notice_type,
    }
    add_unread_notice(user_id, notice)


def add_offline_chat_message(room_id, msg):
    conn = redis_utils.get_connection()
    key = 'room:' + str(room_id) + ':offlinemessage'
    score = int(time.time() * 1000000)
    conn.zadd(key, msg, score)


def get_all_offline_chat_message(room_id):
    conn = redis_utils.get_connection()
    key = 'room:' + str(room_id) + ':offlinemessage'
    return [eval(bytes(item).decode('utf-8')) for item in conn.zrevrange(key, 0, -1)]


def add_unread_notice(user_id, notice):
    conn = redis_utils.get_connection()
    key = 'user:' + str(user_id) + ':notice:unread'
    score = int(time.time()*1000000)
    notice['id'] = score
    conn.zadd(key, notice, score)


def get_all_unread_notice(user_id):
    results = {}
    conn = redis_utils.get_connection()
    key = 'user:' + str(user_id) + ':notice:unread'
    return [eval(item) for item in conn.zrevrange(key, 0, -1)]


def read_notice(user_id, notice_id):
    print(">>>delete")
    print(">>>userid:",user_id)
    conn = redis_utils.get_connection()
    key = 'user:' + str(user_id) + ':notice:unread'
    conn.zremrangebyscore(key, notice_id, notice_id)