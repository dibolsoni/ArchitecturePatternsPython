from abc import ABC, abstractmethod
from adapters import AbstractRepository
from service_layer.message_bus import message_bus


class AbstractUnitOfWork(ABC):
	products: AbstractRepository

	def __enter__(self):
		return self

	def __exit__(self, *args):
		self.rollback()

	def commit(self):
		self._commit()
		self.publish_events()

	def publish_events(self):
		for product in self.products.seen:
			if product is not None and hasattr(product, 'events'):
				while product.events:
					event = product.events.pop(0)
					message_bus.handle(event)

	@abstractmethod
	def _commit(self):
		raise NotImplementedError

	@abstractmethod
	def rollback(self):
		raise NotImplementedError
