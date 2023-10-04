import json
import logging

import redis

import config
from adapters.repository import orm
from bootstrap import bootstrap
from domain.command import ChangeBatchQuantity
from service_layer.unit_of_work import SqlAlchemyUnitOfWork
from service_layer.message_bus import MessageBus

r = redis.Redis(**config.REDIS.host_and_port())


def main():
	pubsub = r.pubsub()
	pubsub.subscribe("change_batch_quantity")
	bus = bootstrap()

	for m in pubsub.listen():
		if m['data'] is not None and m['data'] != 1:
			handle_change_batch_quantity(m, bus)


def handle_change_batch_quantity(message: str, bus: MessageBus):
	logging.debug(f'REDIS handling {message}')
	data = json.loads(message['data'])
	cmd = ChangeBatchQuantity(reference=data['reference'], quantity=data['quantity'])
	bus.handle(message=cmd)


if __name__ == "__main__":
	main()
