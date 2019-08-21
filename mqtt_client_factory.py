import random
from mqtt_client import MQTTClient

class MQTTClientFactory():
    
    @staticmethod
    def new(devide_id):
        client_id = "{0}-{1}-{2}".format("locust", random.randint(1,111233),random.randint(1,111233))
        client = MQTTClient(client_id)
        client.set_device_id(devide_id)
        return client