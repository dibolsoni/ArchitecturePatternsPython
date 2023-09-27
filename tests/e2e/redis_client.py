import json

import redis

import config

r = redis.Redis(**config.REDIS.host_and_port())


def subscription_to(channel):
	pubsub = r.pubsub()
	pubsub.subscribe(channel)
	confirmation = pubsub.get_message(timeout=3)
	assert confirmation['type'] == 'subscribe'
	return pubsub


def publish_message(channel, message):
	json_message = json.dumps(message)
	r.publish(channel, json_message)
