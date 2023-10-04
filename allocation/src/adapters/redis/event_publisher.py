import json
import logging
from dataclasses import asdict

import redis

import config
from domain.event import Event


class EventPublisher:
	def __init__(self):
		self.redis = redis.Redis(**config.REDIS.host_and_port())

	def publish(self, channel: str, event: Event):
		logging.debug(f'REDIS publishing channel:{channel} event: {event}')
		self.redis.publish(channel, json.dumps(asdict(event)))
