from typing import Protocol, Set

from domain import Sku, Product


class AbstractRepository(Protocol):
	def add(self, product: Product):
		...

	def get(self, sku: Sku) -> Product:
		...


class TrackingRepository:
	seen: Set[Product]

	def __init__(self, repo: AbstractRepository):
		self.seen: Set[Product] = set()
		self._repo = repo

	def add(self, product: Product):
		self._repo.add(product)
		self.seen.add(product)

	def get(self, sku: Sku) -> Product:
		product = self._repo.get(sku=sku)
		self.seen.add(product)
		return product
