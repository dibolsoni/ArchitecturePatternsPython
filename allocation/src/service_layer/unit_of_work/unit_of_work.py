from abc import ABC, abstractmethod

from adapters import AbstractRepository


class AbstractUnitOfWork(ABC):
	products: AbstractRepository

	def __enter__(self):
		return self

	def __exit__(self, *args):
		self.rollback()

	@abstractmethod
	def commit(self):
		raise NotImplementedError

	@abstractmethod
	def rollback(self):
		raise NotImplementedError
