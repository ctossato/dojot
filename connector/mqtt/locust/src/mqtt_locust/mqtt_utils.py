"""
MQTT Utils functions.
"""
import paho.mqtt.client as mqtt


MQTT_CONACK_ERRORS = {
    mqtt.CONNACK_ACCEPTED: "CONNACK_ACCEPTED",
    mqtt.CONNACK_REFUSED_PROTOCOL_VERSION: "CONNACK_REFUSED_PROTOCOL_VERSION",
    mqtt.CONNACK_REFUSED_IDENTIFIER_REJECTED: "CONNACK_REFUSED_IDENTIFIER_REJECTED",
    mqtt.CONNACK_REFUSED_SERVER_UNAVAILABLE: "CONNACK_REFUSED_SERVER_UNAVAILABLE",
    mqtt.CONNACK_REFUSED_BAD_USERNAME_PASSWORD: "CONNACK_REFUSED_BAD_USERNAME_PASSWORD",
    mqtt.CONNACK_REFUSED_NOT_AUTHORIZED: "CONNACK_REFUSED_NOT_AUTHORIZED",
}

MQTT_ERRORS = {
    mqtt.MQTT_ERR_AGAIN: "MQTT_ERR_AGAIN",
    mqtt.MQTT_ERR_SUCCESS: "MQTT_ERR_SUCCESS",
    mqtt.MQTT_ERR_NOMEM: "MQTT_ERR_NOMEM",
    mqtt.MQTT_ERR_PROTOCOL: "MQTT_ERR_PROTOCOL",
    mqtt.MQTT_ERR_INVAL: "MQTT_ERR_INVAL",
    mqtt.MQTT_ERR_NO_CONN: "MQTT_ERR_NO_CONN",
    mqtt.MQTT_ERR_CONN_REFUSED: "MQTT_ERR_CONN_REFUSED",
    mqtt.MQTT_ERR_NOT_FOUND: "MQTT_ERR_NOT_FOUND",
    mqtt.MQTT_ERR_CONN_LOST: "MQTT_ERR_CONN_LOST",
    mqtt.MQTT_ERR_TLS: "MQTT_ERR_TLS",
    mqtt.MQTT_ERR_PAYLOAD_SIZE: "MQTT_ERR_PAYLOAD_SIZE",
    mqtt.MQTT_ERR_NOT_SUPPORTED: "MQTT_ERR_NOT_SUPPORTED",
    mqtt.MQTT_ERR_AUTH: "MQTT_ERR_AUTH",
    mqtt.MQTT_ERR_ACL_DENIED: "MQTT_ERR_ACL_DENIED",
    mqtt.MQTT_ERR_UNKNOWN: "MQTT_ERR_UNKNOWN",
    mqtt.MQTT_ERR_ERRNO: "MQTT_ERR_ERRNO",
    mqtt.MQTT_ERR_QUEUE_SIZE: "MQTT_ERR_QUEUE_SIZE",
}


class MqttUtils:
    """MQTT Utils class."""

    @staticmethod
    def conack_error_message(error: int) -> str:
        """Converts the error code from Locust in an understandable string."""

        if MQTT_CONACK_ERRORS.get(error):
            return MQTT_CONACK_ERRORS[error]

        return "{}\n".format(error)

    @staticmethod
    def error_message(error: int) -> str:
        """Converts the error code from Locust in an understandable string."""

        if MQTT_ERRORS.get(error):
            return MQTT_ERRORS[error]

        return "{}\n".format(error)
