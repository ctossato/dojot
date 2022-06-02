#!/bin/bash

readonly DEBUG_MODE=${DEBUG_MODE:-"0"}

# Dojot parameters
readonly DOJOT_GATEWAY_TIMEOUT=${DOJOT_GATEWAY_TIMEOUT:-"180"}
readonly DOJOT_PASSWD=${DOJOT_PASSWD:-"admin"}
readonly DOJOT_URL=${DOJOT_URL:-"http://127.0.0.1:8000"}
readonly DOJOT_USER=${DOJOT_USER:-"admin"}

# MQTT parameters
readonly DOJOT_MQTT_HOST=${DOJOT_MQTT_HOST:-"127.0.0.1"}
readonly DOJOT_MQTT_PORT=${DOJOT_MQTT_PORT:-"1883"}

# HTTP parameters
readonly DOJOT_HTTP_URL=${DOJOT_HTTP_URL:-"https://127.0.0.1"}
readonly DOJOT_HTTP_HOST=$(echo "$DOJOT_HTTP_URL" | sed -E 's/https?:\/\///g')
readonly DOJOT_HTTP_PORT=${DOJOT_HTTP_PORT:-"8080"}

# Redis parameters
readonly REDIS_CONN_TIMEOUT=${REDIS_CONN_TIMEOUT:-"180"}
readonly REDIS_HOST=${REDIS_HOST:-"redis"}
readonly REDIS_PORT=${REDIS_PORT:-"6379"}
readonly REDIS_PASSWD=${REDIS_PASSWD:-""}
# Databases
readonly REDIS_CERTIFICATES_DB=${REDIS_CERTIFICATES_DB:-"0"}
readonly REDIS_MAPPED_DB=${REDIS_MAPPED_DB:-"1"}

#Environment
readonly DOJOT_ENV=${DOJOT_ENV:-"n"}

#locust file
readonly LOCUST_FILE=${LOCUST_FILE:-"mqtt.py"}

if [ "${DEBUG_MODE}" == "1" ]
then
    set -ex
fi

START_TIME=$(date +'%s')
echo "Waiting for Redis fully start. Host '${REDIS_HOST}', '${REDIS_PORT}'..."
while [ "${PONG}" != "PONG" ]; do
    sleep 3
    echo "Ping Redis... "
    if [[ -z "$REDIS_PASSWD" ]] ;  then
        PONG=$(redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" ping | grep PONG)
    else
        PONG=$(redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" -a "${REDIS_PASSWD}" ping | grep PONG)
    fi

    ELAPSED_TIME=$(($(date +'%s') - ${START_TIME}))
    if [ "${ELAPSED_TIME}" -gt "${REDIS_CONN_TIMEOUT}" ]
    then
        echo "Redis is taking too long to fully start. Exiting!"
        exit 1
    fi
done
echo "Redis at host '${REDIS_HOST}', port '${REDIS_PORT}' fully started."

if [ "${DOJOT_ENV}" == "y" ]
then
    # Waiting for dojot API Gateway for at most 3 minutes
    START_TIME=$(date +'%s')
    echo "Waiting for dojot API Gateway fully start. Host '${DOJOT_URL}'..."
    echo "Try to connect to dojot API Gateway... "
    RESPONSE=$(curl --fail -s "${DOJOT_URL}" || echo "")
    while [ -z "${RESPONSE}" ]; do
        sleep 3
        echo "Retry to connect to dojot API Gateway ... "
        RESPONSE=$(curl --fail -s "${DOJOT_URL}" || echo "")

        ELAPSED_TIME=$(($(date +'%s') - ${START_TIME}))
        if [ "${ELAPSED_TIME}" -gt "${DOJOT_GATEWAY_TIMEOUT}" ]
        then
            echo "dojot API Gateway is taking too long to fully start. Exiting!"
            exit 2
        fi
    done
    echo "dojot API Gatewat at '${DOJOT_URL}' fully started."
fi

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

if [ "${REDIS_BACKUP}" == "y" ]
then
    echo "Reading from backup."
    echo "SET device_count 0" | redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" -a "${REDIS_PASSWD}" -n ${REDIS_MAPPED_DB} &> /dev/null
    echo "SET devices_to_revoke 0" | redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" -a "${REDIS_PASSWD}" -n ${REDIS_MAPPED_DB} &> /dev/null
    echo "SET devices_to_renew 0" | redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" -a "${REDIS_PASSWD}" -n ${REDIS_MAPPED_DB} &> /dev/null
fi

# setting locust host parameter
if [ -z "${RESPONSE_HTTP}" ]
then
  HOST_PARAMETER="${DOJOT_MQTT_HOST}:${DOJOT_MQTT_PORT}"
else
  HOST_PARAMETER="${DOJOT_HTTP_URL}:${DOJOT_HTTP_PORT}"
fi

echo "Starting locust master node ..." &&
locust -f locust_files/"${LOCUST_FILE}" -H "${HOST_PARAMETER}" --master