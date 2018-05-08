from utils import redis_utils
import time


def add_offline_chat_message(user_id, notice):
    # conn = redis_utils.get_connection()
    # key = 'user:' + str(user_id) + ':chat:offline'
    pass


def add_unread_notice(user_id, notice):
    conn = redis_utils.get_connection()
    key = 'user:'+str(user_id)+':notice:unread'
    tab = (int(round(time.time() * 1000)))
    notice['tab']=tab
    conn.zadd(key,notice,tab)


def get_all_unread_notice(user_id, page, len):
    conn = redis_utils.get_connection()
    key = 'user:'+str(user_id)+':notice:unread'
    return conn.zrevrange(key, page*len, (page + 1)*len-1)


def read_notice(user_id, tab):
    conn = redis_utils.get_connection()
    key = 'user:' + str(user_id) + ':notice:unread'
    conn.zrem(key, tab)
