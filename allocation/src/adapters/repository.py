import abc

from domain import Sku, Product


class AbstractRepository(abc.ABC):
	@abc.abstractmethod
	def add(self, product: Product):
		raise NotImplementedError

	@abc.abstractmethod
	def get(self, sku: Sku) -> Product:
		raise NotImplementedError
