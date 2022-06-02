"""
HTTP IOT agent locust file
"""
import time

from locust import HttpUser, task, between

from src.common.redis_client import RedisClient
from src.config import CONFIG
from src.utils import Utils


class HttpIotUser(HttpUser):
    """
    Main locust user
    """

    min = CONFIG['locust']['task_min_time']
    max = CONFIG['locust']['task_max_time']
    wait_time = between(min, max)

    def on_start(self):
        cache = RedisClient()

        device_id = cache.next_device_id()
        client_cert_path = CONFIG['security']['cert_dir'] + device_id + ".crt"
        client_key_path = CONFIG['security']['cert_dir'] + device_id + ".key"

        self.client.cert = (client_cert_path, client_key_path)

        # If you want to disable SSL Certificate verification on client side, set the verify parameter to False
        self.client.verify = CONFIG['security']['cert_dir'] + "ca.crt"

    @task
    def publish(self):
        start_time = Utils.seconds_to_milliseconds(time.time())
        data_payload = {"timestamp": start_time}
        self.client.post("/http-agent/v1/incoming-messages",
                         json={"data": data_payload})
