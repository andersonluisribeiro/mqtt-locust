import logging
import redis

class RedisClient():

    def connect(self):
        try:
            self.cache = redis.Redis(host='redis', port=6379, db=0)
            logging.info("connected to redis")
        except Exception as e:
            logging.error("error on connect to redis")


    def next_device_id(self):
        try:
            device_count = self.cache.incr('device_count')
            device_id = self.cache.get(device_count)
            return device_id
        except Exception as e:
            logging.error("error to get device identifier")