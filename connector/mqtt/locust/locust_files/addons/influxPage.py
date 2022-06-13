import json
import logging
import os
from itertools import chain
import requests

from locust import events, stats
from flask import Blueprint, jsonify, current_app

from src.config import CONFIG


influx_page = Blueprint(
            "influx_page",
            __name__
        )


@influx_page.route("/influx")
def influx_web():
    environment = current_app.config["environment"]
    test_start_time = int(environment.stats.total.start_time)
    report = {"test_start_time": environment.stats.total.start_time}

    publish_requests = 0
    influx_points = 0
    difference = None

    for s in chain(stats.sort_stats(environment.runner.stats.entries), [environment.runner.stats.total]):
        if s.name == 'publish' or s.name == '/http-agent/v1/incoming-messages':
            publish_requests = s.num_requests

    try:
        influx_points = int(get_influx_stat(test_start_time))
        difference = publish_requests - influx_points
    except (TimeoutError, IndexError):
        logging.error('Error getting influx data')
        influx_points = 'ERROR'

    report['locust_publish_requests'] = publish_requests
    report['influx_points'] = influx_points
    report['difference'] = difference
    return jsonify(report)


def get_influx_stat(start_time):
    """
    Get influx statistics via influx http API
    """
    url = f"http://{CONFIG['influxdb']['host']}:{CONFIG['influxdb']['port']}/api/v2/query"
    parameters = {'org': CONFIG['influxdb']['org']}
    headers = {'Content-Type': 'application/json', 'Authorization': f"Token {CONFIG['influxdb']['token']}"}
    body = {
        "query": f"from(bucket: \"devices\")"
                 f"    |> range(start: {start_time})"
                 f"    |> group()"
                 f"    |> count(column: \"_value\")",
        "type": "flux"
    }
    try:
        response = requests.post(url, params=parameters, headers=headers, data=json.dumps(body))
        logging.debug("influx status code %d - body response: %s", response.status_code, response.text)
        num_publication = response.text.splitlines()[1].split(',')[5]
    except IndexError:
        logging.error("Parse error: cannot get measurement number.")
        raise
    except TimeoutError:
        logging.error("Influx is not reachable.")
        raise
    return num_publication
