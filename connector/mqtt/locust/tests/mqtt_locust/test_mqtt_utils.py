"""
  Contains test for MQTT Utils class
"""
import unittest
import paho.mqtt.client as mqtt

from src.mqtt_locust.mqtt_utils import MqttUtils


class TestMqttUtils(unittest.TestCase):
    """
      Test MQTT Utils Testcase
    """
    def test_error_message(self):
        """
        error_message() should return the correct names for errors.
        """
        self.assertEqual(MqttUtils.error_message(
            mqtt.MQTT_ERR_AGAIN), "MQTT_ERR_AGAIN")
        self.assertEqual(MqttUtils.error_message(
            mqtt.MQTT_ERR_SUCCESS), "MQTT_ERR_SUCCESS")
        self.assertEqual(MqttUtils.error_message(
            mqtt.MQTT_ERR_NOMEM), "MQTT_ERR_NOMEM")
        self.assertEqual(MqttUtils.error_message(
            mqtt.MQTT_ERR_PROTOCOL), "MQTT_ERR_PROTOCOL")
        self.assertEqual(MqttUtils.error_message(
            mqtt.MQTT_ERR_INVAL), "MQTT_ERR_INVAL")
        self.assertEqual(MqttUtils.error_message(
            mqtt.MQTT_ERR_NO_CONN), "MQTT_ERR_NO_CONN")
        self.assertEqual(MqttUtils.error_message(
            mqtt.MQTT_ERR_CONN_REFUSED), "MQTT_ERR_CONN_REFUSED")
        self.assertEqual(MqttUtils.error_message(
            mqtt.MQTT_ERR_NOT_FOUND), "MQTT_ERR_NOT_FOUND")
        self.assertEqual(MqttUtils.error_message(
            mqtt.MQTT_ERR_CONN_LOST), "MQTT_ERR_CONN_LOST")
        self.assertEqual(MqttUtils.error_message(
            mqtt.MQTT_ERR_TLS), "MQTT_ERR_TLS")
        self.assertEqual(MqttUtils.error_message(
            mqtt.MQTT_ERR_PAYLOAD_SIZE), "MQTT_ERR_PAYLOAD_SIZE")
        self.assertEqual(MqttUtils.error_message(
            mqtt.MQTT_ERR_NOT_SUPPORTED), "MQTT_ERR_NOT_SUPPORTED")
        self.assertEqual(MqttUtils.error_message(
            mqtt.MQTT_ERR_AUTH), "MQTT_ERR_AUTH")
        self.assertEqual(MqttUtils.error_message(
            mqtt.MQTT_ERR_ACL_DENIED), "MQTT_ERR_ACL_DENIED")
        self.assertEqual(MqttUtils.error_message(
            mqtt.MQTT_ERR_UNKNOWN), "MQTT_ERR_UNKNOWN")
        self.assertEqual(MqttUtils.error_message(
            mqtt.MQTT_ERR_ERRNO), "MQTT_ERR_ERRNO")
        self.assertEqual(MqttUtils.error_message(
            mqtt.MQTT_ERR_QUEUE_SIZE), "MQTT_ERR_QUEUE_SIZE")
        self.assertEqual(MqttUtils.error_message(
            101010), "101010\n")

    def test_conack_error_message(self):
        """
        conack_error_message() should return the correct names for errors.
        """
        self.assertEqual(MqttUtils.conack_error_message(
            mqtt.CONNACK_ACCEPTED), "CONNACK_ACCEPTED")
        self.assertEqual(MqttUtils.conack_error_message(
            mqtt.CONNACK_REFUSED_PROTOCOL_VERSION), "CONNACK_REFUSED_PROTOCOL_VERSION")
        self.assertEqual(MqttUtils.conack_error_message(
            mqtt.CONNACK_REFUSED_IDENTIFIER_REJECTED), "CONNACK_REFUSED_IDENTIFIER_REJECTED")
        self.assertEqual(MqttUtils.conack_error_message(
            mqtt.CONNACK_REFUSED_SERVER_UNAVAILABLE), "CONNACK_REFUSED_SERVER_UNAVAILABLE")
        self.assertEqual(MqttUtils.conack_error_message(
            mqtt.CONNACK_REFUSED_BAD_USERNAME_PASSWORD), "CONNACK_REFUSED_BAD_USERNAME_PASSWORD")
        self.assertEqual(MqttUtils.conack_error_message(
            mqtt.CONNACK_REFUSED_NOT_AUTHORIZED), "CONNACK_REFUSED_NOT_AUTHORIZED")
        self.assertEqual(MqttUtils.conack_error_message(
            101010), "101010\n")


if __name__ == "__main__":
    unittest.main()
