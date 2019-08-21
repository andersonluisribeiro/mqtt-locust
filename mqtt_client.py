import paho.mqtt.client as mqtt
import logging
import random
import time
import redis
import json

from message import Message
from utils import Utils

TENANT = "admin"
PUBLISH_TIMEOUT = 5000
REQUEST_TYPE = 'MQTT'
MESSAGE_TYPE_PUB = 'PUB'


class LocustError(Exception):
    pass


class TimeoutError(ValueError):
    pass


class ConnectError(Exception):
    pass


class DisconnectError(Exception):
    pass


class MQTTClient(mqtt.Client):

    def __init__(self, *args, **kwargs):
        super(MQTTClient, self).__init__(*args, **kwargs)
        self.on_connect = self.locust_on_connect
        self.on_publish = self.locust_on_publish
        self.on_disconnect = self.locust_on_disconnect
        self.pubmmap = {}
        self.is_connected = False

    def set_device_id(self, device_id):
        self.device_id = device_id    
    
    def connecting(self, host, port):
        logging.info("--connecting--")

        self.start_time = time.time()
        try:
            super(MQTTClient, self).connect_async(host=host, port=port, keepalive=600)  
            super(MQTTClient, self).loop_start()
        except Exception as e:
            logging.error(str(e))
            Utils.fire_locust_failure(
                request_type=REQUEST_TYPE,
                name='connect',
                response_time=time_delta(self.start_time, time.time()),
                exception=ConnectError("Could not connect to host:["+host+"]")
            )    


    def locust_on_connect(self, client, flags_dict, userdata, rc):
        logging.info("--on_connect--")

        if rc == 0:
            self.is_connected = True

            Utils.fire_locust_success(
                request_type=REQUEST_TYPE,
                name='connect',
                response_time=0,
                response_length=0
            )

            try:
                topic = "/{0}/{1}/attrs".format(TENANT, self.device_id)
                payload = {
                    'temperature': random.randrange(0,10,1)
                } 

                self.publishing(
                    topic=topic,
                    payload=json.dumps(payload),
                    qos=1,
                    timeout=PUBLISH_TIMEOUT)
            except Exception as e:
                logging.error(str(e)) 
                Utils.fire_locust_failure(
                    request_type=REQUEST_TYPE,
                    name='connect',
                    response_time=0,
                    exception=e
                )       


    def publishing(self, topic, payload=None, qos=0, retry=5, name='messages', **kwargs):
        logging.info("--publishing--")

        timeout = kwargs.pop('timeout', 10000)
        start_time = time.time()

        try:
            res = super(MQTTClient, self).publish(
                    topic,
                    payload=payload,
                    qos=qos,
                    retain=False,
                    **kwargs
                )
            [ err, mid ] = res

            if err:
                logging.error(str(err)) 
                Utils.fire_locust_failure(
                    request_type=REQUEST_TYPE,
                    name=name,
                    response_time=time_delta(start_time, time.time()),
                    exception=ValueError(err)
                )

            self.pubmmap[mid] = Message(
                MESSAGE_TYPE_PUB, qos, topic, payload, start_time, timeout, name
            )

            logging.info("publish: err,mid:"+str(err)+","+str(mid)+"")
          
        except Exception as e:
            logging.error(str(e))   
            Utils.fire_locust_failure(
                request_type=REQUEST_TYPE,
                name=name,
                response_time=time_delta(start_time, time.time()),
                exception=e,
            )

    def locust_on_publish(self, client, userdata, mid):
        logging.info("--locust_on_publish--")

        end_time = time.time()
        message = self.pubmmap.pop(mid, None)  

        if message is None:
            logging.info("message is none")
            Utils.fire_locust_failure(
                request_type=REQUEST_TYPE,
                name="message_found",
                response_time=0,
                exception=ValueError("Published message could not be found"),
            )
            return
        
        total_time = Utils.time_delta(message.start_time, end_time)
        logging.info("total time: " + str(total_time))

        if message.timed_out(total_time):
            logging.error("publish timed out")
            Utils.fire_locust_failure(
                request_type=REQUEST_TYPE,
                name=message.name,
                response_time=total_time,
                exception=TimeoutError("publish timed out"),
            )
        else:
            logging.info("message sent")
            Utils.fire_locust_success(
                request_type=REQUEST_TYPE,
                name=message.name,
                response_time=total_time,
                response_length=len(message.payload),
            )

        if self.is_connected:
            self.disconnecting()           


    def disconnecting(self):
        logging.info("--disconnecting--")
        super(MQTTClient, self).disconnect()
        self.is_connected = False


    def locust_on_disconnect(self, client, userdata, rc):
        logging.info("--locust_on_disconnect--, RC: " + str(rc))

        super(MQTTClient, self).loop_stop()

        if rc != 0:
            Utils.fire_locust_failure(
                request_type=REQUEST_TYPE,
                name='disconnect',
                response_time=0,
                exception=DisconnectError("disconnected"),
            )
        del self
               