import logging
import random
from redis_client import RedisClient
from locust import TaskSet, task
from mqtt_client_factory import MQTTClientFactory

data = dict()
data['mqtt_host'] = "10.50.11.54"
data['mqtt_port'] = "30002"

cache = RedisClient()
cache.connect()

class IotDevice(TaskSet):

    def on_start(self):
        self.device_id = cache.next_device_id()

    @task
    def publish(self):
        logging.info("--publish--")

        client = MQTTClientFactory.new(self.device_id)
        client.connecting(host = data['mqtt_host'], port = data['mqtt_port'])
        