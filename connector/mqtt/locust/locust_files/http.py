"""
HTTP IOT agent locust file
"""
import time

from locust import HttpUser, task, between, events

from src.common.redis_client import RedisClient
from src.config import CONFIG
from src.utils import Utils

from addons.influxPage import influx_page


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
        payload_data = {"timestamp": start_time}
        self.client.post("/http-agent/v1/incoming-messages",
                         json={"data": payload_data})


@events.init.add_listener
def locust_init(environment, **kwargs):
    """
    Add influx page to get the difference between publish messages on locust and what is stored in influxdb
    """
    if environment.web_ui:
        # setting environment to blueprints
        environment.web_ui.app.config["environment"] = environment
        # register our new routes and extended UI with the Locust web UI
        environment.web_ui.app.register_blueprint(influx_page)
