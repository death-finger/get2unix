from django.core.cache import cache
from get2unix.settings import CACHES, config
import redis


def get_cache(key):
    return cache.get(key)


def write_cache(key, data, timeout=CACHES['default']['TIMEOUT']):
    try:
        cache.set(key, data, int(timeout))
        return ''
    except Exception as e:
        return e


class RedisOperator:
    def __init__(self, db):
        self.r = redis.Redis(host=config.get('redis', 'host'), port=config.get('redis', 'port'),
                             db=db, password=config.get('redis', 'password'))

    def set(self, key, value):
        return self.r.set(key, value, config.get('redis', 'timeout'))

    def get(self, key):
        return self.r.get(key)

    def keys(self, key):
        return self.r.keys(pattern=key)