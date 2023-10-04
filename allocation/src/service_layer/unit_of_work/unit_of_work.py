from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from adapters.repository import TrackingRepository
from domain.event import Event


class AbstractUnitOfWork(ABC):
	products: TrackingRepository
	session: Session

	def __enter__(self):
		return self

	def __exit__(self, *args):
		self.rollback()

	def commit(self):
		self._commit()

	def collect_new_events(self) -> list[Event]:
		for product in self.products.seen:
			while product.events:
				yield product.events.pop(0)

	@abstractmethod
	def _commit(self):
		raise NotImplementedError

	@abstractmethod
	def rollback(self):
		raise NotImplementedError
