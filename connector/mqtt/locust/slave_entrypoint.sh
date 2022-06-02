#!/bin/bash

readonly DEBUG_MODE=${DEBUG_MODE:-"0"}

# MQTT parameters
readonly DOJOT_MQTT_HOST=${DOJOT_MQTT_HOST:-"127.0.0.1"}
readonly DOJOT_MQTT_PORT=${DOJOT_MQTT_PORT:-"1883"}
readonly DOJOT_MQTT_TIMEOUT=${DOJOT_MQTT_TIMEOUT:-"60"}

# HTTP parameters
readonly DOJOT_HTTP_URL=${DOJOT_HTTP_URL:-"https://127.0.0.1"}
readonly DOJOT_HTTP_HOST=$(echo "$DOJOT_HTTP_URL" | sed -E 's/https?:\/\///g')
readonly DOJOT_HTTP_PORT=${DOJOT_HTTP_PORT:-"8080"}

# Locust parameters
readonly LOCUST_MASTER_HOST=${LOCUST_MASTER_HOST:-"locust-master"}

# Redis parameters
readonly REDIS_CONN_TIMEOUT=${REDIS_CONN_TIMEOUT:-"180"}
readonly REDIS_HOST=${REDIS_HOST:-"redis"}
readonly REDIS_PORT=${REDIS_PORT:-"6379"}
readonly REDIS_PASSWD=${REDIS_PASSWD:-""}

# Certificate directories
readonly CERT_DIR=${CERT_DIR:-"cert/"}
readonly RENEW_CERT_DIR=${RENEW_CERT_DIR:-"renew/"}
readonly REVOKE_CERT_DIR=${REVOKE_CERT_DIR:-"revoke/"}

if [ "${DEBUG_MODE}" == "1" ]
then
    set -ex
fi

# Removing renew and revoke cert directories
rm -rf "${CERT_DIR}${RENEW_CERT_DIR}"
rm -rf "${CERT_DIR}${REVOKE_CERT_DIR}"

# Recreating renew and revoke cert directories
mkdir -p "${CERT_DIR}${RENEW_CERT_DIR}"
mkdir -p "${CERT_DIR}${REVOKE_CERT_DIR}"

# Waiting for redis for at most 3 minutes
START_TIME=$(date +'%s')
echo "Waiting for Redis fully start. Host '${REDIS_HOST}', '${REDIS_PORT}'..."
echo "Try ping Redis... "
if [[ -z "$REDIS_PASSWD" ]] ;  then
    PONG=$(redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" ping | grep PONG)
else
    PONG=$(redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" -a "${REDIS_PASSWD}" ping | grep PONG)
fi
while [ -z "${PONG}" ]; do
    sleep 3
    echo "Retry Redis ping... "
    PONG=$(redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" -a "${REDIS_PASSWD}" ping | grep PONG)

    ELAPSED_TIME=$(($(date +'%s') - ${START_TIME}))
    if [ "${ELAPSED_TIME}" -gt "${REDIS_CONN_TIMEOUT}" ]
    then
        echo "Redis is taking too long to fully start. Exiting!"
        exit 1
    fi
done
echo "Redis at host '${REDIS_HOST}', port '${REDIS_PORT}' fully started."

# Waiting for dojot broker for at most 3 minutes
START_TIME=$(date +'%s')
echo "Waiting for dojot Broker fully start. Host '${DOJOT_MQTT_HOST}', '${DOJOT_MQTT_PORT}' or host '${DOJOT_HTTP_HOST}', '${DOJOT_HTTP_PORT}'..."
echo "Try to connect to dojot Broker ... "
RESPONSE_MQTT=$(nc -zvv "${DOJOT_MQTT_HOST}" "${DOJOT_MQTT_PORT}" 2>&1 | grep succeeded || echo "")
RESPONSE_HTTP=$(nc -zvv "${DOJOT_HTTP_HOST}" "${DOJOT_HTTP_PORT}" 2>&1 | grep succeeded || echo "")
while [ -z "${RESPONSE_MQTT}" ] && [ -z "${RESPONSE_HTTP}" ]; do
    sleep 3
    echo "Retry to connect to dojot broker ... "
    RESPONSE_MQTT=$(nc -zvv "${DOJOT_MQTT_HOST}" "${DOJOT_MQTT_PORT}" 2>&1 | grep succeeded || echo "")
    RESPONSE_HTTP=$(nc -zvv "${DOJOT_HTTP_HOST}" "${DOJOT_HTTP_PORT}" 2>&1 | grep succeeded || echo "")

    ELAPSED_TIME=$(($(date +'%s') - ${START_TIME}))
    if [ ${ELAPSED_TIME} -gt 180 ]
    then
        echo "dojot MQTT broker is taking too long to fully start. Exiting!"
        exit 3
    fi
done

echo -en "dojot broker fully started at: "
if [ -n "${RESPONSE_MQTT}" ]; then echo -n "host ${DOJOT_MQTT_HOST}", port "${DOJOT_MQTT_PORT}";fi
if [ -n "${RESPONSE_MQTT}" ] && [ -n "${RESPONSE_HTTP}" ]; then echo -n " and ";fi
if [ -n "${RESPONSE_HTTP}" ]; then echo -n "host ${DOJOT_HTTP_HOST}", port "${DOJOT_HTTP_PORT}";fi
echo -e .

echo "Starting locust slave node ..."
locust -f locust_files/"${LOCUST_FILE}" --worker --master-host="${LOCUST_MASTER_HOST}"
