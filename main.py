# -*- coding: utf-8 -*-
import logging
from locust import Locust
from iot_device import IotDevice

class User(Locust):
    logging.info("Initializing user...")
    task_set = IotDevice
    min_wait = 10000
    max_wait = 15000
    
