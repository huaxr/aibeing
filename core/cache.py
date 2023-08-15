# -*- coding: utf-8 -*-
# @Team: AIBeing
# @Author: huaxinrui@tal.com
import redis
from core import conf
class RedisClient:
    def __init__(self, host:str, port:int, db:int):
        self.host = host
        self.port = port
        self.db = db
        self.conn = redis.StrictRedis(host=host, port=port, db=db)

    def set_value(self, key: str, value:str, expires_secs: int):
        self.conn.set(key, value)
        # self.conn.expire(key, expires_secs)

    def get_value(self, key: str):
        return self.conn.get(key)

    def delete_key(self, key):
        self.conn.delete(key)

    def increment(self, key):
        self.conn.incr(key)

    def decrement(self, key):
        self.conn.decr(key)



redis_cli = RedisClient(host=conf.config.redis_host, port=int(conf.config.redis_port), db=int(conf.config.redis_db))
