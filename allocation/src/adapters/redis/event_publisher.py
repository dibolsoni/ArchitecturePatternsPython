import json
import logging
from dataclasses import asdict

import redis

import config
from domain.event import Event

r = redis.Redis(**config.REDIS.host_and_port())


def publish(channel, event: Event):
	logging.debug(f'REDIS publishing channel:{channel} event: {event}')
	r.publish(channel, json.dumps(asdict(event)))
