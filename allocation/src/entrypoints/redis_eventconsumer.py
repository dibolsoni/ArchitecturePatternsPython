import json
import logging

import redis

import config
from adapters.sql_alchemy_repository import orm
from domain.command import ChangeBatchQuantity
from service_layer import MessageBus, SqlAlchemyUnitOfWork

r = redis.Redis(**config.REDIS.host_and_port())


def main():
	orm.start_mappers()
	pubsub = r.pubsub()
	pubsub.subscribe("change_batch_quantity")

	for m in pubsub.listen():
		if m['data'] is not None and m['data'] != 1:
			handle_change_batch_quantity(m)


def handle_change_batch_quantity(message):
	logging.debug(f'REDIS handling {message}')
	data = json.loads(message['data'])
	cmd = ChangeBatchQuantity(reference=data['reference'], quantity=data['quantity'])
	MessageBus.handle(message=cmd, uow=SqlAlchemyUnitOfWork())


if __name__ == "__main__":
	main()
