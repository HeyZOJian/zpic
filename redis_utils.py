import redis

POOL = redis.ConnectionPool(host='127.0.0.1',port=6379)


def get_connection():
    return redis.Redis(connection_pool=POOL)
