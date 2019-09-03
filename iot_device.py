import os
import logging
import random
import time
import json
from redis_client import RedisClient
from locust import TaskSet, task
from utils import Utils
import paho.mqtt.publish as publish

from payload import PayloadGenerator

MQTT_HOST = os.environ.get("DOJOT_MQTT_HOST", "127.0.0.1")
MQTT_PORT = os.environ.get("DOJOT_MQTT_PORT", "1883")
MQTT_QOS = 1
REQUEST_TYPE = "mqtt"

cache = RedisClient()
cache.connect()

class IotDevice(TaskSet):

    def on_start(self):
        self.device_id = cache.next_device_id()
        self.topic = "/admin/{}/attrs".format(str(self.device_id))
        self.client_id = "admin:{}".format(str(self.device_id))
        self.payload_gen = PayloadGenerator()

    @task
    def publish(self):
        start_time = time.time()

        try:
            publish.single(topic=self.topic, payload=json.dumps(self.payload_gen.next()), qos=MQTT_QOS, hostname=MQTT_HOST, port=MQTT_PORT, client_id=self.client_id)
            Utils.fire_locust_success(
                request_type=REQUEST_TYPE,
                name='publish',
                response_time=Utils.time_delta(start_time, time.time()),
                response_length=0
            )
        except Exception as e:
            Utils.fire_locust_failure(
                request_type=REQUEST_TYPE,
                name='publish',
                response_time=Utils.time_delta(start_time, time.time()),
                exception=e
            )
