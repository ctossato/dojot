"""
Locust Load Test.
"""
import time
import uuid


from locust import User, task, between, events
from locust.runners import STATE_STOPPING, STATE_STOPPED

from src.utils import Utils
from src.config import CONFIG
from src.mqtt_locust.mqtt_client import MQTTClient
from src.common.redis_client import RedisClient

from addons.influxPage import influx_page


class MqttLocust(User):
    """Abstract Locust client using MQTT."""
    abstract = True

    def __init__(self, environment):
        super().__init__(environment)

        # Connects to Redis database that stores the device_id for each client
        cache = RedisClient()

        revoke = cache.has_to_revoke()
        should_revoke = False
        should_renew = False

        device_id = None
        # We need to differentiate the device IDs to be revogated/renewed from the other ones
        # The revogated/renewed ones will not be stored in Redis; instead, they will be created
        # at runtime
        if revoke:
            should_revoke = revoke["should_revoke"]
            device_id = revoke["device_id"]
        else:
            renew = cache.has_to_renew()

            if renew:
                should_renew = renew["should_renew"]
                device_id = renew["device_id"]
            else:
                device_id = cache.next_device_id()

        # UUID to identify the client run
        run_id = str(uuid.uuid4())

        self.client = MQTTClient(device_id, run_id, should_revoke, should_renew)
        self.client.connect()


class Client(MqttLocust):
    """The client that will run the tasks when hatched."""

    min = CONFIG['locust']['task_min_time']
    max = CONFIG['locust']['task_max_time']
    wait_time = between(min, max)

    @task
    def publish(self):
        """Publishes a message to MQTT broker."""
        if self.environment.runner.state != STATE_STOPPING or self.environment.runner.state != STATE_STOPPED:
            if self.client.is_connected:
                if Utils.should_execute(CONFIG['security']['probability_to_revoke'] / 100.0):
                    self.client.revoke_cert()

                if Utils.should_execute(CONFIG['security']['probability_to_renew'] / 100.0):
                    self.client.renew_cert()

                self.client.publish()

    def on_stop(self):
        """
        Treats the client when Locust test has stopped.
        """
        if len(self.client.pubmmap) != 0:
            time.sleep(10)
        self.client.disconnect()


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



